package com.ecobridge.utils;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/**
 * HashUtils
 * Cryptographic utility for calculating SHA-256 digests for photo integrity
 * and generating deterministic audit hashes for handover records.
 */
public class HashUtils {

    /**
     * Calculates the SHA-256 hash of a file on disk.
     */
    public static String calculateFileSha256(File file) {
        if (file == null || !file.exists()) {
            return "";
        }
        try (InputStream is = new FileInputStream(file)) {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] buffer = new byte[8192];
            int read;
            while ((read = is.read(buffer)) > 0) {
                digest.update(buffer, 0, read);
            }
            byte[] md5sum = digest.digest();
            return bytesToHex(md5sum);
        } catch (Exception e) {
            return "";
        }
    }

    /**
     * Calculates the SHA-256 hash of a string.
     */
    public static String calculateStringSha256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hash);
        } catch (Exception e) {
            return "";
        }
    }

    /**
     * Generates a deterministic tamper-evident record hash for a handover transaction.
     */
    public static String generateHandoverHash(String lotId, String recyclerId,
                                              double weight, double amount,
                                              String paymentMode, String timestamp) {
        String raw = String.format(
                "LOT:%s|REC:%s|WT:%.2f|AMT:%.2f|MODE:%s|TS:%s",
                lotId, recyclerId, weight, amount, paymentMode, timestamp
        );
        return calculateStringSha256(raw);
    }

    private static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }
}
