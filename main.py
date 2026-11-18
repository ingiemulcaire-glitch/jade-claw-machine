import os
import random

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

import database
import animation
from prizes import MACHINES


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Only members with this Discord role can use Matchi commands.
HQ_ROLE_ID = 1546538861578944602

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


def is_staff(interaction: discord.Interaction) -> bool:
    """Return True only if the user has the HQ role."""
    if not isinstance(interaction.user, discord.Member):
        return False

    return any(role.id == HQ_ROLE_ID for role in interaction.user.roles)


async def require_hq(interaction: discord.Interaction) -> bool:
    """Block anyone who does not have the HQ role."""
    if not is_staff(interaction):
        message = "🍵 Only members with the @HQ role can use Matchi commands."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)
        return False

    return True


def machine_details(machine_name):
    """Read a machine's price and prize pool from prizes.py."""
    machine_data = MACHINES[machine_name]

    if isinstance(machine_data, dict):
        price = machine_data.get("price", machine_data.get("cost", 0))
        prizes = machine_data.get("prizes", machine_data.get("pool", []))
        return price, prizes

    if isinstance(machine_data, (tuple, list)) and len(machine_data) == 2:
        first, second = machine_data
        if isinstance(first, (int, float)):
            return first, second
        if isinstance(second, (int, float)):
            return second, first

    # Supports a machine represented directly by its prize list.
    return 0, machine_data


def build_result_embed(
    member: discord.Member,
    machine_name: str,
    prize_won: str,
    attempt_label: str,
    staff: discord.Member,
) -> discord.Embed:
    """Build the result embed shared by normal claws and free reclaws."""
    embed = discord.Embed(
        title="🍵 Matchi's Jade Claw Machine",
        description=(
            f"**Member:** {member.mention}\n"
            f"**Machine:** {machine_name}\n"
            f"**Attempt:** {attempt_label}\n\n"
            f"🎉 **Prize won:** {prize_won}\n\n"
            "Please arrange delivery of the prize!"
        ),
        color=discord.Color.from_rgb(42, 112, 81),
    )
    embed.set_footer(text=f"Run by {staff.display_name}")
    return embed


async def create_claw_result(
    member: discord.Member,
    machine_name: str,
    attempt_type: str,
    staff: discord.Member,
):
    """Choose a prize, create its GIF, and save this attempt in history."""
    _, prize_pool = machine_details(machine_name)

    if not prize_pool:
        raise ValueError(f"{machine_name} has no prizes configured.")

    selected_index = random.randrange(len(prize_pool))
    prize_won = prize_pool[selected_index]

    gif_path = animation.create_claw_gif(
        machine_name=machine_name,
        prizes=prize_pool,
        selected_index=selected_index,
    )

    # Each claw/reclaw is logged as its own row.
    database.save_attempt(
        member_id=member.id,
        member_name=str(member),
        staff_id=staff.id,
        staff_name=str(staff),
        machine=machine_name,
        prize=prize_won,
        attempt_type=attempt_type,
    )

    embed = build_result_embed(
        member=member,
        machine_name=machine_name,
        prize_won=prize_won,
        attempt_label=attempt_type,
        staff=staff,
    )

    file = discord.File(gif_path, filename="matchi_claw.gif")
    embed.set_image(url="attachment://matchi_claw.gif")
    return embed, file


class ReclawView(discord.ui.View):
    """Unlimited free reclaws, restricted to HQ staff."""

    def __init__(
        self,
        member: discord.Member,
        machine_name: str,
        original_attempt_type: str,
    ):
        # timeout=None keeps the button available while the bot is running.
        super().__init__(timeout=None)
        self.member = member
        self.machine_name = machine_name
        self.original_attempt_type = original_attempt_type
        self._busy = False

    @discord.ui.button(
        label="Reclaw",
        emoji="🍵",
        style=discord.ButtonStyle.success,
        custom_id="jade_claw_machine:reclaw",
    )
    async def reclaw(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button,
    ):
        # Permissions are checked on every click, not just when /claw is run.
        if not await require_hq(interaction):
            return

        if not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "Unable to verify your HQ permissions.",
                ephemeral=True,
            )
            return

        if self._busy:
            await interaction.response.send_message(
                "🍵 Matchi is already running this claw. Please try again in a moment.",
                ephemeral=True,
            )
            return

        self._busy = True
        await interaction.response.defer()

        try:
            embed, file = await create_claw_result(
                member=self.member,
                machine_name=self.machine_name,
                attempt_type="Reclaw (Free)",
                staff=interaction.user,
            )

            # Replace the old GIF/result on the same message. The same button
            # remains underneath, allowing another free reclaw.
            await interaction.edit_original_response(
                embed=embed,
                attachments=[file],
                view=self,
            )
        except Exception as error:
            print(f"Reclaw error: {error}")
            await interaction.followup.send(
                "Something went wrong while reclawing. Check the bot console.",
                ephemeral=True,
            )
        finally:
            self._busy = False


