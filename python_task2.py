import discord
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz
import random
import json
from youtube_dl import YoutubeDL

intents = discord.Intents.default()
intents.members = True  # Required for welcoming new members
client = commands.Bot(command_prefix="!", intents=intents)

# Data structures for reminders and polls
reminders = []
polls = {}

# Music-related variables
music_queue = []
is_playing = False

# Function to get current time in UTC
def get_utc_time():
    return datetime.datetime.now(pytz.utc)

# --- Helper Functions ---
def check_time_format(time_str):
    try:
        # Try to parse the time in a specific format
        return datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return None

# --- Reminder Functions ---
@tasks.loop(seconds=60)
async def check_reminders():
    now = get_utc_time()
    for reminder in reminders[:]:
        if reminder['time'] <= now:
            user = client.get_user(reminder['user_id'])
            await user.send(f"Reminder: {reminder['message']}")
            reminders.remove(reminder)

@client.command()
async def setreminder(ctx, time: str, *, message: str):
    reminder_time = check_time_format(time)
    if not reminder_time:
        await ctx.send("Invalid time format. Please use the format YYYY-MM-DD HH:MM:SS.")
        return

    reminder = {'user_id': ctx.author.id, 'time': reminder_time, 'message': message}
    reminders.append(reminder)
    await ctx.send(f"Reminder set for {reminder_time.strftime('%Y-%m-%d %H:%M:%S')}.")
    check_reminders.start()

# --- Poll Functions ---
@client.command()
async def createpoll(ctx, *options):
    if len(options) < 2:
        await ctx.send("You need at least two options for a poll.")
        return
    
    poll_id = random.randint(1000, 9999)
    polls[poll_id] = {"options": options, "votes": {option: 0 for option in options}}
    
    poll_message = f"Poll ID: {poll_id}\n"
    for idx, option in enumerate(options, 1):
        poll_message += f"{idx}. {option}\n"
    
    poll_message += "Use `!vote <poll_id> <option_number>` to vote."
    await ctx.send(poll_message)

@client.command()
async def vote(ctx, poll_id: int, option_number: int):
    if poll_id not in polls:
        await ctx.send("Poll ID not found.")
        return
    
    poll = polls[poll_id]
    if option_number < 1 or option_number > len(poll['options']):
        await ctx.send("Invalid option number.")
        return
    
    selected_option = poll['options'][option_number - 1]
    poll['votes'][selected_option] += 1
    
    await ctx.send(f"You voted for: {selected_option}")

# --- AI Summary Functionality ---
@client.command()
async def summarize(ctx, *, message: str):
    # This is a placeholder for AI-powered summarization, you can integrate Gemini API here
    summary = message[:50] + "..." if len(message) > 50 else message
    await ctx.send(f"Summary: {summary}")

# --- Music Functions ---
@client.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("You need to join a voice channel first.")

@client.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("I'm not connected to any voice channel.")

@client.command()
async def play(ctx, url: str):
    if not ctx.voice_client:
        await ctx.send("I need to be in a voice channel first!")
        return
    
    # Use youtube-dl to fetch the audio URL
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegAudioConvertor',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url2 = info['formats'][0]['url']
        voice = ctx.voice_client
        voice.play(discord.FFmpegPCMAudio(url2))

@client.command()
async def queue(ctx):
    if music_queue:
        await ctx.send("Music Queue:\n" + "\n".join(music_queue))
    else:
        await ctx.send("The queue is empty.")

@client.command()
async def skip(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Skipped the current song.")
    else:
        await ctx.send("No song is currently playing.")

# --- Welcome Message ---
@client.event
async def on_member_join(member):
    await member.send(f"Welcome to the server, {member.name}! Enjoy your stay!")

# --- Error Handling ---
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

# --- Run the Bot ---
client.run('YOUR_BOT_TOKEN')
