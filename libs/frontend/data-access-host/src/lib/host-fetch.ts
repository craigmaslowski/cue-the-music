import { ApiError, apiFetch } from '@cue-the-music/data-access-collection';

/**
 * Fetch wrapper for host endpoints that attaches the X-Host-Token header.
 * On 403 responses, calls the provided deactivation callback to clear host mode.
 */
export async function hostFetch<T>(
  path: string,
  token: string | null,
  options?: RequestInit,
  onUnauthorized?: () => void,
): Promise<T> {
  const headers: Record<string, string> = {};
  if (token) {
    headers['X-Host-Token'] = token;
  }

  try {
    return await apiFetch<T>(path, {
      ...options,
      headers: {
        ...headers,
        ...options?.headers,
      },
    });
  } catch (error) {
    if (error instanceof ApiError && error.status === 403) {
      onUnauthorized?.();
    }
    throw error;
  }
}
