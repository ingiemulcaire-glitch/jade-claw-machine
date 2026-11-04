
from io import BytesIO
from PIL import Image, ImageDraw
import math


WIDTH, HEIGHT = 800, 600

TRANSPARENT = (0, 0, 0, 0)
DARK = (27, 53, 39, 255)
FOREST = (43, 78, 52, 255)
JADE = (91, 139, 79, 255)
MATCHA = (137, 177, 108, 255)
PALE = (225, 239, 203, 255)
CREAM = (255, 249, 226, 255)
GOLD = (225, 190, 105, 255)
SHADOW = (20, 35, 25, 100)

CAPSULE_COLORS = [
    (245, 219, 157, 255),
    (164, 202, 139, 255),
    (248, 239, 211, 255),
    (126, 171, 113, 255),
    (226, 193, 122, 255),
    (202, 224, 177, 255),
    (243, 224, 178, 255),
    (105, 151, 91, 255),
]


def prize_position(index, count):
    columns = 8
    cell_w = 69
    cell_h = 47
    start_x = 124
    start_y = 186

    col = index % columns
    row = index // columns

    return (
        start_x + col * cell_w + cell_w // 2,
        start_y + row * cell_h + cell_h // 2
    )


def rounded(draw, coords, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(
        coords,
        radius=radius,
        fill=fill,
        outline=outline,
        width=width
    )


def draw_capsule(draw, x, y, color, highlighted=False):
    # Soft capsule shadow
    draw.ellipse(
        (x - 23, y - 11, x + 23, y + 20),
        fill=(30, 45, 29, 55)
    )

    # Capsule body
    draw.ellipse(
        (x - 21, y - 16, x + 21, y + 16),
        fill=color,
        outline=(255, 248, 220, 255),
        width=2
    )

    # Glossy highlight
    draw.ellipse(
        (x - 12, y - 11, x + 3, y - 3),
        fill=(255, 255, 240, 205)
    )

    # Capsule seam
    draw.line(
        (x, y - 13, x, y + 13),
        fill=(255, 249, 225, 200),
        width=2
    )

    if highlighted:
        draw.ellipse(
            (x - 25, y - 20, x + 25, y + 20),
            outline=GOLD,
            width=3
        )


def make_frame(machine_name, prizes, selected_index,
               claw_x, claw_y, grabbed=False):

    image = Image.new("RGBA", (WIDTH, HEIGHT), TRANSPARENT)
    draw = ImageDraw.Draw(image)

    # Soft shadow behind the machine
    draw.ellipse(
        (115, 525, 685, 575),
        fill=SHADOW
    )

    # Main cabinet
    rounded(
        draw,
        (75, 28, 725, 558),
        48,
        DARK,
        GOLD,
        5
    )

    # Outer glossy edge
    rounded(
        draw,
        (85, 38, 715, 548),
        42,
        FOREST,
        MATCHA,
        3
    )

    # Top panel
    rounded(
        draw,
        (96, 47, 704, 151),
        31,
        JADE,
        GOLD,
        3
    )

    # Decorative shine on top panel
    draw.arc(
        (112, 53, 688, 130),
        190,
        340,
        fill=(225, 245, 196, 170),
        width=4
    )

    # Header text
    title = "MATCHI'S JADE CLAW"
    try:
        from PIL import ImageFont
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 27)
    except OSError:
        title_font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]

    draw.text(
        ((WIDTH - title_width) // 2, 75),
        title,
        font=title_font,
        fill=CREAM,
        stroke_width=1,
        stroke_fill=FOREST
    )

    # Gold corner ornaments
    for x in (126, 674):
        draw.ellipse(
            (x - 7, 94, x + 7, 108),
            fill=GOLD,
            outline=CREAM,
            width=2
        )

    # Glass window shadow
    rounded(
        draw,
        (101, 132, 699, 484),
        28,
        DARK
    )

    # Glass window
    rounded(
        draw,
        (108, 138, 692, 477),
        23,
        PALE,
        MATCHA,
        4
    )

    # Subtle glass reflections
    draw.line(
        (130, 158, 130, 270),
        fill=(255, 255, 245, 170),
        width=5
    )
    draw.line(
        (140, 158, 140, 225),
        fill=(255, 255, 255, 100),
        width=2
    )

    draw.arc(
        (130, 145, 675, 465),
        195,
        280,
        fill=(255, 255, 255, 95),
        width=3
    )

    # Prize capsules: no text, labels, or numbers
    for index in range(len(prizes)):
        x, y = prize_position(index, len(prizes))
        color = CAPSULE_COLORS[index % len(CAPSULE_COLORS)]
        draw_capsule(draw, x, y, color)

    # Claw cable
    draw.line(
        (claw_x, 143, claw_x, claw_y),
        fill=(255, 247, 214, 255),
        width=7
    )
    draw.line(
        (claw_x - 2, 145, claw_x - 2, claw_y - 2),
        fill=(172, 145, 84, 255),
        width=2
    )

    # Claw head
    rounded(
        draw,
        (claw_x - 20, claw_y - 12,
         claw_x + 20, claw_y + 10),
        8,
        GOLD,
        CREAM,
        2
    )

    draw.ellipse(
        (claw_x - 7, claw_y - 8,
         claw_x + 7, claw_y + 4),
        fill=CREAM
    )

    # Claw arms
    if grabbed:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 6, claw_y + 24),
            fill=GOLD,
            width=6
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 6, claw_y + 24),
            fill=GOLD,
            width=6
        )

        capsule_color = CAPSULE_COLORS[
            selected_index % len(CAPSULE_COLORS)
        ]

        draw.ellipse(
            (claw_x - 13, claw_y + 17,
             claw_x + 13, claw_y + 39),
            fill=capsule_color,
            outline=GOLD,
            width=2
        )
        draw.ellipse(
            (claw_x - 8, claw_y + 20,
             claw_x - 1, claw_y + 25),
            fill=CREAM
        )
    else:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 19, claw_y + 22),
            fill=GOLD,
            width=6
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 19, claw_y + 22),
            fill=GOLD,
            width=6
        )

    # Bottom prize collection slot
    rounded(
        draw,
        (258, 493, 542, 541),
        22,
        JADE,
        GOLD,
        3
    )

    rounded(
        draw,
        (282, 505, 518, 529),
        12,
        DARK
    )

    # Small glossy reflection on collection slot
    draw.line(
        (301, 509, 499, 509),
        fill=(255, 255, 235, 100),
        width=2
    )

    # Small decorative gold dots
    for x in (113, 687):
        for y in (169, 458):
            draw.ellipse(
                (x - 3, y - 3, x + 3, y + 3),
                fill=GOLD
            )

    return image


