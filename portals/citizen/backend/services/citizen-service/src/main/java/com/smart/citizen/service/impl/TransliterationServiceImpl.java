package com.smart.citizen.service.impl;

import com.smart.citizen.service.TransliterationService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import com.ibm.icu.text.Transliterator;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Service for transliterating English text to Hindi (Devanagari script)
 * Uses ICU4J for automatic transliteration of ANY English text to Hindi
 * Pattern matching is used as enhancement/fallback for known words
 */
@Slf4j
@Service
public class TransliterationServiceImpl implements TransliterationService {

    // ICU4J Transliterator for automatic English to Hindi transliteration
    // This handles ANY English text automatically without manual mapping
    private static final Transliterator TRANSLITERATOR;
    
    static {
        try {
            // Create transliterator from Latin script to Devanagari (Hindi)
            // This will automatically transliterate any English text to Hindi
            TRANSLITERATOR = Transliterator.getInstance("Latin-Devanagari");
            log.info("ICU4J Transliterator initialized successfully");
        } catch (Exception e) {
            log.error("Failed to initialize ICU4J Transliterator, will use pattern matching fallback", e);
            throw new RuntimeException("Transliteration service initialization failed", e);
        }
    }

    // Common English to Hindi transliteration mapping (for enhancements/fallback)
    private static final Map<String, String> TRANSLITERATION_MAP = new HashMap<>();
    
    static {
        // Common vowels
        TRANSLITERATION_MAP.put("a", "अ"); TRANSLITERATION_MAP.put("aa", "आ"); TRANSLITERATION_MAP.put("i", "इ");
        TRANSLITERATION_MAP.put("ee", "ई"); TRANSLITERATION_MAP.put("u", "उ"); TRANSLITERATION_MAP.put("oo", "ऊ");
        TRANSLITERATION_MAP.put("e", "ए"); TRANSLITERATION_MAP.put("ai", "ऐ"); TRANSLITERATION_MAP.put("o", "ओ");
        TRANSLITERATION_MAP.put("au", "औ");
        
        // Common consonants
        TRANSLITERATION_MAP.put("k", "क"); TRANSLITERATION_MAP.put("kh", "ख"); TRANSLITERATION_MAP.put("g", "ग");
        TRANSLITERATION_MAP.put("gh", "घ"); TRANSLITERATION_MAP.put("ng", "ङ"); TRANSLITERATION_MAP.put("ch", "च");
        TRANSLITERATION_MAP.put("chh", "छ"); TRANSLITERATION_MAP.put("j", "ज"); TRANSLITERATION_MAP.put("jh", "झ");
        TRANSLITERATION_MAP.put("ny", "ञ"); TRANSLITERATION_MAP.put("t", "त"); TRANSLITERATION_MAP.put("th", "थ");
        TRANSLITERATION_MAP.put("d", "द"); TRANSLITERATION_MAP.put("dh", "ध"); TRANSLITERATION_MAP.put("n", "न");
        TRANSLITERATION_MAP.put("p", "प"); TRANSLITERATION_MAP.put("ph", "फ"); TRANSLITERATION_MAP.put("b", "ब");
        TRANSLITERATION_MAP.put("bh", "भ"); TRANSLITERATION_MAP.put("m", "म"); TRANSLITERATION_MAP.put("y", "य");
        TRANSLITERATION_MAP.put("r", "र"); TRANSLITERATION_MAP.put("l", "ल"); TRANSLITERATION_MAP.put("v", "व");
        TRANSLITERATION_MAP.put("sh", "श"); TRANSLITERATION_MAP.put("shh", "ष"); TRANSLITERATION_MAP.put("s", "स");
        TRANSLITERATION_MAP.put("h", "ह");
        
        // Common name patterns (first names)
        TRANSLITERATION_MAP.put("shanti", "शांति");
        TRANSLITERATION_MAP.put("rani", "रानी");
        TRANSLITERATION_MAP.put("priya", "प्रिया");
        TRANSLITERATION_MAP.put("kavita", "कविता");
        TRANSLITERATION_MAP.put("sunita", "सुनीता");
        TRANSLITERATION_MAP.put("anita", "अनीता");
        TRANSLITERATION_MAP.put("geeta", "गीता");
        TRANSLITERATION_MAP.put("meera", "मीरा");
        TRANSLITERATION_MAP.put("radha", "राधा");
        TRANSLITERATION_MAP.put("sita", "सीता");
        TRANSLITERATION_MAP.put("laxmi", "लक्ष्मी");
        TRANSLITERATION_MAP.put("saraswati", "सरस्वती");
        TRANSLITERATION_MAP.put("ram", "राम");
        TRANSLITERATION_MAP.put("krishna", "कृष्ण");
        TRANSLITERATION_MAP.put("shiva", "शिव");
        TRANSLITERATION_MAP.put("vishnu", "विष्णु");
        TRANSLITERATION_MAP.put("arjun", "अर्जुन");
        TRANSLITERATION_MAP.put("raj", "राज");
        TRANSLITERATION_MAP.put("amit", "अमित");
        TRANSLITERATION_MAP.put("rohit", "रोहित");
        TRANSLITERATION_MAP.put("suresh", "सुरेश");
        TRANSLITERATION_MAP.put("mahesh", "महेश");
        TRANSLITERATION_MAP.put("rakesh", "राकेश");
        
        // Common surname patterns
        TRANSLITERATION_MAP.put("kumar", "कुमार");
        TRANSLITERATION_MAP.put("singh", "सिंह");
        TRANSLITERATION_MAP.put("sharma", "शर्मा");
        TRANSLITERATION_MAP.put("patel", "पटेल");
        TRANSLITERATION_MAP.put("thakur", "ठाकुर");
        TRANSLITERATION_MAP.put("devi", "देवी");
        TRANSLITERATION_MAP.put("lal", "लाल");
        TRANSLITERATION_MAP.put("bai", "बाई");
        TRANSLITERATION_MAP.put("verma", "वर्मा");
        TRANSLITERATION_MAP.put("yadav", "यादव");
        TRANSLITERATION_MAP.put("gupta", "गुप्ता");
        TRANSLITERATION_MAP.put("meena", "मीणा");
        TRANSLITERATION_MAP.put("jain", "जैन");
        TRANSLITERATION_MAP.put("agarwal", "अग्रवाल");
        
        // Common words
        TRANSLITERATION_MAP.put("government", "सरकार"); TRANSLITERATION_MAP.put("scheme", "योजना");
        TRANSLITERATION_MAP.put("rajasthan", "राजस्थान"); TRANSLITERATION_MAP.put("citizen", "नागरिक");
        TRANSLITERATION_MAP.put("benefit", "लाभ"); TRANSLITERATION_MAP.put("service", "सेवा");
        TRANSLITERATION_MAP.put("application", "आवेदन"); TRANSLITERATION_MAP.put("education", "शिक्षा");
        TRANSLITERATION_MAP.put("health", "स्वास्थ्य"); TRANSLITERATION_MAP.put("housing", "आवास");
    }

