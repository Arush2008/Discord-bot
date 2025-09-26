#!/usr/bin/env python3
"""
Discord Bot Authorization Manager
Easily add or remove authorized users for your Discord bot.
"""

import re

BOT_FILE = 'bot.py'

def read_bot_file():
    """Read the current bot.py file"""
    try:
        with open(BOT_FILE, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ {BOT_FILE} not found!")
        return None

def extract_authorized_users(content):
    """Extract current authorized user IDs from bot.py"""
    pattern = r'AUTHORIZED_USER_IDS\s*=\s*\[(.*?)\]'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("❌ Could not find AUTHORIZED_USER_IDS in bot.py")
        return []
    
    # Extract numbers from the list
    ids_text = match.group(1)
    ids = re.findall(r'(\d+)', ids_text)
    return [int(id_) for id_ in ids]

def update_authorized_users(content, user_ids):
    """Update the AUTHORIZED_USER_IDS list in the bot file content"""
    # Create the new list string
    if len(user_ids) == 0:
        new_list = "[]"
    elif len(user_ids) == 1:
        new_list = f"[\n    {user_ids[0]}  # Authorized user\n]"
    else:
        id_lines = []
        for i, user_id in enumerate(user_ids):
            comment = f"# Authorized user {i+1}"
            id_lines.append(f"    {user_id}  {comment}")
        new_list = "[\n" + ",\n".join(id_lines) + "\n]"
    
    # Replace the existing list
    pattern = r'(AUTHORIZED_USER_IDS\s*=\s*)\[.*?\]'
    replacement = f'\\1{new_list}'
    
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def save_bot_file(content):
    """Save the updated content to bot.py"""
    try:
        with open(BOT_FILE, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Error saving file: {e}")
        return False

def display_current_users(user_ids):
    """Display current authorized users"""
    print(f"\n👥 Current Authorized Users ({len(user_ids)}):")
    print("=" * 50)
    if not user_ids:
        print("❌ No authorized users configured!")
    else:
        for i, user_id in enumerate(user_ids, 1):
            print(f"{i}. {user_id}")

def main():
    print("🤖 Discord Bot Authorization Manager")
    print("=" * 50)
    
    # Read current bot file
    content = read_bot_file()
    if not content:
        return
    
    # Extract current authorized users
    current_users = extract_authorized_users(content)
    display_current_users(current_users)
    
    while True:
        print(f"\n📋 Options:")
        print("1. Add user")
        print("2. Remove user") 
        print("3. List users")
        print("4. Clear all users")
        print("5. Exit")
        
        choice = input("\n🔢 Enter choice (1-5): ").strip()
        
        if choice == '1':
            # Add user
            user_id = input("🆔 Enter Discord User ID to add: ").strip()
            if user_id.isdigit():
                user_id = int(user_id)
                if user_id not in current_users:
                    current_users.append(user_id)
                    print(f"✅ Added user {user_id}")
                else:
                    print(f"⚠️  User {user_id} already authorized")
            else:
                print("❌ Invalid user ID! Must be numbers only.")
                
        elif choice == '2':
            # Remove user
            if not current_users:
                print("❌ No users to remove!")
                continue
                
            display_current_users(current_users)
            try:
                index = int(input("\n🔢 Enter number to remove (or 0 to cancel): ")) - 1
                if index == -1:
                    continue
                if 0 <= index < len(current_users):
                    removed_user = current_users.pop(index)
                    print(f"✅ Removed user {removed_user}")
                else:
                    print("❌ Invalid selection!")
            except ValueError:
                print("❌ Please enter a valid number!")
                
        elif choice == '3':
            # List users
            display_current_users(current_users)
            
        elif choice == '4':
            # Clear all
            if current_users:
                confirm = input("⚠️  Clear ALL authorized users? (yes/no): ").lower()
                if confirm in ['yes', 'y']:
                    current_users.clear()
                    print("✅ All users cleared!")
                else:
                    print("❌ Cancelled")
            else:
                print("❌ No users to clear!")
                
        elif choice == '5':
            # Exit - save changes
            updated_content = update_authorized_users(content, current_users)
            if save_bot_file(updated_content):
                print("✅ Changes saved to bot.py")
                print("🔄 Restart your bot to apply changes!")
            else:
                print("❌ Failed to save changes!")
            break
            
        else:
            print("❌ Invalid choice! Please enter 1-5.")

if __name__ == "__main__":
    main()