import functools
from time import sleep

import requests
from requests.exceptions import HTTPError, RequestException

# IGDBWrapper.api_request calls requests.post with no timeout, which could
# stall a long-running import forever. (connect, read) seconds.
DEFAULT_TIMEOUT = (5, 30)

# 429 (rate limited) and 5xx are transient; other 4xx are permanent client
# errors (bad query, auth, etc.) and must not be retried.
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

DEFAULT_MAX_BACKOFF = 30


def _ensure_request_timeout():
    """Patch the `post` IGDBWrapper uses so every request gets a timeout."""
    import igdb.wrapper as igdb_wrapper

    if getattr(igdb_wrapper.post, "_gamerhive_timeout_patched", False):
        return
    patched = functools.partial(requests.post, timeout=DEFAULT_TIMEOUT)
    patched._gamerhive_timeout_patched = True
    igdb_wrapper.post = patched


def _is_retryable(exc: RequestException) -> bool:
    if isinstance(exc, HTTPError):
        # No response means the error happened before a status was received
        # (rare); response present means we can inspect the status code.
        return (
            exc.response is None or exc.response.status_code in RETRYABLE_STATUS_CODES
        )
    # Connection errors / timeouts are transient by nature.
    return True


def _retry_after_seconds(exc: RequestException):
    response = getattr(exc, "response", None)
    if response is None:
        return None
    header = response.headers.get("Retry-After")
    if not header:
        return None
    try:
        return float(header)
    except ValueError:
        return None


def igdb_request_with_retry(
    request_func,
    endpoint,
    query,
    *,
    logger,
    retries=5,
    max_backoff=DEFAULT_MAX_BACKOFF,
):
    _ensure_request_timeout()
    delay = 1
    for attempt in range(1, retries + 1):
        try:
            if attempt > 1:
                logger.write(f"IGDB request {endpoint} attempt {attempt}/{retries}...")
            return request_func(endpoint, query)
        except RequestException as exc:
            status = getattr(getattr(exc, "response", None), "status_code", None)
            if not _is_retryable(exc):
                logger.write(
                    f"IGDB request for {endpoint} failed with non-retryable "
                    f"error (status={status}): {exc}."
                )
                raise
            if attempt == retries:
                logger.write(
                    f"IGDB request for {endpoint} failed after {retries} attempts "
                    f"(status={status}): {exc}."
                )
                raise
            wait = min(max(delay, _retry_after_seconds(exc) or 0), max_backoff)
            logger.write(
                f"IGDB request failed for {endpoint} (attempt {attempt}/{retries}, "
                f"status={status}): {exc}. Backing off for {wait}s before retry "
                f"{attempt + 1}/{retries}."
            )
            sleep(wait)
            delay = min(delay * 2, max_backoff)
