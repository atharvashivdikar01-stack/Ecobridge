package com.ecobridge.audio;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.MediaPlayer;
import android.speech.tts.TextToSpeech;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

import com.ecobridge.EcoBridgeApplication;
import com.ecobridge.R;

import java.util.HashMap;
import java.util.Locale;
import java.util.Map;

/**
 * AudioPromptManager
 * Delivers vernacular voice guidance for low-literacy informal waste collectors.
 *
 * Architecture:
 * 1. Checks for real recorded voice (.ogg / .mp3) in res/raw/[lang]_[promptKey]
 * 2. If valid audio recording exists (>= 1KB), plays instantly via MediaPlayer.
 * 3. If recording is absent, falls back to Android Text-to-Speech (TTS) with:
 *    - Matching target locale (mr_IN, hi_IN, en_IN)
 *    - Shared singleton lifecycle across activities to eliminate binding lag
 *    - Pending prompt queue if called during engine startup
 *    - Localized vernacular string dictionary
 */
public class AudioPromptManager implements TextToSpeech.OnInitListener {

    private static final String TAG = "AudioPromptManager";

    // Standard prompt identifiers across all workflows
    public static final String PROMPT_HOME_GUIDE = "home_guide";
    public static final String PROMPT_TAKE_PHOTO = "take_photo";
    public static final String PROMPT_CLASSIFY_MATERIAL = "classify_material";
    public static final String PROMPT_HAZARD_BATTERY = "hazard_battery";
    public static final String PROMPT_HAZARD_CRT = "hazard_crt";
    public static final String PROMPT_HAZARD_PCB = "hazard_pcb";
    public static final String PROMPT_ENTER_WEIGHT = "enter_weight";
    public static final String PROMPT_CHECK_PRICE = "check_price";
    public static final String PROMPT_SELECT_RECYCLER = "select_recycler";
    public static final String PROMPT_LOT_CREATED = "lot_created";
    public static final String PROMPT_START_HANDOVER = "start_handover";
    public static final String PROMPT_HANDOVER_CONFIRMED = "handover_confirmed";

    private static volatile AudioPromptManager instance;

    private final Context context;
    private MediaPlayer mediaPlayer;
    private TextToSpeech textToSpeech;
    private boolean isTtsReady = false;
    private String pendingSpeechText = null;

    // Dictionary mapping prompt keys to default localized string resource IDs
    private static final Map<String, Integer> PROMPT_STRING_MAP = new HashMap<>();
    static {
        PROMPT_STRING_MAP.put(PROMPT_HOME_GUIDE, R.string.prompt_home_guide);
        PROMPT_STRING_MAP.put(PROMPT_TAKE_PHOTO, R.string.prompt_take_photo);
        PROMPT_STRING_MAP.put(PROMPT_CLASSIFY_MATERIAL, R.string.prompt_classify_material);
        PROMPT_STRING_MAP.put(PROMPT_HAZARD_BATTERY, R.string.hazard_battery_msg);
        PROMPT_STRING_MAP.put(PROMPT_HAZARD_CRT, R.string.hazard_crt_msg);
        PROMPT_STRING_MAP.put(PROMPT_HAZARD_PCB, R.string.hazard_pcb_msg);
        PROMPT_STRING_MAP.put(PROMPT_ENTER_WEIGHT, R.string.prompt_enter_weight);
        PROMPT_STRING_MAP.put(PROMPT_CHECK_PRICE, R.string.prompt_check_price);
        PROMPT_STRING_MAP.put(PROMPT_SELECT_RECYCLER, R.string.prompt_select_recycler);
        PROMPT_STRING_MAP.put(PROMPT_LOT_CREATED, R.string.prompt_lot_created);
        PROMPT_STRING_MAP.put(PROMPT_START_HANDOVER, R.string.prompt_start_handover);
        PROMPT_STRING_MAP.put(PROMPT_HANDOVER_CONFIRMED, R.string.prompt_handover_confirmed);
    }

    /**
     * Singleton accessor for shared TTS lifecycle across the app.
     */
    public static AudioPromptManager getInstance(@NonNull Context context) {
        if (instance == null) {
            synchronized (AudioPromptManager.class) {
                if (instance == null) {
                    instance = new AudioPromptManager(context.getApplicationContext());
                }
            }
        }
        return instance;
    }

    public AudioPromptManager(@NonNull Context context) {
        this.context = context.getApplicationContext();
        initTtsEngine();
    }

    private synchronized void initTtsEngine() {
        if (textToSpeech == null) {
            try {
                textToSpeech = new TextToSpeech(context, this);
            } catch (Exception e) {
                Log.e(TAG, "Failed instantiating TextToSpeech engine", e);
            }
        }
    }

    @Override
    public void onInit(int status) {
        if (status == TextToSpeech.SUCCESS) {
            isTtsReady = true;
            if (textToSpeech != null) {
                textToSpeech.setSpeechRate(0.95f); // Natural pacing for low-literacy collectors
                textToSpeech.setPitch(1.0f);
            }
            updateTtsLanguage();
            Log.i(TAG, "Android TextToSpeech engine initialized successfully.");

            // Flush pending prompt if one was requested before TTS bound
            if (pendingSpeechText != null) {
                String toSpeak = pendingSpeechText;
                pendingSpeechText = null;
                speakFallback(toSpeak);
            }
        } else {
            isTtsReady = false;
            Log.w(TAG, "Android TextToSpeech initialization failed with status: " + status);
        }
    }

