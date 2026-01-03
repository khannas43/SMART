/**
 * Utility functions for extracting user initials from names
 * Works with both English and Hindi (Devanagari) names
 */

/**
 * Check if a character is a Devanagari (Hindi) character
 */
function isDevanagari(char: string): boolean {
  // Devanagari Unicode range: U+0900 to U+097F
  const code = char.charCodeAt(0);
  return code >= 0x0900 && code <= 0x097F;
}

/**
 * Check if a string contains Devanagari characters
 */
function containsDevanagari(text: string): boolean {
  return Array.from(text).some(char => isDevanagari(char));
}

/**
 * Get the first character of a word (handles Devanagari properly)
 */
function getFirstCharacter(word: string): string {
  if (!word || word.trim().length === 0) return '';
  
  // For Devanagari, we need to handle combining characters
  // The first visible character might be followed by combining marks
  const trimmed = word.trim();
  
  // Check if it's Devanagari
  if (isDevanagari(trimmed[0])) {
    // For Devanagari, get the first character (which might include combining marks)
    // Simple approach: get first character, but check for common combining patterns
    let firstChar = trimmed[0];
    
    // Check if next character is a combining mark (vowel signs, etc.)
    if (trimmed.length > 1) {
      const secondChar = trimmed[1];
      // Devanagari combining marks are in range U+093A-U+093C, U+0941-U+0949, U+094D-U+094F, U+0951-U+0957
      const secondCode = secondChar.charCodeAt(0);
      if (
        (secondCode >= 0x093A && secondCode <= 0x093C) ||
        (secondCode >= 0x0941 && secondCode <= 0x0949) ||
        (secondCode >= 0x094D && secondCode <= 0x094F) ||
        (secondCode >= 0x0951 && secondCode <= 0x0957)
      ) {
        // Include the combining mark
        firstChar = trimmed.substring(0, 2);
      }
    }
    
    return firstChar;
  }
  
  // For Latin/English, just return first character
  return trimmed[0].toUpperCase();
}

/**
 * Get user initials from name (first letter of first name + first letter of last name)
 * Works with both English and Hindi names
 * 
 * Examples:
 * - "Rani Thakur" → "RT"
 * - "रानी ठाकुर" → "रठ" (first character of each word)
 * - "Shanti Thakur" → "ST"
 * - "शांति ठाकुर" → "शठ"
 * 
 * @param name - Full name (English or Hindi)
 * @returns Initials (2 characters) or single character if only one word
 */
export function getUserInitials(name: string | null | undefined): string {
  if (!name || name.trim().length === 0) {
    return 'U'; // Default fallback
  }

  const trimmed = name.trim();
  const words = trimmed.split(/\s+/).filter(word => word.length > 0);

  if (words.length === 0) {
    return 'U';
  }

  if (words.length === 1) {
    // Only one word - return first character
    return getFirstCharacter(words[0]);
  }

  // Multiple words - get first character of first and last word
  const firstWord = words[0];
  const lastWord = words[words.length - 1];
  
  const firstInitial = getFirstCharacter(firstWord);
  const lastInitial = getFirstCharacter(lastWord);

  return firstInitial + lastInitial;
}

/**
 * Get user initials based on current language preference
 * Uses Hindi name if available and language is Hindi, otherwise uses English name
 * 
 * @param user - User object with fullName and fullNameHindi
 * @param currentLanguage - Current i18n language code
 * @returns Initials based on language preference
 */
export function getUserInitialsLocalized(
  user: { fullName: string; fullNameHindi?: string } | null | undefined,
  currentLanguage: string
): string {
  if (!user) {
    return 'U';
  }

  // If language is Hindi and Hindi name exists, use Hindi name
  if (currentLanguage === 'hi' && user.fullNameHindi) {
    return getUserInitials(user.fullNameHindi);
  }

  // Otherwise use English name
  return getUserInitials(user.fullName);
}

