
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load private environment variables
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

# Bot configuration
intents = discord.Intents.default()
intents.guilds = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Jade Claw Machine is online!")
    print(f"Logged in as: {bot.user}")


@bot.command()
async def ping(ctx):
    await ctx.send("🍵 Jade Claw Machine is awake!")


if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)