    public synchronized void updateTtsLanguage() {
        if (!isTtsReady || textToSpeech == null) return;

        String lang = "mr";
        try {
            if (EcoBridgeApplication.getInstance() != null) {
                lang = EcoBridgeApplication.getInstance().getSavedLanguage();
            }
        } catch (Exception ignored) {}

        Locale targetLocale;
        if ("hi".equalsIgnoreCase(lang)) {
            targetLocale = new Locale("hi", "IN");
        } else if ("en".equalsIgnoreCase(lang)) {
            targetLocale = new Locale("en", "IN");
        } else {
            // Default: Marathi
            targetLocale = new Locale("mr", "IN");
        }

        try {
            int result = textToSpeech.setLanguage(targetLocale);
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                if ("mr".equalsIgnoreCase(lang)) {
                    // Fall back to Hindi TTS voice if Marathi speech pack is missing
                    Log.i(TAG, "Marathi TTS pack not found on device; falling back to Hindi Devanagari engine.");
                    textToSpeech.setLanguage(new Locale("hi", "IN"));
                } else if ("en".equalsIgnoreCase(lang)) {
                    textToSpeech.setLanguage(Locale.US);
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "Error applying locale to TTS engine", e);
        }
    }

    /**
     * Plays the audio prompt for the given action key.
     * Looks up default localized text automatically if fallbackText is not provided.
     */
    public void playPrompt(@NonNull String promptKey) {
        playPrompt(promptKey, (String) null);
    }

    /**
     * Plays the audio prompt with explicit localized fallback text.
     */
    public void playPrompt(@NonNull String promptKey, @Nullable String fallbackText) {
        stopPlayback();

        String lang = "mr";
        try {
            if (EcoBridgeApplication.getInstance() != null) {
                lang = EcoBridgeApplication.getInstance().getSavedLanguage();
            }
        } catch (Exception ignored) {}

        // Try language prefixes: "mr_take_photo", "marathi_take_photo", etc.
        String[] possibleNames = {
                lang + "_" + promptKey,
                (lang.equals("mr") ? "marathi_" : (lang.equals("hi") ? "hindi_" : "en_")) + promptKey
        };

        int validResId = 0;
        for (String resourceName : possibleNames) {
            int resId = context.getResources().getIdentifier(resourceName, "raw", context.getPackageName());
            if (resId != 0 && isValidAudioResource(resId)) {
                validResId = resId;
                break;
            }
        }

        // 1. If valid real voice audio exists, play via MediaPlayer
        if (validResId != 0) {
            try {
                mediaPlayer = MediaPlayer.create(context, validResId);
                if (mediaPlayer != null) {
                    mediaPlayer.setOnCompletionListener(mp -> {
                        try {
                            mp.release();
                        } catch (Exception ignored) {}
                        mediaPlayer = null;
                    });
                    mediaPlayer.start();
                    Log.i(TAG, "Playing real voice audio resource for: " + promptKey);
                    return;
                }
            } catch (Exception e) {
                Log.w(TAG, "Failed playing raw audio clip for: " + promptKey + ", falling back to TTS.", e);
            }
        }

        // 2. Resolve localized fallback text
        String textToSpeak = fallbackText;
        if (textToSpeak == null || textToSpeak.trim().isEmpty()) {
            Integer resId = PROMPT_STRING_MAP.get(promptKey);
            if (resId != null) {
                try {
                    textToSpeak = context.getString(resId);
                } catch (Exception ignored) {}
            }
        }

        if (textToSpeak != null && !textToSpeak.trim().isEmpty()) {
            speakFallback(textToSpeak.trim());
        }
    }

    /**
     * Checks if a raw resource has valid audio content (>= 1 KB),
     * avoiding crashes on empty or placeholder files.
     */
    private boolean isValidAudioResource(int resId) {
        try (AssetFileDescriptor afd = context.getResources().openRawResourceFd(resId)) {
            if (afd != null) {
                long length = afd.getLength();
                return length >= 1024; // Must be at least 1 KB to be a real audio clip
            }
        } catch (Exception ignored) {}
        return false;
    }

    private synchronized void speakFallback(String text) {
        if (!isTtsReady || textToSpeech == null) {
            // Queue pending text to speak as soon as TTS binds
            pendingSpeechText = text;
            initTtsEngine();
            return;
        }

        try {
            updateTtsLanguage();
            textToSpeech.speak(text, TextToSpeech.QUEUE_FLUSH, null, "EcoBridgePrompt");
            Log.i(TAG, "Spoken via Android TTS fallback: " + text);
        } catch (Exception e) {
            Log.e(TAG, "Error executing TTS speak", e);
        }
    }

    public synchronized void stopPlayback() {
        if (mediaPlayer != null) {
            try {
                if (mediaPlayer.isPlaying()) {
                    mediaPlayer.stop();
                }
                mediaPlayer.release();
            } catch (Exception ignored) {}
            mediaPlayer = null;
        }
        if (textToSpeech != null && isTtsReady) {
            try {
                textToSpeech.stop();
            } catch (Exception ignored) {}
        }
    }

    /**
     * Stop currently playing audio on Activity destroy, but keep TTS engine alive for the app.
     */
    public void release() {
        stopPlayback();
    }

    /**
     * Full shutdown on Application termination.
     */
    public synchronized void shutdown() {
        stopPlayback();
        if (textToSpeech != null) {
            try {
                textToSpeech.shutdown();
            } catch (Exception ignored) {}
            textToSpeech = null;
            isTtsReady = false;
        }
        instance = null;
    }
}