def to_gif_frame(image):
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")

    # Reserve palette index 255 for transparency
    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba, mask=alpha)

    frame = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )

    palette = frame.getpalette()
    palette = palette[:765] + [0, 0, 0]
    frame.putpalette(palette)

    pixels = frame.load()
    alpha_pixels = alpha.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if alpha_pixels[x, y] < 128:
                pixels[x, y] = 255

    return frame


def create_claw_gif(machine_name, prizes, selected_index):
    if not prizes:
        raise ValueError("This machine has no prizes.")

    if not 0 <= selected_index < len(prizes):
        raise ValueError("Invalid prize position.")

    target_x, target_y = prize_position(
        selected_index, len(prizes)
    )

    start_x = WIDTH // 2
    start_y = 160

    frames = []

    # Move the claw horizontally
    for step in range(19):
        t = step / 18
        eased = (1 - math.cos(math.pi * t)) / 2
        x = round(start_x + (target_x - start_x) * eased)

        frames.append(
            make_frame(
                machine_name, prizes, selected_index,
                x, start_y
            )
        )

    # Lower the claw
    for step in range(15):
        t = step / 14
        eased = t * t
        y = round(start_y + (target_y - start_y) * eased)

        frames.append(
            make_frame(
                machine_name, prizes, selected_index,
                target_x, y
            )
        )

    # Grab the capsule
    for _ in range(6):
        frames.append(
            make_frame(
                machine_name, prizes, selected_index,
                target_x, target_y, grabbed=True
            )
        )

    # Lift the capsule
    for step in range(15):
        t = step / 14
        eased = t * t
        y = round(target_y + (start_y - target_y) * eased)

        frames.append(
            make_frame(
                machine_name, prizes, selected_index,
                target_x, y, grabbed=True
            )
        )

    # Return to the center
    for step in range(19):
        t = step / 18
        eased = (1 - math.cos(math.pi * t)) / 2
        x = round(target_x + (start_x - target_x) * eased)

        frames.append(
            make_frame(
                machine_name, prizes, selected_index,
                x, start_y, grabbed=True
            )
        )

    # Pause at the end
    frames.extend([frames[-1].copy() for _ in range(8)])

    gif_frames = [
        to_gif_frame(frame)
        for frame in frames
    ]

    output = BytesIO()

    gif_frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=55,
        loop=0,
        optimize=False,
        disposal=2,
        transparency=255
    )

    output.seek(0)
    return output


