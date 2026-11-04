
import discord
from discord.ext import commands
from discord import app_commands
import os
import random
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


def is_staff(interaction: discord.Interaction):
    return interaction.user.guild_permissions.manage_messages


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
    if not is_staff(interaction):
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


@bot.tree.command(
    name="claw",
    description="Operate a claw machine for a member."
)
@app_commands.choices(
    machine=[
        app_commands.Choice(name=name, value=name)
        for name in MACHINES.keys()
    ]
)
async def claw(
    interaction: discord.Interaction,
    member: discord.Member,
    machine: app_commands.Choice[str],
    points_deducted: bool
):
    if not is_staff(interaction):
        await interaction.response.send_message(
            "🍵 You don't have permission to use this command.",
            ephemeral=True
        )
        return

    if not points_deducted:
        await interaction.response.send_message(
            "🍵 Please deduct the member's Jade Points in the forum before operating the machine.",
            ephemeral=True
        )
        return

    machine_name = machine.value
    machine_data = MACHINES[machine_name]

    prize = random.choice(machine_data["prizes"])

    database.save_attempt(
        member_id=member.id,
        member_name=member.display_name,
        staff_id=interaction.user.id,
        staff_name=interaction.user.display_name,
        machine=machine_name,
        prize=prize,
        attempt_type="Paid"
    )

    embed = discord.Embed(
        title="🍵 Jade Claw Machine",
        description=(
            f"**Member:** {member.mention}\n"
            f"**Machine:** {machine_name}\n\n"
            f"🎁 **Prize won:** {prize}"
        ),
        color=0x83A96B
    )

    embed.set_footer(
        text="Remember to arrange the prize delivery!"
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)
