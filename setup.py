#!/usr/bin/env python3
"""
Discord Bot Setup Helper
This script helps you set up your Discord bot token.
"""

import os
from pathlib import Path

def setup_bot_token():
    print("🤖 Discord Bot Setup Helper")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found! Creating one for you...")
        with open('.env', 'w') as f:
            f.write("# Add your Discord bot token here\n")
            f.write("# Get it from: https://discord.com/developers/applications\n")
            f.write("DISCORD_BOT_TOKEN=your_discord_bot_token_here\n")
        print("✅ Created .env file")
    
    print("\n📋 To get your Discord Bot Token:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click 'New Application' and give it a name")
    print("3. Go to 'Bot' section and click 'Add Bot'")
    print("4. Under 'Token' section, click 'Copy' to copy your bot token")
    print("5. Replace 'your_discord_bot_token_here' in the .env file with your actual token")
    
    print("\n🔧 To invite your bot to a server:")
    print("1. In Discord Developer Portal, go to 'OAuth2' > 'URL Generator'")
    print("2. Select scopes: 'bot'")
    print("3. Select permissions:")
    print("   - Send Messages")
    print("   - Read Messages")
    print("   - Read Message History")
    print("   - Use External Emojis")
    print("   - Add Reactions")
    print("   - Embed Links")
    print("4. Copy the generated URL and open it to invite your bot")
    
    print("\n� IMPORTANT - Set Your Discord User ID:")
    print("1. Open Discord → Settings → Advanced → Enable 'Developer Mode'")
    print("2. Right-click your username → 'Copy ID'")
    print("3. Open bot.py and replace '123456789012345678' with your actual ID")
    print("4. This restricts !roast and !say commands to you only!")
    
    print("\n�🚀 After setting up the token and user ID:")
    print('Run: "/Users/arushbasliyal/Desktop/All projects/Discord-bot/.venv/bin/python" bot.py')
    
    print("\n💡 Current .env file contents:")
    if env_file.exists():
        with open('.env', 'r') as f:
            content = f.read()
            print(content)
    else:
        print("No .env file found")

if __name__ == "__main__":
    setup_bot_token()