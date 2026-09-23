package com.ecobridge.utils;

import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Matrix;
import android.media.ExifInterface;
import android.util.Log;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;

/**
 * ImageUtils
 * Compresses scrap photos to approximately 150 KB JPEG, handling orientation,
 * memory optimization, and scaling down high-resolution camera captures.
 */
public class ImageUtils {

    private static final String TAG = "ImageUtils";
    public static final int TARGET_SIZE_BYTES = 150 * 1024; // ~150 KB target
    public static final int MAX_DIMENSION = 1024; // Max width/height in px

    /**
     * Compresses the source image file to approx 150 KB JPEG and saves to target file.
     */
    public static boolean compressToTargetJpeg(File sourceFile, File destFile) {
        try {
            if (!sourceFile.exists()) {
                Log.e(TAG, "Source file does not exist: " + sourceFile.getAbsolutePath());
                return false;
            }

            // Read image dimensions without full allocation
            BitmapFactory.Options boundsOptions = new BitmapFactory.Options();
            boundsOptions.inJustDecodeBounds = true;
            BitmapFactory.decodeFile(sourceFile.getAbsolutePath(), boundsOptions);

            int width = boundsOptions.outWidth;
            int height = boundsOptions.outHeight;

            // Calculate sample size
            int sampleSize = 1;
            while (width / sampleSize > MAX_DIMENSION || height / sampleSize > MAX_DIMENSION) {
                sampleSize *= 2;
            }

            BitmapFactory.Options decodeOptions = new BitmapFactory.Options();
            decodeOptions.inSampleSize = sampleSize;
            Bitmap bitmap = BitmapFactory.decodeFile(sourceFile.getAbsolutePath(), decodeOptions);
            if (bitmap == null) {
                return false;
            }

            // Fix rotation from EXIF
            bitmap = correctExifOrientation(sourceFile.getAbsolutePath(), bitmap);

            // Compress iteratively to target ~150 KB
            int quality = 85;
            ByteArrayOutputStream bos = new ByteArrayOutputStream();
            bitmap.compress(Bitmap.CompressFormat.JPEG, quality, bos);

            while (bos.size() > TARGET_SIZE_BYTES && quality > 20) {
                bos.reset();
                quality -= 10;
                bitmap.compress(Bitmap.CompressFormat.JPEG, quality, bos);
            }

            try (FileOutputStream fos = new FileOutputStream(destFile)) {
                fos.write(bos.toByteArray());
                fos.flush();
            }

            Log.i(TAG, "Compressed photo saved to " + destFile.getAbsolutePath() +
                    " (" + (destFile.length() / 1024) + " KB, quality=" + quality + ")");
            bitmap.recycle();
            return true;
        } catch (Exception e) {
            Log.e(TAG, "Failed to compress image: " + e.getMessage(), e);
            return false;
        }
    }

    private static Bitmap correctExifOrientation(String photoPath, Bitmap bitmap) {
        try {
            ExifInterface ei = new ExifInterface(photoPath);
            int orientation = ei.getAttributeInt(ExifInterface.TAG_ORIENTATION, ExifInterface.ORIENTATION_NORMAL);
            Matrix matrix = new Matrix();

            switch (orientation) {
                case ExifInterface.ORIENTATION_ROTATE_90:
                    matrix.postRotate(90);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_180:
                    matrix.postRotate(180);
                    break;
                case ExifInterface.ORIENTATION_ROTATE_270:
                    matrix.postRotate(270);
                    break;
                default:
                    return bitmap;
            }

            Bitmap rotated = Bitmap.createBitmap(bitmap, 0, 0, bitmap.getWidth(), bitmap.getHeight(), matrix, true);
            bitmap.recycle();
            return rotated;
        } catch (Exception e) {
            return bitmap;
        }
    }
}
