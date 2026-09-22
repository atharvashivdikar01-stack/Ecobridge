#!/bin/bash

# ECOBRIDGE Collector App - VS Code Setup Script

echo "🚀 Setting up ECOBRIDGE Collector App for VS Code..."

# Install Android SDK tools
echo "📦 Installing Android SDK tools..."
brew install --cask android-commandlinetools

# Accept licenses
echo "📋 Accepting Android SDK licenses..."
yes | sdkmanager --licenses 2>/dev/null || true

# Install required Android components
echo "🔧 Installing Android SDK components..."
sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"

# Create local.properties
echo "⚙️  Creating local.properties..."
echo "sdk.dir=$HOME/Library/Android/sdk" > local.properties

# Create VS Code settings
echo "📝 Creating VS Code settings..."
mkdir -p .vscode
cat > .vscode/settings.json <<EOF
{
    "java.configuration.runtimes": [
        {
            "name": "JavaSE-17",
            "path": "/opt/homebrew/opt/openjdk@25",
            "default": true
        }
    ],
    "android.sdk.path": "$HOME/Library/Android/sdk"
}
EOF

echo "✅ Setup complete! Now you can:"
echo "   1. Open VS Code: code ."
echo "   2. Build: gradle assembleDebug"
echo "   3. Install: gradle installDebug"
echo "   4. Or use Android Studio for full debugging support"