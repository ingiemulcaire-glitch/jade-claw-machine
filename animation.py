
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import math

WIDTH, HEIGHT = 800, 600

# Luxury jade and gold palette
DARK = (20, 43, 31, 255)
FOREST = (32, 70, 47, 255)
EMERALD = (43, 94, 60, 255)
JADE = (77, 127, 77, 255)
LIGHT_JADE = (139, 177, 115, 255)
CREAM = (255, 249, 229, 255)
GOLD = (218, 177, 91, 255)
PALE_GOLD = (255, 231, 168, 255)
GLASS = (239, 246, 224, 255)

CAPSULES = [
    (240, 211, 143, 255),
    (153, 192, 126, 255),
    (250, 239, 209, 255),
    (108, 151, 91, 255),
    (226, 190, 111, 255),
    (193, 216, 167, 255),
    (244, 222, 174, 255),
    (84, 127, 77, 255),
]


def get_font(size, bold=False):
    try:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
        return ImageFont.truetype(name, size)
    except OSError:
        return ImageFont.load_default()


def gradient_panel(image, bounds, top, bottom, radius,
                   outline=None, outline_width=1):
    x1, y1, x2, y2 = bounds
    width = x2 - x1
    height = y2 - y1

    panel = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    pixels = panel.load()

    for y in range(height):
        t = y / max(1, height - 1)
        colour = tuple(
            round(top[i] * (1 - t) + bottom[i] * t)
            for i in range(3)
        ) + (255,)

        for x in range(width):
            pixels[x, y] = colour

    mask = Image.new("L", (width, height), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, width - 1, height - 1),
        radius=radius,
        fill=255
    )
    panel.putalpha(mask)
    image.alpha_composite(panel, (x1, y1))

    if outline:
        ImageDraw.Draw(image).rounded_rectangle(
            bounds,
            radius=radius,
            outline=outline,
            width=outline_width
        )


