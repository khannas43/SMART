package com.smart.citizen.service.impl;

import com.smart.citizen.service.FileStorageService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.security.MessageDigest;
import java.util.UUID;

@Service
@Slf4j
public class FileStorageServiceImpl implements FileStorageService {

    private final Path fileStorageLocation;

    public FileStorageServiceImpl(@Value("${file.upload-dir:./uploads}") String uploadDir) {
        this.fileStorageLocation = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.fileStorageLocation);
            log.info("File storage directory initialized: {}", this.fileStorageLocation);
        } catch (IOException ex) {
            throw new RuntimeException("Could not create the directory where uploaded files will be stored.", ex);
        }
    }

    @Override
    public String storeFile(MultipartFile file, String subDirectory) throws IOException {
        // Validate file
        if (file.isEmpty()) {
            throw new IllegalArgumentException("File is empty");
        }

        // Generate unique filename
        String originalFilename = StringUtils.cleanPath(file.getOriginalFilename());
        if (originalFilename.contains("..")) {
            throw new IllegalArgumentException("Invalid file path: " + originalFilename);
        }

        String fileExtension = "";
        int lastDotIndex = originalFilename.lastIndexOf('.');
        if (lastDotIndex > 0) {
            fileExtension = originalFilename.substring(lastDotIndex);
        }

        String uniqueFilename = UUID.randomUUID().toString() + fileExtension;

        // Create subdirectory if specified
        Path targetDirectory = this.fileStorageLocation;
        if (subDirectory != null && !subDirectory.isEmpty()) {
            targetDirectory = this.fileStorageLocation.resolve(subDirectory);
            Files.createDirectories(targetDirectory);
        }

        // Copy file to target location
        Path targetLocation = targetDirectory.resolve(uniqueFilename);
        Files.copy(file.getInputStream(), targetLocation, StandardCopyOption.REPLACE_EXISTING);

        // Return relative path
        String relativePath = subDirectory != null && !subDirectory.isEmpty()
                ? subDirectory + "/" + uniqueFilename
                : uniqueFilename;

        log.info("File stored successfully: {}", relativePath);
        return relativePath;
    }

    @Override
    public Path loadFileAsPath(String filePath) {
        return this.fileStorageLocation.resolve(filePath).normalize();
    }

    @Override
    public boolean deleteFile(String filePath) throws IOException {
        Path file = loadFileAsPath(filePath);
        if (Files.exists(file)) {
            Files.delete(file);
            log.info("File deleted: {}", filePath);
            return true;
        }
        return false;
    }

    @Override
    public byte[] loadFileAsBytes(String filePath) throws IOException {
        Path file = loadFileAsPath(filePath);
        if (!Files.exists(file)) {
            throw new IOException("File not found: " + filePath);
        }
        return Files.readAllBytes(file);
    }

    @Override
    public boolean fileExists(String filePath) {
        Path file = loadFileAsPath(filePath);
        return Files.exists(file);
    }

    /**
     * Calculate SHA-256 hash of file content
     */
    public String calculateFileHash(byte[] fileContent) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(fileContent);
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (Exception e) {
            log.error("Error calculating file hash", e);
            return null;
        }
    }
}

