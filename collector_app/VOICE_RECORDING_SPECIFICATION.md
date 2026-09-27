# EcoBridge Mobile — Real Voice Module & Recording Specification

This document provides the complete, authoritative guide for recording native human voice audio files (`.ogg`) for the EcoBridge Android Collector App (`collector_app`).

The app uses an **Audio-First Hybrid Architecture**:
1. When a collector arrives on a screen, the app checks `res/raw/` for the corresponding `.ogg` audio file in the collector's active language (`mr`, `hi`, `en`).
2. If the audio recording is present (file size $\ge$ 1 KB), the app plays the human voice recording via `MediaPlayer`.
3. If the audio recording is absent, the app automatically and transparently falls back to Android's on-device `TextToSpeech` (TTS) using the matching regional locale and optimized speech rate (0.95x).

---

## 1. File Storage Location & Naming Rules

All voice files **must** be placed in the Android resource directory:
```
collector_app/app/src/main/res/raw/
```

### Naming Conventions:
Android resource names **must only contain lowercase letters, numbers, and underscores** (`[a-z0-9_]`). No spaces, capital letters, or hyphens.

Format:
- Marathi: `mr_<prompt_key>.ogg` (or `marathi_<prompt_key>.ogg`)
- Hindi: `hi_<prompt_key>.ogg` (or `hindi_<prompt_key>.ogg`)
- English: `en_<prompt_key>.ogg`

Example:
- `res/raw/mr_take_photo.ogg`
- `res/raw/hi_take_photo.ogg`
- `res/raw/en_take_photo.ogg`

---

## 2. Audio Engineering & Recording Parameters

To guarantee instant playback on low-end Android smartphones without memory pressure or distortion:

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Container / Codec** | **OGG Vorbis (`.ogg`)** | Android native hardware decoding support |
| **Channels** | **Mono (1 Channel)** | Keeps file size small, centers audio in device speaker |
| **Sample Rate** | **44.1 kHz (44,100 Hz)** | Industry standard speech sampling |
| **Bit Depth** | **16-bit PCM** | Clean dynamic range |
| **Target Bitrate** | **64 kbps - 96 kbps** | Crisp voice quality with minimal storage (~15–30 KB per clip) |
| **Volume Normalization** | **-14 LUFS** (integrated) | Clear, audible speech in outdoor sunlight & noisy scrap yards |
| **Silence Padding** | **50ms lead-in, 100ms tail** | Prevents click/pop transients upon start & finish |
| **Voice Tone** | **Calm, respectful, instructional** | Friendly, dignified tone for informal scrap aggregators |

---

## 3. Complete Master Sentence List by Screen

### Screen 1: Dashboard / Home (`HomeActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `home_guide` | `en_home_guide.ogg` | English | *"Welcome to EcoBridge. Tap Weigh New Scrap to record lots, check prices, or find recyclers."* | Played when collector taps audio guide banner on home screen |
| `home_guide` | `hi_home_guide.ogg` | Hindi | **"इकोब्रिज में आपका स्वागत है। ई-कचरा रिकॉर्ड करने, भाव देखने या रीसाइक्लर खोजने के लिए नया स्क्रैप तौलें पर टैप करें।"** | Home dashboard overview prompt |
| `home_guide` | `mr_home_guide.ogg` | Marathi | **"इकोब्रिजमध्ये आपले स्वागत आहे. ई-कचरा नोंदवण्यासाठी, भाव पाहण्यासाठी किंवा रिसायकलर शोधण्यासाठी नवीन स्क्रॅप मोजा वर टॅप करा."** | Home dashboard overview prompt |

---

### Screen 2: Step 1 Camera Capture (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `take_photo` | `en_take_photo.ogg` | English | *"Point the camera at your scrap lot and take a clear photo."* | Played when camera preview opens in Step 1 |
| `take_photo` | `hi_take_photo.ogg` | Hindi | **"कैमरा कबाड़ की ओर रखें और एक स्पष्ट फोटो लें।"** | Instructions for photographing scrap |
| `take_photo` | `mr_take_photo.ogg` | Marathi | **"कॅमेरा भंगाराकडे धरा आणि एक स्पष्ट फोटो काढा."** | Instructions for photographing scrap |

