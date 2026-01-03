package com.smart.citizen.service;

/**
 * Service for transliterating English text to Hindi (Devanagari script)
 */
public interface TransliterationService {
    /**
     * Transliterate English text to Hindi
     * @param englishText The English text to transliterate
     * @return Hindi text in Devanagari script, or null if input is null/empty
     */
    String transliterateToHindi(String englishText);
    
    /**
     * Transliterate a name (handles common name patterns)
     * @param englishName The English name to transliterate
     * @return Hindi name in Devanagari script
     */
    String transliterateName(String englishName);
}

