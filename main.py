
import discord
from discord.ext import commands
from discord import app_commands
import os
import random
from datetime import datetime
from dotenv import load_dotenv

import database
import animation
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
            "🍵 Deduct the member's Jade Points in the forum before operating the machine.",
            ephemeral=True
        )
        return

    # Acknowledge the interaction before generating the GIF.
    await interaction.response.defer(
        ephemeral=True,
        thinking=True
    )

    machine_name = machine.value
    prize_pool = MACHINES[machine_name]["prizes"]

    if not prize_pool:
        await interaction.followup.send(
            "🍵 This machine has no prizes configured.",
            ephemeral=True
        )
        return

    # Select the exact prize entry before creating the animation.
    prize_index = random.randrange(len(prize_pool))
    prize = prize_pool[prize_index]

    # Generate the animated GIF.
    try:
        gif_buffer = animation.create_claw_gif(
            machine_name=machine_name,
            prizes=prize_pool,
            selected_index=prize_index
        )
    except Exception as error:
        print(f"Animation generation error: {error}")
        await interaction.followup.send(
            "🍵 The claw animation couldn't be generated. "
            "No attempt was recorded. Please try again.",
            ephemeral=True
        )
        return

    # Record the attempt after successful animation generation.
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

    embed.set_image(url="attachment://matchi_claw.gif")
    embed.set_footer(
        text="Remember to arrange the prize in the member's ticket!"
    )

    gif_file = discord.File(
        gif_buffer,
        filename="matchi_claw.gif"
    )

    await interaction.followup.send(
        embed=embed,
        file=gif_file,
        ephemeral=True
    )


@bot.tree.command(
    name="history",
    description="View previous Jade Claw Machine attempts."
)
@app_commands.describe(
    member="Optional: view attempts for one member."
)
async def history(
    interaction: discord.Interaction,
    member: discord.Member = None
):
    if not is_staff(interaction):
        await interaction.response.send_message(
            "🍵 You don't have permission to use this command.",
            ephemeral=True
        )
        return

    with database.connect() as db:
        if member is None:
            rows = db.execute("""
                SELECT member_name, staff_name, machine,
                       prize, attempt_type, created_at
                FROM attempts
                ORDER BY id DESC
                LIMIT 10
            """).fetchall()
        else:
            rows = db.execute("""
                SELECT member_name, staff_name, machine,
                       prize, attempt_type, created_at
                FROM attempts
                WHERE member_id = ?
                ORDER BY id DESC
                LIMIT 10
            """, (str(member.id),)).fetchall()

    if not rows:
        await interaction.response.send_message(
            "🍵 No claw attempts were found.",
            ephemeral=True
        )
        return

    embed = discord.Embed(
        title="📜 Jade Claw Machine History",
        description=(
            f"Showing the latest 10 attempts for {member.mention}."
            if member else
            "Showing the latest 10 attempts across all members."
        ),
        color=0x83A96B
    )

    for (
        member_name,
        staff_name,
        machine_name,
        prize,
        attempt_type,
        created_at
    ) in rows:
        try:
            date_text = datetime.fromisoformat(
                created_at
            ).strftime("%b %d, %Y • %I:%M %p UTC")
        except (ValueError, TypeError):
            date_text = str(created_at)

        embed.add_field(
            name=f"🎁 {member_name} — {prize}",
            value=(
                f"**Machine:** {machine_name}\n"
                f"**Operated by:** {staff_name}\n"
                f"**Attempt:** {attempt_type}\n"
                f"**Date:** {date_text}"
            ),
            inline=False
        )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


if TOKEN is None:
    raise ValueError("DISCORD_TOKEN is missing!")

bot.run(TOKEN)
