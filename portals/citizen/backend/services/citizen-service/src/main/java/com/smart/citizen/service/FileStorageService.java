package com.smart.citizen.service;

import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Path;

public interface FileStorageService {
    /**
     * Store a file and return the file path
     */
    String storeFile(MultipartFile file, String subDirectory) throws IOException;

    /**
     * Load file as a resource
     */
    Path loadFileAsPath(String filePath);

    /**
     * Delete a file
     */
    boolean deleteFile(String filePath) throws IOException;

    /**
     * Get file content as bytes
     */
    byte[] loadFileAsBytes(String filePath) throws IOException;

    /**
     * Check if file exists
     */
    boolean fileExists(String filePath);

    /**
     * Calculate SHA-256 hash of file content
     */
    String calculateFileHash(byte[] fileContent);
}

