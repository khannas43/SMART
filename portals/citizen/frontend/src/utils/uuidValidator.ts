/**
 * UUID validation utility
 */

/**
 * Validates if a string is a valid UUID (v4 format)
 * @param uuid - The string to validate
 * @returns true if the string is a valid UUID, false otherwise
 */
export const isValidUUID = (uuid: string): boolean => {
  if (!uuid || typeof uuid !== 'string') {
    return false;
  }
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
};

