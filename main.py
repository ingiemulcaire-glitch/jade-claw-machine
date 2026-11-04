
import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

import database
from prizes import MACHINES

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


@bot.tree.command(
    name="prizes",
    description="View a machine's complete prize pool."
)
@app_commands.choices(
    machine=[
        app_commands.Choice(name=name, value=name)
        for name in MACHINES.keys()
    ]
)
async def prizes(
    interaction: discord.Interaction,
    machine: app_commands.Choice[str]
):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(
            "🍵 You don't have permission to use this command.",
            ephemeral=True
        )
        return

    machine_data = MACHINES[machine.value]

    prize_list = "\n".join(
        f"**{index}.** {prize}"
        for index, prize in enumerate(
            machine_data["prizes"], start=1
        )
    )

    embed = discord.Embed(
        title=f"🍵 {machine.value}",
        description=prize_list,
        color=0x83A96B
    )

    embed.add_field(
        name="Machine Price",
        value=f"{machine_data['price']:,} Jade Points",
        inline=True
    )

    embed.add_field(
        name="Prize Entries",
        value=str(len(machine_data["prizes"])),
        inline=True
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)