---

### Screen 3: Step 2 AI Material Classification (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `classify_material` | `en_classify_material.ogg` | English | *"AI is analyzing the scrap material. Please verify the detected category."* | Played when photo is captured and inference runs |
| `classify_material` | `hi_classify_material.ogg` | Hindi | **"एआई सामग्री की पहचान कर रहा है। कृपया पहचानी गई श्रेणी की पुष्टि करें।"** | Verification prompt for detected scrap type |
| `classify_material` | `mr_classify_material.ogg` | Marathi | **"एआय भंगाराची तपासणी करत आहे. कृपया ओळखलेल्या प्रकाराची खात्री करा."** | Verification prompt for detected scrap type |

---

### Screen 4: Step 2 Hazard Warnings (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `hazard_battery` | `en_hazard_battery.ogg` | English | *"Warning! Hazardous battery detected. Do not puncture, crush, or expose to heat."* | Critical safety warning for swollen/damaged batteries |
| `hazard_battery` | `hi_hazard_battery.ogg` | Hindi | **"सावधान! खतरनाक बैटरी मिली है। इसे न काटें, न तोड़ें और न ही आग के पास ले जाएं।"** | Battery safety PPE alert |
| `hazard_battery` | `mr_hazard_battery.ogg` | Marathi | **"सावधान! धोकादायक बॅटरी आढळली आहे. याला कापू नका, तोडू नका किंवा आगीजवळ नेऊ नका."** | Battery safety PPE alert |
| `hazard_crt` | `en_hazard_crt.ogg` | English | *"Warning! Hazardous CRT glass detected. Wear protective gloves and do not break the tube."* | Lead exposure and vacuum implosion alert |
| `hazard_crt` | `hi_hazard_crt.ogg` | Hindi | **"सावधान! खतरनाक सीआरटी कांच मिली है। मोटे दस्ताने पहनें और ट्यूब न तोड़ें।"** | CRT glass safety alert |
| `hazard_crt` | `mr_hazard_crt.ogg` | Marathi | **"सावधान! धोकादायक सीआरटी काच आढळली आहे. जाड हातमोजे वापरा आणि काच फोडू नका."** | CRT glass safety alert |
| `hazard_pcb` | `en_hazard_pcb.ogg` | English | *"Warning! Contains lead solder. Avoid bare skin contact and do not inhale dust."* | Burnt PCB toxic residue alert |
| `hazard_pcb` | `hi_hazard_pcb.ogg` | Hindi | **"सावधान! सर्किट बोर्ड में लेड सोल्डर है। सीधे न छुएं और धूल या धुएं से बचें।"** | PCB safety alert |
| `hazard_pcb` | `mr_hazard_pcb.ogg` | Marathi | **"सावधान! सर्किट बोर्डमध्ये लेड सोल्डर आहे. थेट हात लावू नका आणि विषारी धुरापासून दूर राहा."** | PCB safety alert |

---

### Screen 5: Step 3 Weight Input (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `enter_weight` | `en_enter_weight.ogg` | English | *"Enter or adjust the gross weight of the scrap lot in kilograms."* | Step 3 keypad guidance |
| `enter_weight` | `hi_enter_weight.ogg` | Hindi | **"कबाड़ का कुल वजन किलोग्राम में दर्ज करें।"** | Step 3 keypad guidance |
| `enter_weight` | `mr_enter_weight.ogg` | Marathi | **"भंगाराचे एकूण वजन किलोग्रॅममध्ये टाका."** | Step 3 keypad guidance |

---

### Screen 6: Step 4 Fair Price Intelligence (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `check_price` | `en_check_price.ogg` | English | *"Review the benchmark market price and estimated total value for your lot."* | Step 4 market rate transparency |
| `check_price` | `hi_check_price.ogg` | Hindi | **"अपने कबाड़ का बाजार भाव और अनुमानित कुल मूल्य देखें।"** | Step 4 market rate transparency |
| `check_price` | `mr_check_price.ogg` | Marathi | **"आपल्या भंगाराचा बाजारभाव आणि अंदाजित एकूण मूल्य तपासा."** | Step 4 market rate transparency |

