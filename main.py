
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Matchi is online as {bot.user}!")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    print(f"Message received: {message.content}")

    await bot.process_commands(message)

@bot.command()
async def ping(ctx):
    print("Ping command detected!")
    await ctx.send("🍵 Matchi is awake!")

bot.run(TOKEN)

