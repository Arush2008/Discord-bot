import discord
from discord.ext import commands
import random
import asyncio
import aiohttp
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# CONFIGURATION - Set Discord user IDs here to restrict certain commands
# To find Discord ID: Enable Developer Mode in Discord → Right-click user name → Copy ID
# Add or remove user IDs from this list as needed
AUTHORIZED_USER_IDS = [
    934723467675332608,  # Authorized user 1
    883516391074971698   # Authorized user 2
]

# 1. Basic setup with command prefix "!" and message_content intent enabled
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

# Data file for persistent storage
DATA_FILE = 'user_data.json'

# Load user data from file
def load_user_data():
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}

# Save user data to file
def save_user_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(user_data, f, indent=2)
    except Exception as e:
        print(f"Error saving user data: {e}")

# Load existing data on startup
user_data = load_user_data()

# Shop items configuration
SHOP_ITEMS = {
    'say_unlock': {
        'name': '🗣️ Say Command Unlock',
        'price': 1000000,
        'description': 'Unlock the !say command for yourself!',
        'type': 'unlock'
    },
    'vip_role': {
        'name': '⭐ VIP Role',
        'price': 5000,
        'description': 'Get the exclusive VIP role!',
        'type': 'role',
        'role_name': 'VIP'
    },
    'premium_role': {
        'name': '💎 Premium Role', 
        'price': 10000,
        'description': 'Get the Premium role with special perks!',
        'type': 'role',
        'role_name': 'Premium'
    },
    'legendary_role': {
        'name': '🏆 Legendary Role',
        'price': 25000,
        'description': 'Join the legendary members club!',
        'type': 'role',
        'role_name': 'Legendary'
    },
    'elite_role': {
        'name': '👑 Elite Role',
        'price': 50000,
        'description': 'Become an elite member!',
        'type': 'role', 
        'role_name': 'Elite'
    }
}

# Jokes list for the !joke command
jokes = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "What do you call a fake noodle? An impasta!",
    "Why did the math book look so sad? Because it was full of problems!",
    "What do you call a bear with no teeth? A gummy bear!",
    "Why don't skeletons fight each other? They don't have the guts!",
    "What do you call a sleeping bull? A bulldozer!",
    "Why did the bicycle fall over? Because it was two-tired!",
    "What do you call a fish wearing a bowtie? Sofishticated!"
]

# Roasts list
roasts = [
    "You're like a cloud. When you disappear, it's a beautiful day!",
    "I'd agree with you, but then we'd both be wrong.",
    "You bring everyone so much joy... when you leave the room!",
    "If laughter is the best medicine, your face must be curing the world!",
    "You're not stupid; you just have bad luck thinking!",
    "I'd explain it to you, but I don't have any crayons with me.",
    "You're the reason God created the middle finger!",
    "If I had a dollar for every time you said something smart, I'd be broke!",
    "You're like a software update. Whenever I see you, I think 'Not now'!",
    "I'm not saying you're stupid, but you have bad luck when it comes to thinking!"
]

# Compliments list
compliments = [
    "You're absolutely amazing and brighten everyone's day!",
    "Your smile could light up the darkest room!",
    "You have the best laugh, it's so contagious!",
    "You're incredibly thoughtful and kind!",
    "Your positive energy is inspiring to everyone around you!",
    "You have such a creative and brilliant mind!",
    "You make the world a better place just by being in it!",
    "Your friendship means the world to people!",
    "You have an amazing sense of humor!",
    "You're stronger than you know and braver than you feel!"
]

# Quiz questions
quiz_questions = [
    {
        "question": "What is the capital of France?",
        "options": ["A) London", "B) Berlin", "C) Paris", "D) Madrid"],
        "answer": "C"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["A) Venus", "B) Mars", "C) Jupiter", "D) Saturn"],
        "answer": "B"
    },
    {
        "question": "What is 2 + 2?",
        "options": ["A) 3", "B) 4", "C) 5", "D) 6"],
        "answer": "B"
    },
    {
        "question": "Who painted the Mona Lisa?",
        "options": ["A) Van Gogh", "B) Picasso", "C) Leonardo da Vinci", "D) Michelangelo"],
        "answer": "C"
    },
    {
        "question": "What is the largest ocean on Earth?",
        "options": ["A) Atlantic", "B) Indian", "C) Arctic", "D) Pacific"],
        "answer": "D"
    }
]

current_quiz = {}

# Bot event: Ready
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# 10. Welcome message when a new user joins the server
@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='general')
    if channel:
        embed = discord.Embed(
            title="Welcome! 🎉",
            description=f"Welcome to the server, {member.mention}! We're glad to have you here!",
            color=0x00ff00
        )
        await channel.send(embed=embed)

# Helper function to delete command messages for cleaner chat (for others, not the author)
async def delete_command_message(ctx, delete_for_author=False):
    # Only delete the message if we want to hide it from everyone, 
    # or if it's a restricted command that failed
    if delete_for_author:
        try:
            await ctx.message.delete()
        except discord.NotFound:
            pass  # Message already deleted
        except discord.Forbidden:
            pass  # No permission to delete
        except Exception:
            pass  # Any other error

# Ultra-fast message deletion function for !say command
async def delete_message_fast(message):
    """Delete message as fast as possible with multiple attempts"""
    try:
        await message.delete()
    except discord.NotFound:
        pass  # Message already deleted
    except discord.Forbidden:
        pass  # No permission to delete
    except discord.HTTPException:
        pass  # Network error
    except Exception:
        pass  # Any other error

# Helper function to check if user is authorized for restricted commands
def is_authorized(user_id):
    return user_id in AUTHORIZED_USER_IDS

# Helper function to check if user can use say command
def can_use_say_command(user_id):
    if is_authorized(user_id):  # Owner can always use it
        return True
    data = get_user_data(user_id)
    return 'say_unlock' in data['purchased_items']

