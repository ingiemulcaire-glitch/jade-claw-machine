
import os
import random
import sqlite3

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import database
import animation
from prizes import MACHINES


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def is_staff(interaction: discord.Interaction) -> bool:
    return interaction.user.guild_permissions.manage_messages


def machine_details(machine_name):
    """Read a machine's price and prize pool from prizes.py."""
    machine_data = MACHINES[machine_name]

    if isinstance(machine_data, dict):
        price = machine_data.get(
            "price",
            machine_data.get("cost", 0)
        )
        prizes = machine_data.get(
            "prizes",
            machine_data.get("pool", [])
        )
        return price, prizes

    if isinstance(machine_data, (tuple, list)) and len(machine_data) == 2:
        first, second = machine_data

        if isinstance(first, (int, float)):
            return first, second

        if isinstance(second, (int, float)):
            return second, first

    # Supports a machine represented directly by its prize list.
    return 0, machine_data


@bot.event
async def on_ready():
    database.initialize_database()

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as error:
        print(f"Command sync error: {error}")

    print(f"Logged in as {bot.user}")


@bot.tree.command(
    name="ping",
    description="Check whether Matchi is online."
)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🍵 Matchi is awake!")


@bot.tree.command(
    name="prizes",
    description="View the prizes for a claw machine."
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
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return

    price, prize_pool = machine_details(machine.value)

    embed = discord.Embed(
        title=f"🎁 {machine.value}",
        description=(
            f"**Cost:** {price:,} Jade Points\n\n"
            + "\n".join(
                f"• {prize}" for prize in prize_pool
            )
        ),
        color=discord.Color.from_rgb(42, 112, 81)
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


@bot.tree.command(
    name="claw",
    description="Run a claw machine attempt for a member."
)
@app_commands.choices(
    machine=[
        app_commands.Choice(name=name, value=name)
        for name in MACHINES.keys()
    ],
    attempt_type=[
        app_commands.Choice(name="Paid Attempt", value="Paid"),
        app_commands.Choice(name="Bonus Claw", value="Bonus")
    ]
)
async def claw(
    interaction: discord.Interaction,
    member: discord.Member,
    machine: app_commands.Choice[str],
    attempt_type: app_commands.Choice[str]
):
    if not is_staff(interaction):
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return

    _, prize_pool = machine_details(machine.value)

    if not prize_pool:
        await interaction.response.send_message(
            "This machine has no prizes configured.",
            ephemeral=True
        )
        return

    await interaction.response.defer()

    selected_index = random.randrange(len(prize_pool))
    prize_won = prize_pool[selected_index]

    try:
        gif_path = animation.create_claw_gif(
            machine_name=machine.value,
            prizes=prize_pool,
            selected_index=selected_index
        )

        database.save_attempt(
            member_id=member.id,
            member_name=str(member),
            staff_id=interaction.user.id,
            staff_name=str(interaction.user),
            machine=machine.value,
            prize=prize_won,
            attempt_type=attempt_type.value
        )

        embed = discord.Embed(
            title="🍵 Matchi's Jade Claw Machine",
            description=(
                f"**Member:** {member.mention}\n"
                f"**Machine:** {machine.value}\n"
                f"**Attempt:** {attempt_type.name}\n\n"
                f"🎉 **Prize won:** {prize_won}\n\n"
                "Please arrange delivery of the prize!"
            ),
            color=discord.Color.from_rgb(42, 112, 81)
        )

        embed.set_footer(
            text=f"Run by {interaction.user.display_name}"
        )

        file = discord.File(
            gif_path,
            filename="matchi_claw.gif"
        )
        embed.set_image(url="attachment://matchi_claw.gif")

        await interaction.followup.send(
            embed=embed,
            file=file
        )

    except Exception as error:
        print(f"Claw command error: {error}")
        await interaction.followup.send(
            "Something went wrong while running the claw machine. "
            "Check the bot console for details.",
            ephemeral=True
        )


@bot.tree.command(
    name="history",
    description="View recent claw machine attempts."
)
async def history(
    interaction: discord.Interaction,
    member: discord.Member = None
):
    if not is_staff(interaction):
        await interaction.response.send_message(
            "You don't have permission to use this command.",
            ephemeral=True
        )
        return

    try:
        with database.connect() as db:
            if member:
                rows = db.execute(
                    """
                    SELECT member_name, staff_name, machine, prize,
                           attempt_type, delivery_status, created_at
                    FROM attempts
                    WHERE member_id = ?
                    ORDER BY id DESC
                    LIMIT 10
                    """,
                    (str(member.id),)
                ).fetchall()
            else:
                rows = db.execute(
                    """
                    SELECT member_name, staff_name, machine, prize,
                           attempt_type, delivery_status, created_at
                    FROM attempts
                    ORDER BY id DESC
                    LIMIT 10
                    """
                ).fetchall()

        if not rows:
            await interaction.response.send_message(
                "No claw attempts were found.",
                ephemeral=True
            )
            return

        embed = discord.Embed(
            title="📜 Matchi Claw History",
            color=discord.Color.from_rgb(42, 112, 81)
        )

        for row in rows:
            (
                member_name,
                staff_name,
                machine_name,
                prize,
                attempt_type,
                delivery_status,
                created_at
            ) = row

            embed.add_field(
                name=f"{member_name} — {attempt_type}",
                value=(
                    f"**Machine:** {machine_name}\n"
                    f"**Prize:** {prize}\n"
                    f"**Staff:** {staff_name}\n"
                    f"**Delivery:** {delivery_status}\n"
                    f"**Date:** {created_at}"
                ),
                inline=False
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )

    except Exception as error:
        print(f"History command error: {error}")
        await interaction.response.send_message(
            "Couldn't load claw history. Check the bot console.",
            ephemeral=True
        )


if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing. Check your .env file."
    )

bot.run(TOKEN)