def prize_position(index, count):
    columns = 8
    cell_w = 69
    cell_h = 47
    start_x = 124
    start_y = 186

    return (
        start_x + (index % columns) * cell_w + cell_w // 2,
        start_y + (index // columns) * cell_h + cell_h // 2
    )


def draw_capsule(draw, x, y, colour):
    # Subtle shadow
    draw.ellipse(
        (x - 20, y - 9, x + 23, y + 19),
        fill=(35, 47, 29, 65)
    )

    # Glossy capsule
    draw.ellipse(
        (x - 21, y - 16, x + 21, y + 16),
        fill=colour,
        outline=CREAM,
        width=2
    )

    # Capsule seam and reflection
    draw.line(
        (x, y - 13, x, y + 13),
        fill=(255, 247, 220, 220),
        width=2
    )

    draw.arc(
        (x - 15, y - 13, x + 9, y + 8),
        start=195,
        end=285,
        fill=(255, 255, 245, 255),
        width=3
    )


def make_frame(machine_name, prizes, selected_index,
               claw_x, claw_y, grabbed=False):
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Soft shadow below the machine
    draw.ellipse(
        (125, 532, 675, 570),
        fill=(10, 20, 12, 85)
    )

    # Main cabinet
    gradient_panel(
        image,
        (75, 28, 725, 558),
        (74, 124, 75),
        (19, 43, 29),
        48,
        GOLD,
        5
    )

    draw = ImageDraw.Draw(image)

    # Fine inner gold border
    draw.rounded_rectangle(
        (84, 37, 716, 549),
        radius=41,
        outline=(239, 211, 143, 210),
        width=2
    )

    # Header
    gradient_panel(
        image,
        (96, 46, 704, 151),
        (82, 139, 83),
        (34, 76, 46),
        29,
        PALE_GOLD,
        2
    )

    draw = ImageDraw.Draw(image)

    # Reflected light on the header
    draw.arc(
        (111, 51, 689, 130),
        195, 345,
        fill=(222, 241, 190, 180),
        width=3
    )

    title = "MATCHI'S JADE CLAW"
    title_font = get_font(27, bold=True)
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]

    draw.text(
        ((WIDTH - title_width) // 2 + 1, 75 + 2),
        title,
        font=title_font,
        fill=DARK
    )
    draw.text(
        ((WIDTH - title_width) // 2, 75),
        title,
        font=title_font,
        fill=CREAM,
        stroke_width=1,
        stroke_fill=PALE_GOLD
    )

    # Gold corner studs
    for x in (126, 674):
        draw.ellipse(
            (x - 6, 112, x + 6, 124),
            fill=GOLD,
            outline=CREAM,
            width=1
        )

    # Window frame
    draw.rounded_rectangle(
        (100, 130, 700, 485),
        radius=28,
        fill=DARK,
        outline=GOLD,
        width=3
    )

    # Glass interior
    gradient_panel(
        image,
        (108, 138, 692, 477),
        (242, 248, 225),
        (200, 219, 176),
        22,
        (178, 202, 147, 255),
        2
    )

    draw = ImageDraw.Draw(image)

    # Glass reflections
    draw.line(
        (129, 158, 129, 266),
        fill=(255, 255, 250, 190),
        width=4
    )
    draw.line(
        (139, 158, 139, 218),
        fill=(255, 255, 255, 120),
        width=2
    )
    draw.arc(
        (128, 146, 668, 463),
        200, 265,
        fill=(255, 255, 255, 115),
        width=3
    )

    # Capsules have no visible prize names or numbers
    for i in range(len(prizes)):
        x, y = prize_position(i, len(prizes))
        draw_capsule(draw, x, y, CAPSULES[i % len(CAPSULES)])

    # Claw cable
    draw.line(
        (claw_x, 143, claw_x, claw_y),
        fill=DARK,
        width=8
    )
    draw.line(
        (claw_x - 2, 145, claw_x - 2, claw_y),
        fill=PALE_GOLD,
        width=3
    )

    # Gold claw mechanism
    draw.rounded_rectangle(
        (claw_x - 18, claw_y - 12,
         claw_x + 18, claw_y + 10),
        radius=7,
        fill=GOLD,
        outline=DARK,
        width=2
    )
    draw.line(
        (claw_x - 8, claw_y - 7,
         claw_x + 8, claw_y - 7),
        fill=CREAM,
        width=2
    )

    if grabbed:
        # Closed claw carrying the winning capsule
        draw.line(
            (claw_x - 7, claw_y + 5,
             claw_x - 5, claw_y + 23),
            fill=GOLD,
            width=6
        )
        draw.line(
            (claw_x + 7, claw_y + 5,
             claw_x + 5, claw_y + 23),
            fill=GOLD,
            width=6
        )

        colour = CAPSULES[selected_index % len(CAPSULES)]
        draw_capsule(draw, claw_x, claw_y + 31, colour)
    else:
        # Open claw
        draw.line(
            (claw_x - 7, claw_y + 5,
             claw_x - 18, claw_y + 22),
            fill=GOLD,
            width=5
        )
        draw.line(
            (claw_x + 7, claw_y + 5,
             claw_x + 18, claw_y + 22),
            fill=GOLD,
            width=5
        )

    # Prize collection slot
    gradient_panel(
        image,
        (258, 493, 542, 541),
        (89, 143, 82),
        (29, 67, 41),
        21,
        GOLD,
        3
    )

    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (282, 505, 518, 529),
        radius=12,
        fill=DARK,
        outline=JADE,
        width=2
    )
    draw.line(
        (302, 509, 498, 509),
        fill=(157, 190, 124, 180),
        width=2
    )

    return image


def to_gif_frame(image):
    # Use a reserved palette index for transparent pixels.
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")

    rgb = Image.new("RGB", rgba.size, (0, 0, 0))
    rgb.paste(rgba, mask=alpha)

    frame = rgb.quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )

    palette = frame.getpalette()
    frame.putpalette(palette[:765] + [0, 0, 0])

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

    # Smooth horizontal movement
    for step in range(17):
        t = step / 16
        eased = (1 - math.cos(math.pi * t)) / 2
        x = round(start_x + (target_x - start_x) * eased)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            x, start_y
        ))

    # Lower the claw
    for step in range(13):
        t = step / 12
        eased = t * t * (3 - 2 * t)
        y = round(start_y + (target_y - start_y) * eased)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, y
        ))

    # Grab the capsule
    for _ in range(5):
        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, target_y, grabbed=True
        ))

    # Lift the capsule
    for step in range(13):
        t = step / 12
        eased = t * t * (3 - 2 * t)
        y = round(target_y + (start_y - target_y) * eased)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, y, grabbed=True
        ))

    # Return to the centre
    for step in range(17):
        t = step / 16
        eased = (1 - math.cos(math.pi * t)) / 2
        x = round(target_x + (start_x - target_x) * eased)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            x, start_y, grabbed=True
        ))

    # Hold the final pose briefly
    frames.extend([frames[-1].copy() for _ in range(8)])

    gif_frames = [to_gif_frame(frame) for frame in frames]
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
