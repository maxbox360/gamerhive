type RegisterUserPayload = {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
};

type User = {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
};

const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const apiBaseUrl = apiUrl.replace(/\/$/, "");

async function readErrorMessage(response: Response, fallback: string): Promise<string> {
  try {
    const data = await response.json();
    if (typeof data?.detail === "string" && data.detail.trim()) {
      return data.detail;
    }
    if (typeof data?.message === "string" && data.message.trim()) {
      return data.message;
    }
  } catch {
    // Ignore parse errors and use fallback.
  }

  return fallback;
}

async function getCsrfToken(): Promise<string> {
  const response = await fetch(`${apiBaseUrl}/api/auth/csrf`, {
    method: "GET",
    credentials: "include",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Could not initialize secure session."));
  }

  const data = await response.json();
  if (typeof data?.csrfToken !== "string" || !data.csrfToken) {
    throw new Error("Could not initialize secure session.");
  }

  return data.csrfToken;
}

export async function registerUser(payload: RegisterUserPayload): Promise<User> {
  const csrfToken = await getCsrfToken();
  const response = await fetch(`${apiBaseUrl}/api/auth/register`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response, "Registration failed. Please try again."));
  }

  return response.json();
}
