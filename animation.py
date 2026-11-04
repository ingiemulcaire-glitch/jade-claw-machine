from io import BytesIO
import math
import textwrap

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 800, 600
BG = (247, 245, 231)
DARK_GREEN = (44, 76, 53)
MATCHA = (131, 169, 107)
LIGHT_GREEN = (220, 235, 202)
GOLD = (208, 171, 82)
CREAM = (255, 252, 240)
INK = (49, 57, 43)


def get_font(size=16):
    # Uses Pillow's built-in font so no font files are required.
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def centered_text(draw, xy, text, font, fill):
    x, y = xy
    box = draw.textbbox((0, 0), text, font=font)
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.text((x - width / 2, y - height / 2), text,
              font=font, fill=fill)


def short_label(prize, limit=14):
    """Shorten labels to fit inside the machine's prize slots."""
    if len(prize) <= limit:
        return prize
    return prize[:limit - 2] + ".."


def prize_position(index, count):
    # Eight columns; each entry gets its own position, even
    # when multiple entries have the same prize name.
    columns = 8
    cell_w = 85
    cell_h = 47
    start_x = 60
    start_y = 177

    col = index % columns
    row = index // columns

    x = start_x + col * cell_w + cell_w // 2
    y = start_y + row * cell_h + cell_h // 2

    return x, y, start_x + col * cell_w, start_y + row * cell_h


def draw_machine(machine_name, prizes, selected_index,
                 claw_x, claw_y, grabbed=False):
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    # Header
    centered_text(
        draw, (WIDTH // 2, 35),
        "MATCHI'S JADE CLAW MACHINE",
        get_font(25), DARK_GREEN
    )
    centered_text(
        draw, (WIDTH // 2, 70),
        machine_name,
        get_font(20), MATCHA
    )

    # Machine cabinet
    draw.rounded_rectangle(
        (28, 98, 772, 505),
        radius=24, fill=DARK_GREEN, outline=GOLD, width=5
    )

    # Glass window
    draw.rounded_rectangle(
        (48, 120, 752, 472),
        radius=15, fill=CREAM, outline=MATCHA, width=4
    )

    # Prize slots
    for index, prize in enumerate(prizes):
        x, y, left, top = prize_position(index, len(prizes))

        right = left + 81
        bottom = top + 43

        is_selected = index == selected_index
        fill = LIGHT_GREEN if is_selected else (255, 255, 248)
        outline = GOLD if is_selected else (193, 207, 178)
        border_width = 3 if is_selected else 1

        draw.rounded_rectangle(
            (left + 2, top + 2, right - 2, bottom - 2),
            radius=7, fill=fill,
            outline=outline, width=border_width
        )

        # The selected prize is highlighted throughout the animation.
        label = short_label(prize)
        centered_text(
            draw, (x, y - 5), label,
            get_font(9), DARK_GREEN
        )
        centered_text(
            draw, (x, y + 11), f"#{index + 1}",
            get_font(9), MATCHA
        )

    # Claw cable
    draw.line(
        (claw_x, 124, claw_x, claw_y),
        fill=(100, 105, 94), width=4
    )

    # Claw head
    draw.rounded_rectangle(
        (claw_x - 17, claw_y - 8, claw_x + 17, claw_y + 9),
        radius=5, fill=GOLD, outline=DARK_GREEN, width=2
    )

    # Claw prongs open before grabbing, closed afterward.
    if grabbed:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 4, claw_y + 21),
            fill=DARK_GREEN, width=4
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 4, claw_y + 21),
            fill=DARK_GREEN, width=4
        )
        draw.ellipse(
            (claw_x - 8, claw_y + 12,
             claw_x + 8, claw_y + 28),
            fill=MATCHA, outline=DARK_GREEN, width=2
        )
    else:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 16, claw_y + 20),
            fill=DARK_GREEN, width=4
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 16, claw_y + 20),
            fill=DARK_GREEN, width=4
        )

    # Prize collection slot
    draw.rounded_rectangle(
        (270, 516, 530, 570),
        radius=12, fill=LIGHT_GREEN, outline=GOLD, width=3
    )
    centered_text(
        draw, (WIDTH // 2, 543),
        "PRIZE COLLECTION",
        get_font(17), DARK_GREEN
    )

    return image


def create_claw_gif(machine_name, prizes, selected_index):
    """
    Return an animated GIF as a BytesIO object.

    selected_index identifies the exact prize-list entry.
    Duplicate prize names therefore have separate positions.
    """
    if not prizes:
        raise ValueError("The machine has no prizes.")

    if not 0 <= selected_index < len(prizes):
        raise ValueError("Selected prize index is out of range.")

    target_x, target_y, _, _ = prize_position(
        selected_index, len(prizes)
    )

    # Keep the initial claw near the center of the machine.
    start_x = WIDTH // 2
    start_y = 145

    frames = []

    # Move horizontally above the selected prize.
    for step in range(13):
        t = step / 12
        x = round(start_x + (target_x - start_x) * t)
        frame = draw_machine(
            machine_name, prizes, selected_index, x, start_y
        )
        frames.append(frame)

    # Lower the claw toward the exact prize position.
    for step in range(11):
        t = step / 10
        y = round(start_y + (target_y - start_y) * t)
        frame = draw_machine(
            machine_name, prizes, selected_index,
            target_x, y
        )
        frames.append(frame)

    # Grab the selected prize.
    for _ in range(4):
        frame = draw_machine(
            machine_name, prizes, selected_index,
            target_x, target_y, grabbed=True
        )
        frames.append(frame)

    # Lift the prize.
    for step in range(13):
        t = step / 12
        y = round(target_y + (start_y - target_y) * t)
        frame = draw_machine(
            machine_name, prizes, selected_index,
            target_x, y, grabbed=True
        )
        frames.append(frame)

    # Return toward the center with the prize.
    for step in range(13):
        t = step / 12
        x = round(target_x + (start_x - target_x) * t)
        frame = draw_machine(
            machine_name, prizes, selected_index,
            x, start_y, grabbed=True
        )
        frames.append(frame)

    # Final winning frame.
    final_frame = draw_machine(
        machine_name, prizes, selected_index,
        start_x, start_y, grabbed=True
    )
    final_draw = ImageDraw.Draw(final_frame)

    prize_text = prizes[selected_index]
    centered_text(
        final_draw, (WIDTH // 2, 585),
        f"WINNER: {prize_text}",
        get_font(17), DARK_GREEN
    )
    frames.extend([final_frame.copy() for _ in range(8)])

    output = BytesIO()
    frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=65,
        loop=0,
        optimize=False,
        disposal=2
    )
    output.seek(0)
    return output