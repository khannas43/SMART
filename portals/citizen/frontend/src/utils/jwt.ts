/**
 * Utility functions for JWT token handling
 */

/**
 * Decode JWT token to get payload
 * Note: This does NOT verify the token, it only decodes it
 */
export const decodeJWT = (token: string): any => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding JWT:', error);
    return null;
  }
};

/**
 * Get username (Aadhaar number) from JWT token
 */
export const getUsernameFromToken = (token: string | null): string | null => {
  if (!token) return null;
  const decoded = decodeJWT(token);
  return decoded?.sub || decoded?.username || null;
};