# Enhanced role creation and assignment system
async def get_or_create_role(guild, role_name, color=None):
    """Create or get a role in the Discord server with proper error handling"""
    print(f"🔍 Looking for role '{role_name}' in guild '{guild.name}'")
    
    # First, check if role already exists
    role = discord.utils.get(guild.roles, name=role_name)
    
    if role:
        print(f"✅ Found existing role: {role_name} (ID: {role.id}, Color: {role.color})")
        return role
    
    # Role doesn't exist, create it
    print(f"🆕 Creating new role: {role_name}")
    
    try:
        # Check bot permissions first
        bot_member = guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            print(f"❌ Bot missing 'Manage Roles' permission in {guild.name}")
            return None
        
        # Set role colors
        if color is None:
            role_colors = {
                'VIP': 0xFFD700,        # Gold
                'Premium': 0x9932CC,    # Purple  
                'Legendary': 0xFF4500,  # Orange Red
                'Elite': 0xDC143C       # Crimson
            }
            color = role_colors.get(role_name, 0x00FF00)  # Default green
        
        # Create the role with enhanced properties
        role = await guild.create_role(
            name=role_name,
            color=discord.Color(color),
            hoist=True,
            mentionable=True,
            reason=f"Shop system: Creating role for purchases"
        )
        
        print(f"🎉 Successfully created role: {role_name}")
        print(f"   📊 Role ID: {role.id}")
        print(f"   🎨 Role Color: {role.color}")
        print(f"   📍 Role Position: {role.position}")
        print(f"   🏷️ Role Hoisted: {role.hoist}")
        print(f"   🔔 Role Mentionable: {role.mentionable}")
        
        return role
        
    except discord.Forbidden as e:
        print(f"❌ Permission denied creating role '{role_name}': {e}")
        print(f"   💡 Make sure bot has 'Manage Roles' permission")
        print(f"   💡 Make sure bot's role is higher than roles it's trying to create")
        return None
        
    except discord.HTTPException as e:
        print(f"❌ HTTP error creating role '{role_name}': {e}")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error creating role '{role_name}': {e}")
        return None


# Enhanced role assignment function
async def assign_role_to_user(guild, user, role_name, force_assign=False):
    """Assign a role to a user with comprehensive error checking"""
    
    # Check if guild is valid
    if not guild:
        print(f"❌ No guild provided for role assignment")
        return False, "No server context available for role assignment"
    
    print(f"🎯 Assigning role '{role_name}' to {user} in {guild.name}")
    
    # Get or create the role
    role = await get_or_create_role(guild, role_name)
    if not role:
        return False, "Could not create or find the role"
    
    # Check if user already has the role (unless forced)
    if role in user.roles and not force_assign:
        print(f"ℹ️  User {user} already has role {role_name}")
        return "already_has", f"You already have the {role_name} role!"
    
    try:
        # Check bot permissions
        bot_member = guild.get_member(bot.user.id)
        if not bot_member.guild_permissions.manage_roles:
            return False, "Bot missing 'Manage Roles' permission"
        
        # Check role hierarchy
        if role.position >= bot_member.top_role.position:
            return False, f"Bot's role is too low to assign {role_name} (hierarchy issue)"
        
        # Assign the role
        await user.add_roles(role, reason=f"Shop purchase: {role_name}")
        
        print(f"✅ Successfully assigned role {role_name} to {user}")
        return True, f"Successfully granted {role_name} role!"
        
    except discord.Forbidden as e:
        print(f"❌ Permission denied assigning role: {e}")
        return False, "Permission denied - check bot permissions and role hierarchy"
        
    except discord.HTTPException as e:
        print(f"❌ HTTP error assigning role: {e}")
        return False, f"Discord error: {str(e)}"
        
    except Exception as e:
        print(f"❌ Unexpected error assigning role: {e}")
        return False, f"Unexpected error: {str(e)}"

# Helper function to get or create user data
def get_user_data(user_id):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            'coins': 0,
            'last_daily': None,
            'last_work': None,
            'purchased_items': [],
            'unlocked_commands': []
        }
    return user_data[str(user_id)]

# Helper function to add coins to user
def add_coins(user_id, amount):
    data = get_user_data(user_id)
    data['coins'] += amount
    save_user_data()  # Save after modifying data
    return data['coins']

# 2. Ping command that replies with "Pong!"
@bot.command(name='ping')
async def ping(ctx):
    add_coins(ctx.author.id, 1)
    await ctx.send('Pong! 🏓')

# 3. Joke command that picks a random joke from a list
@bot.command(name='joke')
async def joke(ctx):
    add_coins(ctx.author.id, 2)
    random_joke = random.choice(jokes)
    embed = discord.Embed(title="Here's a joke for you! 😄", description=random_joke, color=0xffff00)
    await ctx.send(embed=embed)