@bot.event
async def on_ready():
    database.initialize_database()

    # Reclaw buttons are attached to each /claw result. Because each button
    # stores that result's member and machine in memory, buttons on messages
    # from before a bot restart will not be recoverable automatically.
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands!")
    except Exception as error:
        print(f"Command sync error: {error}")

    print(f"Logged in as {bot.user}")


@bot.tree.command(
    name="ping",
    description="Check whether Matchi is online.",
)
async def ping(interaction: discord.Interaction):
    if not await require_hq(interaction):
        return

    await interaction.response.send_message(
        "🍵 Matchi is awake!",
        ephemeral=True,
    )


@bot.tree.command(
    name="prizes",
    description="View the prizes for a claw machine.",
)
@app_commands.choices(
    machine=[
        app_commands.Choice(name=name, value=name)
        for name in MACHINES.keys()
    ]
)
async def prizes(
    interaction: discord.Interaction,
    machine: app_commands.Choice[str],
):
    if not await require_hq(interaction):
        return

    price, prize_pool = machine_details(machine.value)
    embed = discord.Embed(
        title=f"🎁 {machine.value}",
        description=(
            f"**Cost:** {price:,} Jade Points\n\n"
            + "\n".join(f"• {prize}" for prize in prize_pool)
        ),
        color=discord.Color.from_rgb(42, 112, 81),
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command(
    name="claw",
    description="Run a claw machine attempt for a member.",
)
@app_commands.choices(
    machine=[
        app_commands.Choice(name=name, value=name)
        for name in MACHINES.keys()
    ],
    attempt_type=[
        app_commands.Choice(name="Paid Attempt", value="Paid"),
        app_commands.Choice(name="Bonus Claw", value="Bonus"),
    ],
)
async def claw(
    interaction: discord.Interaction,
    member: discord.Member,
    machine: app_commands.Choice[str],
    attempt_type: app_commands.Choice[str],
):
    if not await require_hq(interaction):
        return

    _, prize_pool = machine_details(machine.value)
    if not prize_pool:
        await interaction.response.send_message(
            "This machine has no prizes configured.",
            ephemeral=True,
        )
        return

    await interaction.response.defer()

    try:
        embed, file = await create_claw_result(
            member=member,
            machine_name=machine.value,
            attempt_type=attempt_type.value,
            staff=interaction.user,
        )

        view = ReclawView(
            member=member,
            machine_name=machine.value,
            original_attempt_type=attempt_type.value,
        )

        await interaction.followup.send(
            embed=embed,
            file=file,
            view=view,
        )
    except Exception as error:
        print(f"Claw command error: {error}")
        await interaction.followup.send(
            "Something went wrong while running the claw machine. "
            "Check the bot console for details.",
            ephemeral=True,
        )


@bot.tree.command(
    name="history",
    description="View recent claw machine attempts.",
)
async def history(
    interaction: discord.Interaction,
    member: discord.Member = None,
):
    if not await require_hq(interaction):
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
                    (str(member.id),),
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
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="📜 Matchi Claw History",
            color=discord.Color.from_rgb(42, 112, 81),
        )

        for row in rows:
            (
                member_name,
                staff_name,
                machine_name,
                prize,
                attempt_type,
                delivery_status,
                created_at,
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
                inline=False,
            )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True,
        )

    except Exception as error:
        print(f"History command error: {error}")
        message = "Couldn't load claw history. Check the bot console."
        if interaction.response.is_done():
            await interaction.followup.send(message, ephemeral=True)
        else:
            await interaction.response.send_message(message, ephemeral=True)


if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing. Check your .env file.")


bot.run(TOKEN)
