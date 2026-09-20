from time import sleep

from requests.exceptions import RequestException


def igdb_request_with_retry(request_func, endpoint, query, *, logger, retries=3):
    delay = 1
    for attempt in range(1, retries + 1):
        try:
            if attempt > 1:
                logger.write(f"IGDB request {endpoint} attempt {attempt}/{retries}...")
            return request_func(endpoint, query)
        except RequestException as exc:
            if attempt == retries:
                raise
            logger.write(
                f"IGDB request failed for {endpoint} (attempt {attempt}/{retries}): {exc}. "
                f"Backing off for {delay}s before retry {attempt + 1}/{retries}."
            )
            sleep(delay)
            delay *= 2