# 4. Roast command that sends a funny roast targeting the mentioned user (RESTRICTED)
@bot.command(name='roast')
async def roast(ctx, member: discord.Member = None):
    # Check if user is authorized
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
        
    if member is None:
        embed = discord.Embed(
            title="❌ Missing Target",
            description="Please mention someone to roast! Usage: `!roast @username`",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    if member == ctx.author:
        embed = discord.Embed(
            title="🤔 Nice Try",
            description="You can't roast yourself! That's just sad! 😢",
            color=0xffff00
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    add_coins(ctx.author.id, 3)
    random_roast = random.choice(roasts)
    embed = discord.Embed(
        title="🔥 ROASTED! 🔥",
        description=f"{member.mention}, {random_roast}",
        color=0xff4500
    )
    await ctx.send(embed=embed)

# 5. Compliment command that sends a random wholesome compliment
@bot.command(name='compliment')
async def compliment(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    add_coins(ctx.author.id, 2)
    random_compliment = random.choice(compliments)
    embed = discord.Embed(
        title="💖 A Compliment! 💖",
        description=f"{member.mention}, {random_compliment}",
        color=0xff69b4
    )
    await ctx.send(embed=embed)

# 6. Quiz command with multiple choice questions
@bot.command(name='quiz')
async def quiz(ctx):
    if ctx.channel.id in current_quiz:
        await ctx.send("A quiz is already running in this channel! Wait for it to finish.")
        return
    
    question_data = random.choice(quiz_questions)
    current_quiz[ctx.channel.id] = {
        'question': question_data,
        'answered': False
    }
    
    embed = discord.Embed(title="🧠 Quiz Time! 🧠", color=0x00bfff)
    embed.add_field(name="Question:", value=question_data['question'], inline=False)
    embed.add_field(name="Options:", value='\n'.join(question_data['options']), inline=False)
    embed.add_field(name="Instructions:", value="Type A, B, C, or D to answer!", inline=False)
    
    await ctx.send(embed=embed)
    
    # Wait for answer
    def check(m):
        return (m.channel == ctx.channel and 
                m.content.upper() in ['A', 'B', 'C', 'D'] and
                not current_quiz[ctx.channel.id]['answered'])
    
    try:
        answer_msg = await bot.wait_for('message', check=check, timeout=30.0)
        current_quiz[ctx.channel.id]['answered'] = True
        
        if answer_msg.content.upper() == question_data['answer']:
            add_coins(answer_msg.author.id, 10)
            embed = discord.Embed(
                title="🎉 Correct! 🎉",
                description=f"Great job, {answer_msg.author.mention}! You earned 10 coins!",
                color=0x00ff00
            )
        else:
            embed = discord.Embed(
                title="❌ Incorrect! ❌",
                description=f"Sorry {answer_msg.author.mention}, the correct answer was {question_data['answer']}",
                color=0xff0000
            )
        
        await ctx.send(embed=embed)
        
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="⏰ Time's Up! ⏰",
            description=f"Nobody answered in time! The correct answer was {question_data['answer']}",
            color=0x808080
        )
        await ctx.send(embed=embed)
    
    finally:
        if ctx.channel.id in current_quiz:
            del current_quiz[ctx.channel.id]

# 7. Meme command that fetches a random meme from Reddit
@bot.command(name='meme')
async def meme(ctx):
    add_coins(ctx.author.id, 2)
    
    # List of meme subreddits
    subreddits = ['memes', 'dankmemes', 'wholesomememes', 'ProgrammerHumor', 'funny']
    subreddit = random.choice(subreddits)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://www.reddit.com/r/{subreddit}/random/.json') as response:
                if response.status == 200:
                    data = await response.json()
                    meme_data = data[0]['data']['children'][0]['data']
                    
                    if meme_data['url'].endswith(('.jpg', '.png', '.gif', '.jpeg')):
                        embed = discord.Embed(
                            title=meme_data['title'],
                            color=0xff4500
                        )
                        embed.set_image(url=meme_data['url'])
                        embed.set_footer(text=f"From r/{subreddit} | 👍 {meme_data['score']}")
                        await ctx.send(embed=embed)
                    else:
                        await ctx.send(f"Here's a meme: {meme_data['url']}")
                else:
                    await ctx.send("Couldn't fetch a meme right now. Try again later! 😅")
    except:
        # Fallback if Reddit API fails
        fallback_memes = [
            "https://i.imgur.com/dQw4w9W.gif",  # You know what this is 😉
            "Sorry, couldn't fetch a meme right now! Here's a joke instead: Why don't programmers like nature? It has too many bugs! 🐛"
        ]
        await ctx.send(random.choice(fallback_memes))

# 8. Say command is now handled in on_message event for instant deletion
# This prevents the command from appearing even for a millisecond

# 9. Simple text-based economy system
@bot.command(name='balance')
async def balance(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    user_coins = get_user_data(member.id)['coins']
    embed = discord.Embed(
        title="💰 Balance 💰",
        description=f"{member.mention} has **{user_coins}** coins!",
        color=0xffd700
    )
    await ctx.send(embed=embed)

@bot.command(name='daily')
async def daily(ctx):
    user_id = str(ctx.author.id)
    data = get_user_data(ctx.author.id)
    
    now = datetime.now()
    last_daily = data.get('last_daily')
    
    if last_daily:
        last_daily_time = datetime.fromisoformat(last_daily)
        if now - last_daily_time < timedelta(hours=24):
            time_left = timedelta(hours=24) - (now - last_daily_time)
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            embed = discord.Embed(
                title="⏰ Daily Cooldown",
                description=f"{ctx.author.mention}, you've already claimed your daily reward!\nCome back in {hours}h {minutes}m",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            return
    
    daily_amount = random.randint(50, 100)
    data['coins'] += daily_amount
    data['last_daily'] = now.isoformat()
    save_user_data()  # Save after modifying data
    
    embed = discord.Embed(
        title="🎁 Daily Reward! 🎁",
        description=f"{ctx.author.mention} received **{daily_amount}** coins! Come back tomorrow for more!",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


# 🎮 NEW GAME COMMANDS

# Rock Paper Scissors game
@bot.command(name='rps')
async def rock_paper_scissors(ctx, user_choice=None):
    if user_choice is None:
        await ctx.send("Please choose rock, paper, or scissors! Usage: `!rps rock`")
        return
    
    user_choice = user_choice.lower()
    if user_choice not in ['rock', 'paper', 'scissors']:
        await ctx.send("Invalid choice! Please choose: rock, paper, or scissors")
        return
    
    bot_choice = random.choice(['rock', 'paper', 'scissors'])
    
    # Determine winner
    if user_choice == bot_choice:
        result = "It's a tie!"
        color = 0xffff00
        coins = 1
    elif (user_choice == 'rock' and bot_choice == 'scissors') or \
         (user_choice == 'paper' and bot_choice == 'rock') or \
         (user_choice == 'scissors' and bot_choice == 'paper'):
        result = f"You win! 🎉"
        color = 0x00ff00
        coins = 3
    else:
        result = "You lose! 😢"
        color = 0xff0000
        coins = 1
    
    add_coins(ctx.author.id, coins)
    
    embed = discord.Embed(title="🪨📄✂️ Rock Paper Scissors", color=color)
    embed.add_field(name=f"{ctx.author.display_name}'s choice", value=user_choice.capitalize(), inline=True)
    embed.add_field(name="My choice", value=bot_choice.capitalize(), inline=True)
    embed.add_field(name="Result", value=f"{ctx.author.mention}: {result}\n+{coins} coins!", inline=False)
    await ctx.send(embed=embed)


# Guess the Number game
guess_games = {}

@bot.command(name='guess')
async def guess_number(ctx):
    if ctx.channel.id in guess_games:
        game = guess_games[ctx.channel.id]
        embed = discord.Embed(
            title="🔢 Number Guessing Game",
            description=f"Game already running! Guess a number between 1-100\n"
                       f"Attempts: {game['attempts']}",
            color=0x00bfff
        )
        await ctx.send(embed=embed)
        return
    
    number = random.randint(1, 100)
    guess_games[ctx.channel.id] = {
        'number': number,
        'attempts': 0,
        'starter': ctx.author
    }
    
    embed = discord.Embed(
        title="🔢 Number Guessing Game Started!",
        description="I'm thinking of a number between 1-100!\nJust type a number to guess!",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.event  
async def on_message(message):
    # Handle !say command with MAXIMUM SPEED deletion
    if message.content.startswith('!say') and not message.author.bot:
        
        # FASTEST possible deletion with minimal delay
        deletion_task = asyncio.create_task(message.delete())
        
        # Process command while deletion happens
        if can_use_say_command(message.author.id):
            # Extract the message content
            if len(message.content) > 5:  # More than just "!say "
                say_content = message.content[5:]  # Remove "!say " prefix
                if say_content.strip():
                    add_coins(message.author.id, 1)
                    # Send response immediately
                    await message.channel.send(say_content)
                else:
                    embed = discord.Embed(
                        title="❌ Missing Message",
                        description="Usage: `!say <message>`",
                        color=0xff0000
                    )
                    await message.channel.send(embed=embed, delete_after=3)
            else:
                embed = discord.Embed(
                    title="❌ Missing Message", 
                    description="Usage: `!say <message>`",
                    color=0xff0000
                )
                await message.channel.send(embed=embed, delete_after=3)
        else:
            # Unauthorized user
            embed = discord.Embed(
                title="🚫 Access Denied",
                description="Owner only command!",
                color=0xff0000
            )
            await message.channel.send(embed=embed, delete_after=3)
        
        # Wait for deletion to complete
        try:
            await deletion_task
        except:
            pass
        return
    
    # Ignore bot messages and process other commands
    if message.author.bot:
        return
    
    # Handle guess game only for non-command messages
    if message.channel.id in guess_games and not message.content.startswith('!'):
        try:
            guess = int(message.content)
            game = guess_games[message.channel.id]
            game['attempts'] += 1
            
            if guess == game['number']:
                add_coins(message.author.id, 10)
                embed = discord.Embed(
                    title="🎉 Congratulations!",
                    description=f"{message.author.mention} guessed the number {game['number']} "
                               f"in {game['attempts']} attempts!\n+10 coins!",
                    color=0x00ff00
                )
                await message.channel.send(embed=embed)
                del guess_games[message.channel.id]
            elif guess < game['number']:
                await message.add_reaction('📈')  # Higher
            else:
                await message.add_reaction('📉')  # Lower
                
        except ValueError:
            pass  # Not a number, ignore
    
    # Process all commands except !say (which is handled above)
    if message.content.startswith('!') and not message.content.startswith('!say'):
        await bot.process_commands(message)


# Would You Rather command
wyr_questions = [
    "Would you rather have the ability to fly OR be invisible?",
    "Would you rather eat pizza for every meal OR never eat pizza again?",
    "Would you rather live in the past OR live in the future?",
    "Would you rather have super strength OR super speed?",
    "Would you rather be able to read minds OR predict the future?",
    "Would you rather have unlimited money OR unlimited time?",
    "Would you rather be famous OR be the smartest person alive?",
    "Would you rather live underwater OR live in space?",
    "Would you rather have wings OR have gills?",
    "Would you rather control fire OR control water?"
]

@bot.command(name='wyr')
async def would_you_rather(ctx):
    add_coins(ctx.author.id, 1)
    question = random.choice(wyr_questions)
    
    embed = discord.Embed(
        title="🤔 Would You Rather?",
        description=question,
        color=0xff69b4
    )
    embed.set_footer(text="React with 👍 or 👎 to vote!")
    
    msg = await ctx.send(embed=embed)
    await msg.add_reaction('👍')
    await msg.add_reaction('👎')


# 🤖 UTILITY COMMANDS

# Random Facts command
facts = [
    "Honey never spoils! Archaeologists have found 3000-year-old honey that's still edible.",
    "A group of flamingos is called a 'flamboyance'.",
    "Bananas are berries, but strawberries aren't!",
    "Octopuses have three hearts and blue blood.",
    "The shortest war in history lasted only 38-45 minutes.",
    "A day on Venus is longer than its year.",
    "Sharks have been around longer than trees.",
    "There are more possible games of chess than atoms in the observable universe.",
    "Wombat poop is cube-shaped.",
    "The human brain contains approximately 86 billion neurons."
]

@bot.command(name='fact')
async def random_fact(ctx):
    add_coins(ctx.author.id, 1)
    fact = random.choice(facts)
    
    embed = discord.Embed(
        title="🧠 Random Fact",
        description=fact,
        color=0x9932cc
    )
    await ctx.send(embed=embed)


# Server Info command
@bot.command(name='serverinfo')
async def server_info(ctx):
    guild = ctx.guild
    embed = discord.Embed(
        title=f"📊 {guild.name} Server Info",
        color=0x00bfff
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👥 Members", value=guild.member_count, inline=True)
    embed.add_field(name="📝 Text Channels", value=len(guild.text_channels), inline=True)
    embed.add_field(name="🔊 Voice Channels", value=len(guild.voice_channels), inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    await ctx.send(embed=embed)


# User Info command
@bot.command(name='userinfo')
async def user_info(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author
    
    embed = discord.Embed(
        title=f"👤 {member.display_name}'s Info",
        color=member.color if member.color != discord.Color.default() else 0x00bfff
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)
    embed.add_field(name="📛 Username", value=str(member), inline=True)
    embed.add_field(name="🆔 ID", value=member.id, inline=True)
    embed.add_field(name="📅 Joined Server", value=member.joined_at.strftime("%B %d, %Y"), inline=False)
    embed.add_field(name="📅 Account Created", value=member.created_at.strftime("%B %d, %Y"), inline=False)
    
    # Show roles (excluding @everyone)
    roles = [role.mention for role in member.roles[1:]]
    if roles:
        embed.add_field(name="🏷️ Roles", value=" ".join(roles), inline=False)
    
    await ctx.send(embed=embed)


# 💰 MORE ECONOMY COMMANDS

# Work command
work_jobs = [
    ("Pizza Delivery", (10, 25)),
    ("Dog Walker", (8, 20)),
    ("Programmer", (20, 50)),
    ("Streamer", (5, 100)),
    ("Teacher", (15, 30)),
    ("Artist", (12, 35)),
    ("Chef", (18, 40)),
    ("Gamer", (3, 80)),
    ("YouTuber", (1, 150)),
    ("Musician", (10, 45))
]

@bot.command(name='work')
async def work(ctx):
    user_id = str(ctx.author.id)
    data = get_user_data(ctx.author.id)
    
    # Check cooldown (30 minutes)
    now = datetime.now()
    last_work = data.get('last_work')
    
    if last_work:
        last_work_time = datetime.fromisoformat(last_work)
        if now - last_work_time < timedelta(minutes=30):
            time_left = timedelta(minutes=30) - (now - last_work_time)
            minutes_left = time_left.seconds // 60
            embed = discord.Embed(
                title="😴 Work Cooldown",
                description=f"{ctx.author.mention}, you're tired! Rest for {minutes_left} more minutes before working again.",
                color=0xff9900
            )
            await ctx.send(embed=embed)
            return
    
    job, (min_pay, max_pay) = random.choice(work_jobs)
    pay = random.randint(min_pay, max_pay)
    
    data['coins'] += pay
    data['last_work'] = now.isoformat()
    save_user_data()  # Save after modifying data
    
    embed = discord.Embed(
        title="💼 Work Complete!",
        description=f"{ctx.author.mention} worked as a {job} and earned **{pay}** coins!",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


# Leaderboard command
@bot.command(name='leaderboard', aliases=['lb'])
async def leaderboard(ctx):
    if not user_data:
        await ctx.send("No one has any coins yet! Use some commands to start earning!")
        return
    
    # Sort users by coins
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]['coins'], reverse=True)
    top_10 = sorted_users[:10]
    
    embed = discord.Embed(
        title="🏆 Coin Leaderboard",
        color=0xffd700
    )
    
    for i, (user_id, data) in enumerate(top_10):
        try:
            user = bot.get_user(int(user_id))
            name = user.display_name if user else f"User {user_id}"
            
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            embed.add_field(
                name=f"{medal} {name}",
                value=f"{data['coins']} coins",
                inline=False
            )
        except:
            pass
    
    await ctx.send(embed=embed)


# Poll command
@bot.command(name='poll')
async def poll(ctx, question, *options):
    if len(options) < 2:
        await ctx.send("Please provide at least 2 options! Usage: `!poll \"Question?\" \"Option 1\" \"Option 2\"`")
        return
    
    if len(options) > 10:
        await ctx.send("Too many options! Maximum is 10.")
        return
    
    # Number emojis
    numbers = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
    
    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=0x00bfff
    )
    
    for i, option in enumerate(options):
        embed.add_field(
            name=f"{numbers[i]} Option {i+1}",
            value=option,
            inline=False
        )
    
    embed.set_footer(text="React with the corresponding number to vote!")
    
    msg = await ctx.send(embed=embed)
    for i in range(len(options)):
        await msg.add_reaction(numbers[i])


# 🔥 ADDITIONAL COMMANDS

@bot.command(name="stealth_say")
async def stealth_say(ctx, *, message: str):
    """Alternative say command that deletes the trigger message quickly"""
    # Check authorization
    if not can_use_say_command(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    # Delete the command message quickly
    try:
        await ctx.message.delete()
    except:
        pass
    
    # Send the message publicly
    await ctx.send(message)
    add_coins(ctx.author.id, 1)


@bot.command(name="stealth_roast")
async def stealth_roast(ctx, target: discord.Member):
    """Alternative roast command that deletes the trigger message quickly"""
    # Check authorization
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    # Delete the command message quickly
    try:
        await ctx.message.delete()
    except:
        pass

    if target == ctx.author:
        embed = discord.Embed(
            title="🤔 Nice Try",
            description="You can't roast yourself! That's just sad! 😢",
            color=0xffff00
        )
        await ctx.send(embed=embed, delete_after=5)
        return

    # Send the roast publicly
    random_roast = random.choice(roasts)
    embed = discord.Embed(
        title="🔥 ROASTED! 🔥",
        description=f"{target.mention}, {random_roast}",
        color=0xff4500
    )
    await ctx.send(embed=embed)
    add_coins(ctx.author.id, 3)


# 🛒 SHOP SYSTEM

@bot.command(name='shop')
async def shop(ctx):
    """Display the shop with items user can purchase - EPHEMERAL MESSAGE"""
    # Check if command is used in a server (not DMs)
    if not ctx.guild:
        embed = discord.Embed(
            title="❌ Server Only Command",
            description="The shop command can only be used in a server, not in DMs!",
            color=discord.Color.red()
        )
        await ctx.author.send(embed=embed)
        return
    
    # Delete the command message for privacy
    try:
        await ctx.message.delete()
    except:
        pass
    
    user_coins = get_user_data(ctx.author.id)['coins']
    
    embed = discord.Embed(
        title="🛒 **PRIVATE COIN SHOP** 🛒",
        description=f"💰 Your Balance: **{user_coins:,}** coins\n\n"
                   "🔒 **This message is only visible to you!**\n"
                   "Other server members cannot see this shop.",
        color=0xffd700
    )
    
    shop_text = ""
    
    for i, (item_id, item_data) in enumerate(SHOP_ITEMS.items(), 1):
        price_formatted = f"{item_data['price']:,}"
        
        # Check if user can afford it
        affordable = "✅ **AFFORDABLE**" if user_coins >= item_data['price'] else "❌ **TOO EXPENSIVE**"
        
        # Check if already purchased
        user_data_obj = get_user_data(ctx.author.id)
        if item_id in user_data_obj['purchased_items']:
            affordable = "✨ **ALREADY OWNED**"
        
        shop_text += f"**{i}.** {item_data['name']}\n"
        shop_text += f"💸 **Price:** {price_formatted} coins\n"
        shop_text += f"📝 **Description:** {item_data['description']}\n"
        shop_text += f"📊 **Status:** {affordable}\n"
        shop_text += "─" * 40 + "\n\n"
    
    embed.description += f"\n{shop_text}"
    embed.set_footer(text="💡 Use !buy <item_number> to purchase! • Only you can see this message")
    
    # Send in server channel but make it private-looking and auto-delete
    shop_msg = await ctx.send(f"🔒 {ctx.author.mention}", embed=embed, delete_after=45)
    
    # Brief pause then remove the mention for cleaner appearance
    await asyncio.sleep(1)
    try:
        await shop_msg.edit(content="🔒 **Private Shop** (auto-deleting)", embed=embed)
    except:
        pass  # Message might have been deleted already


@bot.command(name='buy')
async def buy_item(ctx, item_number: int = None):
    """Purchase an item from the shop - PRIVATE TRANSACTION"""
    
    # Check if command is used in a server (not DMs)
    if not ctx.guild:
        embed = discord.Embed(
            title="❌ Server Only Command",
            description="The buy command can only be used in a server, not in DMs!\n"
                       "Please go to the server and use `!buy <number>` there.",
            color=discord.Color.red()
        )
        await ctx.author.send(embed=embed)
        return
    
    print(f"🛒 Buy command used by {ctx.author} in {ctx.guild.name}")
    
    # Delete the command message for privacy
    try:
        await ctx.message.delete()
    except Exception:
        pass
    
    if item_number is None:
        embed = discord.Embed(
            title="❌ Missing Item Number",
            description="Usage: `!buy <item_number>`\nUse `!shop` to see items!",
            color=0xff0000
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}", embed=embed, delete_after=10)
        return
    
    # Get item by number
    items_list = list(SHOP_ITEMS.items())
    if item_number < 1 or item_number > len(items_list):
        embed = discord.Embed(
            title="❌ Invalid Item Number",
            description=f"Please choose between 1-{len(items_list)}!",
            color=0xff0000
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}", embed=embed, delete_after=10)
        return
    
    item_id, item_data = items_list[item_number - 1]
    user_data_obj = get_user_data(ctx.author.id)
    
    # Check if already purchased - special handling for roles
    if item_id in user_data_obj['purchased_items']:
        # For roles, offer to equip them for free
        if item_data['type'] == 'role':
            class EquipOwnedRoleView(discord.ui.View):
                def __init__(self, guild, user, role_name):
                    super().__init__(timeout=60)
                    self.guild = guild
                    self.user = user
                    self.role_name = role_name
                
                @discord.ui.button(label="✅ Equip Role", 
                                 style=discord.ButtonStyle.green)
                async def equip_role(self, button: discord.ui.Button, 
                                   interaction: discord.Interaction):
                    # Force assign the role (re-equip it)
                    equip_result, equip_msg = await assign_role_to_user(
                        self.guild, 
                        self.user, 
                        self.role_name, 
                        force_assign=True
                    )
                    
                    if equip_result is True:
                        success_embed = discord.Embed(
                            title="✅ Role Equipped!",
                            description=f"👑 **{item_data['role_name']} role "
                                      f"equipped!**\n"
                                      f"You can now use this role in all chats.\n\n"
                                      f"💰 **No coins charged** - you already "
                                      f"owned this role!",
                            color=discord.Color.green()
                        )
                        await interaction.response.edit_message(embed=success_embed, 
                                                              view=None)
                    else:
                        error_embed = discord.Embed(
                            title="❌ Equip Failed",
                            description=f"Failed to equip role: {equip_msg}",
                            color=discord.Color.red()
                        )
                        await interaction.response.edit_message(embed=error_embed, 
                                                              view=None)
                
                @discord.ui.button(label="❌ Cancel", 
                                 style=discord.ButtonStyle.gray)
                async def cancel_equip(self, button: discord.ui.Button, 
                                     interaction: discord.Interaction):
                    cancel_embed = discord.Embed(
                        title="🔄 Cancelled",
                        description="Role equip cancelled.",
                        color=discord.Color.orange()
                    )
                    await interaction.response.edit_message(embed=cancel_embed, 
                                                          view=None)
            
            owned_role_embed = discord.Embed(
                title="🎭 Role Already Owned",
                description=f"You already own **{item_data['name']}**!\n\n"
                          f"Would you like to **equip/re-equip** it for **FREE**?\n"
                          f"This ensures it's properly assigned and visible.\n\n"
                          f"💰 **Current Balance:** {user_data_obj['coins']:,} coins",
                color=discord.Color.blue()
            )
            
            print(f"🔍 Creating EquipOwnedRoleView with:")
            print(f"   Guild: {ctx.guild} ({ctx.guild.name if ctx.guild else 'None'})")
            print(f"   User: {ctx.author}")
            print(f"   Role: {item_data['role_name']}")
            
            view = EquipOwnedRoleView(ctx.guild, ctx.author, item_data['role_name'])
            # For role interactions, send in server to maintain guild context
            await ctx.send(f"{ctx.author.mention}", embed=owned_role_embed, 
                         view=view, delete_after=60)
            return
        
        # For non-role items, show normal "already owned" message
        embed = discord.Embed(
            title="✨ Already Owned!",
            description=f"You already own **{item_data['name']}**!",
            color=0xffff00
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}", embed=embed, delete_after=10)
        return
    
    # Check if user has enough coins with detailed message
    if user_data_obj['coins'] < item_data['price']:
        needed = item_data['price'] - user_data_obj['coins']
        embed = discord.Embed(
            title="💸 Insufficient Balance!",
            description=f"**Item:** {item_data['name']}\n"
                       f"**Price:** {item_data['price']:,} coins\n"
                       f"**Your Balance:** {user_data_obj['coins']:,} coins\n"
                       f"**You Need:** {needed:,} more coins\n\n"
                       f"💡 *Earn more coins by using commands, working, or claiming daily rewards!*",
            color=0xff0000
        )
        try:
            await ctx.author.send(embed=embed)
        except discord.Forbidden:
            await ctx.send(f"{ctx.author.mention}", embed=embed, delete_after=15)
        return
    
    # Show confirmation before purchase
    confirm_embed = discord.Embed(
        title="🛒 Purchase Confirmation",
        description=f"**Are you sure you want to buy:**\n\n"
                   f"**Item:** {item_data['name']}\n"
                   f"**Price:** {item_data['price']:,} coins\n"
                   f"**Description:** {item_data['description']}\n\n"
                   f"**Your current balance:** {user_data_obj['coins']:,} coins\n"
                   f"**Balance after purchase:** {user_data_obj['coins'] - item_data['price']:,} coins\n\n"
                   f"React with ✅ to confirm or ❌ to cancel",
        color=0xffaa00
    )
    
    try:
        confirm_msg = await ctx.author.send(embed=confirm_embed)
        await confirm_msg.add_reaction('✅')
        await confirm_msg.add_reaction('❌')
        
        def check(reaction, user):
            return (user == ctx.author and 
                   str(reaction.emoji) in ['✅', '❌'] and 
                   reaction.message.id == confirm_msg.id)
        
        try:
            reaction, _ = await bot.wait_for('reaction_add', check=check, timeout=30.0)
            
            if str(reaction.emoji) == '❌':
                cancel_embed = discord.Embed(
                    title="❌ Purchase Cancelled",
                    description="Your purchase has been cancelled.",
                    color=0x808080
                )
                await ctx.author.send(embed=cancel_embed)
                return
            
            # For role purchases, test assignment FIRST before deducting coins
            if item_data['type'] == 'role':
                print("🛒 Pre-purchase role validation...")
                print(f"   👤 User: {ctx.author} ({ctx.author.id})")
                print(f"   🏷️  Role: {item_data['role_name']}")
                print(f"   🏰 Guild: {ctx.guild.name} ({ctx.guild.id})")
                
                # Test role assignment BEFORE deducting coins
                result, message = await assign_role_to_user(
                    ctx.guild,
                    ctx.author,
                    item_data['role_name']
                )
                
                if result == False:
                    # Role assignment failed - don't deduct coins
                    fail_description = (
                        f"**Role Assignment Failed:** {message}\n\n"
                        "💡 **Troubleshooting:**\n"
                        "• Check bot has 'Manage Roles' permission\n"
                        "• Ensure bot role is higher than shop roles\n"
                        "• Try `!checkperms` to diagnose issues\n\n"
                        f"💰 **No coins were deducted** - balance: "
                        f"{user_data_obj['coins']:,} coins"
                    )
                    fail_embed = discord.Embed(
                        title="❌ Purchase Failed",
                        description=fail_description,
                        color=discord.Color.red()
                    )
                    await ctx.respond(embed=fail_embed, ephemeral=True)
                    return
                print("✅ Role assignment validated - proceeding with purchase")
            
            # Process purchase - deduct coins and save
            user_data_obj['coins'] -= item_data['price']
            user_data_obj['purchased_items'].append(item_id)
            save_user_data()  # Save after purchase
            
            # Handle different item types
            success_msg = "🎉 **PURCHASE CONFIRMED!** 🎉\n\n"
            success_msg += f"✅ You successfully bought **{item_data['name']}**!\n"
            remaining_coins = user_data_obj['coins']
            success_msg += f"💰 **Remaining balance:** {remaining_coins:,} coins\n\n"
            
            if item_data['type'] == 'unlock':
                if item_id == 'say_unlock':
                    user_data_obj['unlocked_commands'].append('say')
                    success_msg += "✨ **SPECIAL UNLOCK:** You can now use the `!say` command!"
            
            elif item_data['type'] == 'role':
                # Role was already successfully assigned above during validation
                try:
                    role = discord.utils.get(ctx.guild.roles, name=item_data['role_name'])
                    if role and hasattr(role, 'name'):
                        success_msg += f"👑 **ROLE GRANTED:** You now have the **{role.name}** role!\n"
                        success_msg += f"🎨 **Role Color:** {role.color}\n"
                        success_msg += f"📍 **Role Position:** #{len(ctx.guild.roles) - role.position}\n"
                        success_msg += f"🏷️  **Role ID:** {role.id}"
                        
                        # Save role purchase info for future reference
                        if 'purchased_roles' not in user_data_obj:
                            user_data_obj['purchased_roles'] = []
                        user_data_obj['purchased_roles'].append({
                            'role_name': item_data['role_name'],
                            'role_id': role.id,
                            'purchase_date': datetime.now().isoformat(),
                            'guild_id': ctx.guild.id
                        })
                        save_user_data()
                    else:
                        success_msg += f"✅ **Role Assigned:** {item_data['role_name']} role granted!"
                        print(f"⚠️ Role object issue for {item_data['role_name']}: {role}")
                except Exception as e:
                    print(f"❌ Error getting role info: {e}")
                    success_msg += f"✅ **Role Assigned:** {item_data['role_name']} role granted!"
            
            embed = discord.Embed(
                title="✅ Purchase Successful!",
                description=success_msg,
                color=0x00ff00
            )
            await ctx.author.send(embed=embed)
            
        except asyncio.TimeoutError:
            timeout_embed = discord.Embed(
                title="⏰ Purchase Timeout",
                description="Purchase timed out. Please try again.",
                color=0x808080
            )
            await ctx.author.send(embed=timeout_embed)
            
    except discord.Forbidden:
        # Fallback to channel message if DMs are disabled
        try:
            await ctx.send(f"{ctx.author.mention} I tried to send you a private confirmation, but your DMs are disabled. Please enable DMs for private transactions!", delete_after=10)
        except Exception:
            pass
    except Exception as e:
        # Comprehensive error handling for any other issues
        print(f"🚨 Error in buy command: {type(e).__name__}: {e}")
        print(f"   User: {ctx.author} ({ctx.author.id})")
        print(f"   Guild: {ctx.guild.name if ctx.guild else 'DM'}")
        print(f"   Item Number: {item_number}")
        
        error_embed = discord.Embed(
            title="❌ Purchase Error",
            description="An error occurred during your purchase. Please try again or contact an admin.",
            color=0xff0000
        )
        error_embed.add_field(
            name="Troubleshooting Tips",
            value="• Make sure you have enough coins\n• Use `!shop` to see valid items\n• Check if bot has proper permissions",
            inline=False
        )
        
        try:
            await ctx.author.send(embed=error_embed)
        except discord.Forbidden:
            try:
                await ctx.send(embed=error_embed, delete_after=15)
            except Exception:
                pass


# �️ DEBUG AND ADMIN COMMANDS

@bot.command(name='checkperms')
async def check_permissions(ctx):
    """Check bot permissions in the server (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to bot owners only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    bot_member = ctx.guild.get_member(bot.user.id)
    perms = bot_member.guild_permissions
    
    embed = discord.Embed(
        title=f"🤖 Bot Permissions in {ctx.guild.name}",
        color=0x00bfff
    )
    
    # Key permissions for the shop system
    key_perms = {
        'Manage Roles': perms.manage_roles,
        'Send Messages': perms.send_messages,
        'Manage Messages': perms.manage_messages,
        'Embed Links': perms.embed_links,
        'Add Reactions': perms.add_reactions,
        'Read Message History': perms.read_message_history,
        'Administrator': perms.administrator
    }
    
    perm_text = ""
    for perm_name, has_perm in key_perms.items():
        status = "✅" if has_perm else "❌"
        perm_text += f"{status} {perm_name}\n"
    
    embed.add_field(name="Key Permissions", value=perm_text, inline=False)
    
    # Bot role info
    embed.add_field(
        name="Bot Role Info", 
        value=f"**Highest Role:** {bot_member.top_role.name}\n"
              f"**Role Position:** {bot_member.top_role.position}\n"
              f"**Total Roles:** {len(ctx.guild.roles)}", 
        inline=False
    )
    
    # Existing shop roles
    shop_roles = []
    for item_id, item_data in SHOP_ITEMS.items():
        if item_data['type'] == 'role':
            role = discord.utils.get(ctx.guild.roles, name=item_data['role_name'])
            if role:
                shop_roles.append(f"✅ {role.name} (Position: {role.position})")
            else:
                shop_roles.append(f"❌ {item_data['role_name']} (Missing)")
    
    if shop_roles:
        embed.add_field(
            name="Shop Roles Status", 
            value="\n".join(shop_roles), 
            inline=False
        )
    
    await ctx.send(embed=embed)


@bot.command(name='createrole')
async def manual_create_role(ctx, *, role_name):
    """Manually create a shop role for testing (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to bot owners only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    # Check if it's a valid shop role
    valid_roles = [item['role_name'] for item in SHOP_ITEMS.values() if item['type'] == 'role']
    if role_name not in valid_roles:
        embed = discord.Embed(
            title="❌ Invalid Role",
            description=f"Role must be one of: {', '.join(valid_roles)}",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=10)
        return
    
    print(f"🔧 Manual role creation requested: {role_name}")
    role = await get_or_create_role(ctx.guild, role_name)
    
    if role:
        embed = discord.Embed(
            title="✅ Role Created Successfully!",
            description=f"**Role:** {role.name}\n"
                       f"**ID:** {role.id}\n"
                       f"**Color:** {role.color}\n"
                       f"**Position:** {role.position}",
            color=0x00ff00
        )
    else:
        embed = discord.Embed(
            title="❌ Role Creation Failed",
            description="Check console for detailed error information.",
            color=0xff0000
        )
    
    await ctx.send(embed=embed)


# �👑 OWNER-ONLY COIN MANAGEMENT COMMANDS

@bot.command(name='addcoins')
async def add_coins_to_user(ctx, member: discord.Member, amount: int):
    """Add coins to a user (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Invalid Amount",
            description="Amount must be positive!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    user_data_obj = get_user_data(member.id)
    old_balance = user_data_obj['coins']
    user_data_obj['coins'] += amount
    save_user_data()
    
    embed = discord.Embed(
        title="💰 Coins Added Successfully!",
        description=f"**User:** {member.mention}\n"
                   f"**Amount Added:** {amount:,} coins\n"
                   f"**Previous Balance:** {old_balance:,} coins\n"
                   f"**New Balance:** {user_data_obj['coins']:,} coins",
        color=0x00ff00
    )
    await ctx.send(embed=embed)


@bot.command(name='removecoins')
async def remove_coins_from_user(ctx, member: discord.Member, amount: int):
    """Remove coins from a user (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied", 
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    if amount <= 0:
        embed = discord.Embed(
            title="❌ Invalid Amount",
            description="Amount must be positive!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    user_data_obj = get_user_data(member.id)
    old_balance = user_data_obj['coins']
    
    if amount > old_balance:
        embed = discord.Embed(
            title="⚠️ Insufficient Balance",
            description=f"{member.mention} only has {old_balance:,} coins!\n"
                       f"Cannot remove {amount:,} coins.",
            color=0xff9900
        )
        await ctx.send(embed=embed, delete_after=10)
        return
    
    user_data_obj['coins'] -= amount
    save_user_data()
    
    embed = discord.Embed(
        title="💸 Coins Removed Successfully!",
        description=f"**User:** {member.mention}\n"
                   f"**Amount Removed:** {amount:,} coins\n"
                   f"**Previous Balance:** {old_balance:,} coins\n"
                   f"**New Balance:** {user_data_obj['coins']:,} coins",
        color=0xff4500
    )
    await ctx.send(embed=embed)


@bot.command(name='setcoins')
async def set_user_coins(ctx, member: discord.Member, amount: int):
    """Set a user's coins to a specific amount (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    if amount < 0:
        embed = discord.Embed(
            title="❌ Invalid Amount",
            description="Amount cannot be negative!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    user_data_obj = get_user_data(member.id)
    old_balance = user_data_obj['coins']
    user_data_obj['coins'] = amount
    save_user_data()
    
    embed = discord.Embed(
        title="🎯 Coins Set Successfully!",
        description=f"**User:** {member.mention}\n"
                   f"**Previous Balance:** {old_balance:,} coins\n"
                   f"**New Balance:** {amount:,} coins",
        color=0x9932cc
    )
    await ctx.send(embed=embed)


@bot.command(name='resetcoins')
async def reset_user_coins(ctx, member: discord.Member):
    """Reset a user's coins to 0 (OWNER ONLY)"""
    if not is_authorized(ctx.author.id):
        embed = discord.Embed(
            title="🚫 Access Denied",
            description="This command is restricted to the bot owner only!",
            color=0xff0000
        )
        await ctx.send(embed=embed, delete_after=5)
        return
    
    user_data_obj = get_user_data(member.id)
    old_balance = user_data_obj['coins']
    user_data_obj['coins'] = 0
    save_user_data()
    
    embed = discord.Embed(
        title="🔄 Coins Reset Successfully!",
        description=f"**User:** {member.mention}\n"
                   f"**Previous Balance:** {old_balance:,} coins\n"
                   f"**New Balance:** 0 coins",
        color=0x808080
    )
    await ctx.send(embed=embed)


# Help command override
@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(title="🤖 Bot Commands 🤖", color=0x00bfff)
    
    # Basic Commands
    embed.add_field(name="**⭐ Basic Commands**", value=(
        "`!ping` - Check if bot is online\n"
        "`!help` - Show this help menu\n"
        "`!joke` - Get a random joke\n"
        "`!compliment @user` - Give someone a compliment\n"
        "`!meme` - Get a random meme\n"
        "`!fact` - Get a random fact"
    ), inline=False)
    
    # Game Commands
    embed.add_field(name="**🎮 Game Commands**", value=(
        "`!rps rock/paper/scissors` - Play rock paper scissors\n"
        "`!guess` - Start number guessing game (1-100)\n"
        "`!quiz` - Answer trivia questions\n"
        "`!wyr` - Would you rather questions"
    ), inline=False)
    
    # Economy Commands
    embed.add_field(name="**💰 Economy Commands**", value=(
        "`!balance [@user]` - Check coin balance\n"
        "`!daily` - Claim daily coins (24h cooldown)\n"
        "`!work` - Work for coins (30m cooldown)\n"
        "`!leaderboard` - See top coin earners\n"
        "`!shop` - Browse the coin shop (private)\n"
        "`!buy <number>` - Purchase shop items"
    ), inline=False)
    
    # Utility Commands
    embed.add_field(name="**🔧 Utility Commands**", value=(
        "`!serverinfo` - Show server information\n"
        "`!userinfo [@user]` - Show user information\n"
        "`!poll \"Question?\" \"Option1\" \"Option2\"` - Create a poll"
    ), inline=False)
    
    # Restricted Commands  
    embed.add_field(name="**🔒 Restricted Commands**", value=(
        "`!roast @user` - Roast someone (owner only)\n"
        "`!say <message>` - Say command (buy unlock in shop!)\n"
        "`!stealth_say <message>` - Say with quick deletion\n"
        "`!stealth_roast @user` - Roast with quick deletion"
    ), inline=False)
    
    # Owner Only Commands
    if is_authorized(ctx.author.id):
        embed.add_field(name="**👑 Owner Only Commands**", value=(
            "`!addcoins @user <amount>` - Give coins to user\n"
            "`!removecoins @user <amount>` - Take coins from user\n"
            "`!setcoins @user <amount>` - Set user's coins\n"
            "`!resetcoins @user` - Reset user's coins to 0"
        ), inline=False)
    
    embed.set_footer(text="💡 You earn coins by using commands! Shop is private (sent to DMs)! 🎉")
    await ctx.send(embed=embed)


# Enhanced error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found! Use `!help` to see available commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Usage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ User not found! Make sure to mention a valid user.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument! Usage: `{ctx.prefix}{ctx.command.name} {ctx.command.signature}`")
    elif isinstance(error, AttributeError):
        print(f"🚨 AttributeError in {ctx.command}: {error}")
        print(f"   Command: {ctx.message.content}")
        print(f"   User: {ctx.author} ({ctx.author.id})")
        print(f"   Guild: {ctx.guild.name if ctx.guild else 'DM'}")
        await ctx.send("❌ Internal error occurred! This has been logged for debugging.")
    elif isinstance(error, commands.CommandInvokeError):
        original_error = error.original
        print(f"🚨 Command Error: {ctx.command}")
        print(f"   Original Error: {original_error}")
        print(f"   Command: {ctx.message.content}")
        print(f"   User: {ctx.author} ({ctx.author.id})")
        
        if isinstance(original_error, AttributeError):
            await ctx.send("❌ Role assignment error! Check bot permissions and try again.")
        else:
            await ctx.send(f"❌ Command failed: {str(original_error)}")
    else:
        print(f"🚨 Unhandled Error: {type(error).__name__}")
        print(f"   Error: {error}")
        print(f"   Command: {ctx.command}")
        print(f"   Content: {ctx.message.content}")
        await ctx.send("❌ An unexpected error occurred! Please try again or contact an admin.")

# Run the bot
if __name__ == "__main__":
    token = os.getenv('DISCORD_BOT_TOKEN')
    if token:
        bot.run(token)
    else:
        print("Error: DISCORD_BOT_TOKEN environment variable not set!")
