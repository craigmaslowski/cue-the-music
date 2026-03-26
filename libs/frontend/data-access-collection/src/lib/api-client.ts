const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  `http://${window.location.hostname}:8000`;

/** Shared fetch wrapper that points to the backend API. */
export async function apiFetch<T>(
  path: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const { headers: optionHeaders, ...rest } = options ?? {};
  const response = await fetch(url, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(optionHeaders instanceof Headers
        ? Object.fromEntries(optionHeaders.entries())
        : optionHeaders),
    },
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({
      detail: response.statusText,
    })) as { detail?: string };
    throw new ApiError(response.status, errorBody.detail ?? response.statusText);
  }

  // 204 No Content has no body — Safari throws on response.json() for empty bodies
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

/** Typed API error with HTTP status code. */
export class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}
