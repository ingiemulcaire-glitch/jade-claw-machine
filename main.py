import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import database

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.event
async def on_ready():
    print(f"Matchi is online as {bot.user}!")

    database.initialize_database()
    print("Matchi database initialized!")

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as error:
        print(f"Command sync error: {error}")

@bot.tree.command(
    name="ping",
    description="Check if Matchi is responding."
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        "🍵 Matchi is awake!"
    )

if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)