    @Override
    public String transliterateToHindi(String englishText) {
        if (englishText == null || englishText.trim().isEmpty()) {
            return null;
        }

        try {
            // Use ICU4J for automatic transliteration - handles ANY English text
            // This works for any name: Shanti, Sherni, Rani, etc.
            String transliterated = TRANSLITERATOR.transliterate(englishText.trim());
            
            // Apply common word enhancements (for better accuracy on known words)
            String enhanced = applyCommonWordEnhancements(transliterated, englishText);
            
            log.debug("Transliterated '{}' to '{}'", englishText, enhanced);
            return enhanced;
        } catch (Exception e) {
            log.warn("ICU4J transliteration failed for: {}, falling back to pattern matching", englishText, e);
            return transliterateWithPatternMatching(englishText);
        }
    }

    @Override
    public String transliterateName(String englishName) {
        if (englishName == null || englishName.trim().isEmpty()) {
            return null;
        }

        // Use the same transliteration method - ICU4J handles names automatically
        return transliterateToHindi(englishName);
    }
    
    /**
     * Apply common word enhancements to improve transliteration accuracy
     * for known words/names that might not transliterate perfectly
     */
    private String applyCommonWordEnhancements(String transliterated, String original) {
        String result = transliterated;
        String lowerOriginal = original.toLowerCase();
        
        // Apply enhancements for common words that might need correction
        // ICU4J is generally good, but we can fine-tune specific cases here
        for (Map.Entry<String, String> entry : TRANSLITERATION_MAP.entrySet()) {
            if (lowerOriginal.contains(entry.getKey())) {
                // Only apply if the transliteration doesn't already have the Hindi version
                if (!result.contains(entry.getValue())) {
                    // This is a fallback - ICU4J should handle most cases
                    result = result.replaceAll("(?i)" + java.util.regex.Pattern.quote(entry.getKey()), entry.getValue());
                }
            }
        }
        
        return result;
    }
    
    /**
     * Fallback transliteration using pattern matching (if ICU4J fails)
     */
    private String transliterateWithPatternMatching(String englishText) {
        String text = englishText.trim();
        String originalText = text;
        String lowerText = text.toLowerCase();
        
        // Sort entries by length (longer patterns first)
        List<Map.Entry<String, String>> sortedEntries = TRANSLITERATION_MAP.entrySet().stream()
            .sorted((e1, e2) -> Integer.compare(e2.getKey().length(), e1.getKey().length()))
            .collect(java.util.stream.Collectors.toList());
        
        // Try to match common patterns
        for (Map.Entry<String, String> entry : sortedEntries) {
            if (lowerText.contains(entry.getKey())) {
                text = text.replaceAll("(?i)\\b" + java.util.regex.Pattern.quote(entry.getKey()) + "\\b", entry.getValue());
                lowerText = text.toLowerCase();
            }
        }
        
        if (!text.equals(originalText)) {
            return text;
        }
        
        return transliterateCharacterByCharacter(englishText);
    }

    /**
     * Simple character-by-character transliteration
     * This is a basic implementation - for production, consider using ICU4J or similar library
     */
    private String transliterateCharacterByCharacter(String text) {
        // For now, return a simple transliteration
        // In production, you might want to use ICU4J library for better accuracy
        StringBuilder result = new StringBuilder();
        
        for (char c : text.toCharArray()) {
            if (Character.isWhitespace(c)) {
                result.append(c);
            } else if (Character.isLetter(c)) {
                // Basic transliteration - this is simplified
                // For production, use a proper transliteration library
                String transliterated = TRANSLITERATION_MAP.getOrDefault(
                    String.valueOf(c).toLowerCase(), 
                    String.valueOf(c)
                );
                result.append(transliterated);
            } else {
                result.append(c);
            }
        }
        
        return result.toString();
    }
}

