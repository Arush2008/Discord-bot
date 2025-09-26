#!/usr/bin/env python3
"""
Discord Bot Invite URL Generator
Run this script to generate the proper invite URL for your Discord bot.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_invite_urls():
    """Generate invite URLs for the Discord bot"""
    
    print("🤖 Discord Bot Invite URL Generator")
    print("=" * 50)
    
    # Try to get bot token to extract application ID
    token = os.getenv('DISCORD_BOT_TOKEN')
    
    if not token:
        print("❌ No bot token found in environment variables!")
        print("Please add DISCORD_BOT_TOKEN to your .env file")
        return
    
    print("✅ Bot token found!")
    print("\n📋 To get your Bot's Application ID:")
    print("1. Go to https://discord.com/developers/applications")
    print("2. Click on your bot application")
    print("3. Copy the 'Application ID' (Client ID)")
    
    # Get Application ID from user
    app_id = input("\n🆔 Enter your Bot's Application ID: ").strip()
    
    if not app_id or not app_id.isdigit():
        print("❌ Invalid Application ID! Must be numbers only.")
        return
    
    print(f"\n🔗 Invite URLs for Bot ID: {app_id}")
    print("=" * 60)
    
    # Administrator permissions (easiest setup)
    admin_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions=8&scope=bot"
    print(f"\n👑 ADMINISTRATOR PERMISSIONS (Recommended for testing):")
    print(f"🔗 {admin_url}")
    
    # Specific permissions for this bot
    specific_perms = 388160  # Send Messages + Manage Messages + Embed Links + Add Reactions + Read Message History + Manage Roles
    specific_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={specific_perms}&scope=bot"
    print(f"\n🎯 SPECIFIC PERMISSIONS (Production ready):")
    print(f"🔗 {specific_url}")
    
    # Minimal permissions
    minimal_perms = 2048  # Send Messages only
    minimal_url = f"https://discord.com/api/oauth2/authorize?client_id={app_id}&permissions={minimal_perms}&scope=bot"
    print(f"\n📝 MINIMAL PERMISSIONS (Basic functionality only):")
    print(f"🔗 {minimal_url}")
    
    print(f"\n📋 How to use:")
    print("1. Copy one of the URLs above")
    print("2. Paste it in your browser")
    print("3. Select the server you want to add the bot to")
    print("4. Click 'Authorize'")
    print("5. Complete the captcha if prompted")
    
    print(f"\n⚠️  Important Notes:")
    print("- You must have 'Manage Server' permissions on the Discord server")
    print("- Use Administrator permissions for easiest setup")
    print("- The bot will appear in your server's member list once added")
    print("- Test with '!ping' command to verify it's working")

if __name__ == "__main__":
    generate_invite_urls()