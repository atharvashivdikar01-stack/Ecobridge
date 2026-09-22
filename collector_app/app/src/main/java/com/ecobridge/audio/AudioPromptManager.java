package com.ecobridge.audio;

import android.content.Context;
import android.media.MediaPlayer;
import android.speech.tts.TextToSpeech;
import android.util.Log;

import com.ecobridge.EcoBridgeApplication;

import java.util.Locale;

/**
 * AudioPromptManager
 * Delivers vernacular voice guidance for low-literacy collectors.
 * Plays local audio resources from res/raw with automatic fallback
 * to Android Text-to-Speech without requiring active internet.
 */
public class AudioPromptManager implements TextToSpeech.OnInitListener {

    private static final String TAG = "AudioPromptManager";

    // Standard prompt identifiers
    public static final String PROMPT_TAKE_PHOTO = "take_photo";
    public static final String PROMPT_ENTER_WEIGHT = "enter_weight";
    public static final String PROMPT_LOT_CREATED = "lot_created";
    public static final String PROMPT_HANDOVER_CONFIRMED = "handover_confirmed";

    private final Context context;
    private MediaPlayer mediaPlayer;
    private TextToSpeech textToSpeech;
    private boolean isTtsReady = false;

    public AudioPromptManager(Context context) {
        this.context = context.getApplicationContext();
        this.textToSpeech = new TextToSpeech(this.context, this);
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            isTtsReady = true;
            updateTtsLanguage();
            Log.i(TAG, "Android TextToSpeech engine initialized.");
        } else {
            Log.w(TAG, "Android TextToSpeech initialization failed with status: " + status);
        }
    }

    public void updateTtsLanguage() {
        if (!isTtsReady || textToSpeech == null) return;
        String lang = EcoBridgeApplication.getInstance().getSavedLanguage();
        Locale targetLocale;
        if ("mr".equalsIgnoreCase(lang)) {
            targetLocale = new Locale("mr", "IN");
        } else if ("hi".equalsIgnoreCase(lang)) {
            targetLocale = new Locale("hi", "IN");
        } else {
            targetLocale = Locale.ENGLISH;
        }

        int result = textToSpeech.setLanguage(targetLocale);
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            // Fall back to Hindi or default Indian English if Marathi TTS voice data is missing on device
            textToSpeech.setLanguage(new Locale("hi", "IN"));
        }
    }

    /**
     * Plays the audio prompt for the given action key in the user's active language.
     */
    public void playPrompt(String promptKey, String fallbackText) {
        stopPlayback();

        String lang = EcoBridgeApplication.getInstance().getSavedLanguage();
        String resourceName = (lang.equals("mr") ? "marathi_" : (lang.equals("hi") ? "hindi_" : "en_")) + promptKey;
        int resId = context.getResources().getIdentifier(resourceName, "raw", context.getPackageName());

        if (resId != 0) {
            try {
                mediaPlayer = MediaPlayer.create(context, resId);
                if (mediaPlayer != null) {
                    mediaPlayer.setOnCompletionListener(mp -> {
                        mp.release();
                        mediaPlayer = null;
                    });
                    mediaPlayer.start();
                    Log.i(TAG, "Playing local audio resource: " + resourceName);
                    return;
                }
            } catch (Exception e) {
                Log.w(TAG, "Failed playing raw audio clip: " + resourceName + ", falling back to TTS.", e);
            }
        }

        // Fallback to Android Text-to-Speech
        speakFallback(fallbackText);
    }

    private void speakFallback(String text) {
        if (isTtsReady && textToSpeech != null && text != null && !text.isEmpty()) {
            updateTtsLanguage();
            textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, "EcoBridgePrompt");
            Log.i(TAG, "Spoken via Android TTS fallback: " + text);
        }
    }

    public void stopPlayback() {
        if (mediaPlayer != null) {
            try {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.stop();
                }
                mediaPlayer.release();
            } catch (Exception ignored) {}
            mediaPlayer = null;
        }
        if (textToSpeech != null) {
            textToSpeech.stop();
        }
    }

    public void release() {
        stopPlayback();
        if (textToSpeech != null) {
            textToSpeech.shutdown();
            textToSpeech = null;
        }
    }
}