---

### Screen 7: Step 5 Recycler Matching (`NewLotActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `select_recycler` | `en_select_recycler.ogg` | English | *"Select a certified recycler near you to proceed with handover."* | Step 5 recycler directory selection |
| `select_recycler` | `hi_select_recycler.ogg` | Hindi | **"हैंडओवर के लिए अपने नजदीकी प्रमाणित रीसाइक्लर का चयन करें।"** | Step 5 recycler directory selection |
| `select_recycler` | `mr_select_recycler.ogg` | Marathi | **"हस्तांतरणासाठी जवळचा अधिकृत रिसायकलर निवडा."** | Step 5 recycler directory selection |

---

### Screen 8: Lot Creation Confirmation (`LotCreatedActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `lot_created` | `en_lot_created.ogg` | English | *"Scrap lot created successfully and saved offline on your device."* | Played upon QR token generation |
| `lot_created` | `hi_lot_created.ogg` | Hindi | **"स्क्रैप लॉट सफलतापूर्वक बन गया और आपके फोन में सुरक्षित सेव हो गया।"** | Played upon QR token generation |
| `lot_created` | `mr_lot_created.ogg` | Marathi | **"स्क्रॅप लॉट यशस्वीरीत्या तयार झाला आणि फोनमध्ये ऑफलाइन सेव्ह झाला."** | Played upon QR token generation |

---

### Screen 9: Handover & Settlement (`HandoverActivity`)

| Prompt Key | Target Filename | Language | Exact Phrase to Record | Description & Context |
| :--- | :--- | :--- | :--- | :--- |
| `start_handover` | `en_start_handover.ogg` | English | *"Enter the verified scale weight and confirm the payment amount."* | Played upon entering Handover screen |
| `start_handover` | `hi_start_handover.ogg` | Hindi | **"कांटे का वास्तविक वजन दर्ज करें और भुगतान राशि की पुष्टि करें।"** | Scale terminal verification prompt |
| `start_handover` | `mr_start_handover.ogg` | Marathi | **"काट्यावरील प्रत्यक्ष वजन नोंदवा आणि पेमेंट रकमेची खात्री करा."** | Scale terminal verification prompt |
| `handover_confirmed` | `en_handover_confirmed.ogg` | English | *"Handover recorded successfully. Please collect your cash payment."* | Played after submission with audit hash |
| `handover_confirmed` | `hi_handover_confirmed.ogg` | Hindi | **"हस्तांतरण सफलतापूर्वक दर्ज हुआ। कृपया अपनी नकद राशि प्राप्त करें।"** | Cash collection confirmation |
| `handover_confirmed` | `mr_handover_confirmed.ogg` | Marathi | **"हस्तांतरण यशस्वीरीत्या नोंदवले गेले. कृपया आपली रोख रक्कम स्वीकारा."** | Cash collection confirmation |

---

## 4. How the Android Audio Engine Handles Files

The code in `com.ecobridge.audio.AudioPromptManager`:

```java
// Automatic file resolution:
int resId = context.getResources().getIdentifier(lang + "_" + promptKey, "raw", context.getPackageName());

if (resId != 0 && isValidAudioResource(resId)) {
    // 1. Play human studio voice recording
    mediaPlayer = MediaPlayer.create(context, resId);
    mediaPlayer.start();
} else {
    // 2. Seamlessly falls back to Android Text-to-Speech
    // Uses pre-initialized single engine with 0.95x rate and matching regional voice
    speakFallback(localizedDictionaryText);
}
```

This guarantees that:
- You do **not** need to deploy all audio recordings at once; you can add them file-by-file.
- The app will **never crash** or lag if an audio file is missing or corrupted.
- Voice guidance remains 100% active for non-literate waste pickers under all circumstances.
