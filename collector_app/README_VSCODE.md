# ECOBRIDGE Collector App - VS Code Setup

## 🚀 Quick Start with VS Code

### Option 1: Automated Setup
```bash
cd collector_app
./setup-vscode.sh
```

### Option 2: Manual Setup

#### 1. Install Android SDK
```bash
brew install --cask android-commandlinetools
yes | sdkmanager --licenses
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
```

#### 2. Open in VS Code
```bash
code collector_app
```

#### 3. Build from VS Code Terminal
Open the integrated terminal (Ctrl+`) and run:
```bash
gradle assembleDebug
```

#### 4. Install on Device/Emulator
```bash
gradle installDebug
```

## 📱 Running the App

### Method 1: VS Code Debugging
1. Open VS Code
2. Press F5 or go to Run and Debug
3. Select "Build Debug APK" configuration
4. Once built, run "Install Debug APK"

### Method 2: Terminal Commands
```bash
# Build the application
gradle assembleDebug

# Install on connected Android device
gradle installDebug

# Or run on emulator
gradle installDebug
```

### Method 3: Android Studio (Recommended for Full Debugging)
While VS Code is great for development, Android Studio provides:
- Full Android Emulator integration
- Visual layout editor
- Advanced debugging tools
- Performance profiling

## 🔧 VS Code Extensions (Optional)
Install these for better Android development experience:
- **Extension Pack for Java** (by Microsoft)
- **Android iOS Emulator** (for running emulators)
- **Gradle for Java** (for Gradle integration)

## 📋 Project Structure
```
collector_app/
├── app/
│   └── src/main/
│       ├── java/com/ecobridge/  # Java source code
│       ├── res/                  # Resources (layouts, strings, etc.)
│       └── assets/               # TFLite model files
├── .vscode/                      # VS Code configuration
├── gradle/                       # Gradle wrapper
└── local.properties              # Android SDK path
```

## 🎯 Build Variants
- `assembleDebug` - Debug build (faster, signed with debug key)
- `assembleRelease` - Release build (optimized, requires signing)
- `installDebug` - Install debug APK on connected device
- `installRelease` - Install release APK on connected device

## 🔍 Troubleshooting

### SDK Location Error
If you see "SDK location not found", ensure `local.properties` exists:
```bash
echo "sdk.dir=$HOME/Library/Android/sdk" > local.properties
```

### Java Version Error
Ensure Java 17+ is installed:
```bash
java -version
# Should show Java 17 or higher
```

### Device Not Found
Check if your device is connected:
```bash
adb devices
```

## 🎨 Application Features
The app includes:
- ✅ Offline-first operation
- ✅ CameraX photo capture with compression
- ✅ TFLite AI material classification
- ✅ Room database for local storage
- ✅ WorkManager background sync
- ✅ Multilingual support (Marathi, Hindi, English)
- ✅ Voice prompts with TTS fallback
- ✅ QR code generation
- ✅ Transaction ledger and earnings tracking

## 📞 Support
For issues or questions, refer to the main project documentation or check the Android logs in VS Code terminal.