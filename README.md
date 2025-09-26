# Discord Bot Project

A feature-rich Discord bot with fun commands, economy system, and interactive features.

## Features

1. **Basic Commands**
   - `!ping` - Check if bot is online
   - `!help` - Show all available commands

2. **Fun Commands**
   - `!joke` - Get a random joke
   - `!roast @user` - Send a friendly roast
   - `!compliment @user` - Give a wholesome compliment
   - `!say <message>` - Make the bot repeat your message

3. **Interactive Features**
   - `!quiz` - Answer trivia questions
   - `!meme` - Get random memes from Reddit

4. **Economy System**
   - `!balance [@user]` - Check coin balance
   - `!daily` - Claim daily coin rewards
   - Earn coins by using commands

5. **Auto Features**
   - Welcome messages for new members

## Setup Instructions

### 1. Create a Discord Application
1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to "Bot" section and click "Add Bot"
4. Copy the bot token (keep it secret!)

### 2. Local Development
1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your bot token:
   ```
   DISCORD_BOT_TOKEN=your_bot_token_here
   ```
4. Run the bot: `python bot.py`

### 3. Deploy to Render

#### Step 1: Prepare your code
- Make sure all files are committed to a Git repository
- Push to GitHub, GitLab, or Bitbucket

#### Step 2: Create Render Account
1. Go to [render.com](https://render.com)
2. Sign up for a free account
3. Connect your GitHub/GitLab account

#### Step 3: Create New Web Service
1. Click "New +" and select "Web Service"
2. Connect your repository
3. Configure the service:
   - **Name**: Your bot name
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

#### Step 4: Add Environment Variables
1. In the Render dashboard, go to your service
2. Click "Environment"
3. Add environment variable:
   - **Key**: `DISCORD_BOT_TOKEN`
   - **Value**: Your Discord bot token

#### Step 5: Deploy
1. Click "Deploy" to start the deployment
2. Wait for the build to complete
3. Your bot should now be online!

### 4. Invite Bot to Server
1. In Discord Developer Portal, go to "OAuth2" > "URL Generator"
2. Select scopes: `bot`
3. Select permissions:
   - Send Messages
   - Use Slash Commands
   - Read Message History
   - Add Reactions
   - Embed Links
4. Copy the generated URL and open it to invite your bot

## Bot Permissions Needed
- Send Messages
- Read Messages
- Read Message History
- Use External Emojis
- Add Reactions
- Embed Links
- Attach Files

## File Structure
```
Discord-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── Procfile           # Render deployment config
├── runtime.txt        # Python version specification
├── .env.example       # Example environment variables
└── README.md          # This file
```

## Troubleshooting

### Common Issues:
1. **Bot not responding**: Check if the bot token is correct
2. **Permission errors**: Make sure the bot has necessary permissions
3. **Meme command failing**: Reddit API might be down, bot will show fallback message

### Support
If you encounter issues, check:
- Bot token is correctly set in environment variables
- Bot has proper permissions in your Discord server
- All dependencies are installed correctly

## Contributing
Feel free to contribute by:
- Adding new commands
- Improving existing features
- Fixing bugs
- Adding better error handling

Enjoy your Discord bot! 🤖