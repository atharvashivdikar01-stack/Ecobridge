package com.ecobridge.camera;

import android.content.Context;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.camera.core.Camera;
import androidx.camera.core.CameraSelector;
import androidx.camera.core.ImageCapture;
import androidx.camera.core.ImageCaptureException;
import androidx.camera.core.Preview;
import androidx.camera.lifecycle.ProcessCameraProvider;
import androidx.camera.view.PreviewView;
import androidx.core.content.ContextCompat;
import androidx.lifecycle.LifecycleOwner;

import com.google.common.util.concurrent.ListenableFuture;

import java.io.File;
import java.util.concurrent.ExecutionException;

/**
 * CameraManager
 * Manages CameraX lifecycle, surface binding, photo capture, and hardware flashlight.
 */
public class CameraManager {

    private static final String TAG = "CameraManager";

    private final Context context;
    private final LifecycleOwner lifecycleOwner;
    private final PreviewView previewView;

    private ProcessCameraProvider cameraProvider;
    private ImageCapture imageCapture;
    private Camera camera;
    private boolean isFlashOn = false;

    public interface OnCaptureCallback {
        void onImageCaptured(File capturedFile);
        void onError(Exception e);
    }

    public CameraManager(Context context, LifecycleOwner lifecycleOwner, PreviewView previewView) {
        this.context = context;
        this.lifecycleOwner = lifecycleOwner;
        this.previewView = previewView;
    }

    public void startCamera(Runnable onReady) {
        ListenableFuture<ProcessCameraProvider> cameraProviderFuture =
                ProcessCameraProvider.getInstance(context);

        cameraProviderFuture.addListener(() -> {
            try {
                cameraProvider = cameraProviderFuture.get();

                Preview preview = new Preview.Builder().build();
                preview.setSurfaceProvider(previewView.getSurfaceProvider());

                imageCapture = new ImageCapture.Builder()
                        .setCaptureMode(ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY)
                        .setFlashMode(ImageCapture.FLASH_MODE_AUTO)
                        .build();

                CameraSelector cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA;

                cameraProvider.unbindAll();
                camera = cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        cameraSelector,
                        preview,
                        imageCapture
                );

                if (onReady != null) {
                    onReady.run();
                }
                Log.i(TAG, "CameraX bound to lifecycle successfully.");
            } catch (ExecutionException | InterruptedException e) {
                Log.e(TAG, "Failed binding CameraX: " + e.getMessage(), e);
            }
        }, ContextCompat.getMainExecutor(context));
    }

    public void capturePhoto(final File destinationFile, final OnCaptureCallback callback) {
        if (imageCapture == null) {
            if (callback != null) {
                callback.onError(new IllegalStateException("Camera is not initialized"));
            }
            return;
        }

        ImageCapture.OutputFileOptions outputOptions =
                new ImageCapture.OutputFileOptions.Builder(destinationFile).build();

        imageCapture.takePicture(
                outputOptions,
                ContextCompat.getMainExecutor(context),
                new ImageCapture.OnImageSavedCallback() {
                    @Override
                    public void onImageSaved(@NonNull ImageCapture.OutputFileResults outputFileResults) {
                        Log.i(TAG, "Image successfully captured: " + destinationFile.getAbsolutePath());
                        if (callback != null) {
                            callback.onImageCaptured(destinationFile);
                        }
                    }

                    @Override
                    public void onError(@NonNull ImageCaptureException exception) {
                        Log.e(TAG, "Image capture failed: " + exception.getMessage(), exception);
                        if (callback != null) {
                            callback.onError(exception);
                        }
                    }
                }
        );
    }

    public boolean toggleFlash() {
        if (camera != null && camera.getCameraInfo().hasFlashUnit()) {
            isFlashOn = !isFlashOn;
            camera.getCameraControl().enableTorch(isFlashOn);
            return isFlashOn;
        }
        return false;
    }

    public void stopCamera() {
        if (cameraProvider != null) {
            cameraProvider.unbindAll();
        }
    }
}
