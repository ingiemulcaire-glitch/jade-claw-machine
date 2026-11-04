from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 800, 600

DARK = (38, 68, 48)
GREEN = (105, 151, 91)
LIGHT = (187, 215, 155)
CREAM = (255, 250, 225)
GOLD = (220, 184, 99)

CAPSULE_COLORS = [
    (244, 218, 155),
    (164, 202, 139),
    (244, 235, 203),
    (132, 177, 119),
    (226, 195, 127),
    (203, 224, 177),
    (242, 224, 180),
    (114, 157, 100),
]


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default()


def prize_position(index, count):
    columns = 8
    cell_w = 69
    cell_h = 47
    start_x = 124
    start_y = 186

    col = index % columns
    row = index // columns

    x = start_x + col * cell_w + cell_w // 2
    y = start_y + row * cell_h + cell_h // 2

    return x, y


def make_frame(machine_name, prizes, selected_index,
               claw_x, claw_y, grabbed=False):
    # Transparent canvas: no solid rectangular background.
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Rounded machine cabinet.
    draw.rounded_rectangle(
        (75, 28, 725, 558),
        radius=48,
        fill=DARK,
        outline=GOLD,
        width=5
    )

    # Rounded top canopy.
    draw.rounded_rectangle(
        (94, 45, 706, 151),
        radius=32,
        fill=GREEN,
        outline=LIGHT,
        width=3
    )

    # Machine title.
    title = "MATCHI'S JADE CLAW"
    box = draw.textbbox((0, 0), title, font=font(27))
    title_w = box[2] - box[0]

    draw.text(
        ((WIDTH - title_w) // 2, 70),
        title,
        font=font(27),
        fill=CREAM
    )

    # Small decorative dots on the canopy.
    for x in (126, 674):
        draw.ellipse(
            (x - 5, 94, x + 5, 104),
            fill=GOLD
        )

    # Glass compartment.
    draw.rounded_rectangle(
        (105, 135, 695, 480),
        radius=25,
        fill=(229, 238, 207),
        outline=LIGHT,
        width=5
    )

    # Subtle glass shine.
    draw.line(
        (126, 159, 126, 286),
        fill=(248, 252, 235),
        width=4
    )

    # All prizes look like mystery capsules.
    # Names, numbers, and prize values are never drawn.
    for index in range(len(prizes)):
        x, y = prize_position(index, len(prizes))

        color = CAPSULE_COLORS[index % len(CAPSULE_COLORS)]
        radius_x = 21
        radius_y = 15

        draw.ellipse(
            (
                x - radius_x,
                y - radius_y,
                x + radius_x,
                y + radius_y
            ),
            fill=color,
            outline=(255, 248, 218),
            width=2
        )

        # Decorative capsule seam.
        draw.line(
            (x - 12, y, x + 12, y),
            fill=(255, 247, 221),
            width=2
        )

        # Gold ring identifies the selected capsule
        # without revealing its prize name.
        if index == selected_index:
            draw.ellipse(
                (
                    x - radius_x - 4,
                    y - radius_y - 4,
                    x + radius_x + 4,
                    y + radius_y + 4
                ),
                outline=GOLD,
                width=3
            )

    # Claw cable and mechanism.
    draw.line(
        (claw_x, 143, claw_x, claw_y),
        fill=(225, 220, 188),
        width=5
    )

    draw.rounded_rectangle(
        (claw_x - 17, claw_y - 9,
         claw_x + 17, claw_y + 9),
        radius=6,
        fill=GOLD,
        outline=DARK,
        width=2
    )

    # Claw prongs.
    if grabbed:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 5, claw_y + 23),
            fill=DARK,
            width=5
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 5, claw_y + 23),
            fill=DARK,
            width=5
        )

        # Capsule held by the claw.
        draw.ellipse(
            (claw_x - 12, claw_y + 18,
             claw_x + 12, claw_y + 36),
            fill=CAPSULE_COLORS[
                selected_index % len(CAPSULE_COLORS)
            ],
            outline=GOLD,
            width=2
        )
    else:
        draw.line(
            (claw_x - 8, claw_y + 5,
             claw_x - 18, claw_y + 22),
            fill=DARK,
            width=5
        )
        draw.line(
            (claw_x + 8, claw_y + 5,
             claw_x + 18, claw_y + 22),
            fill=DARK,
            width=5
        )

    # Rounded collection chute.
    draw.rounded_rectangle(
        (258, 493, 542, 541),
        radius=22,
        fill=GREEN,
        outline=GOLD,
        width=3
    )

    draw.rounded_rectangle(
        (282, 505, 518, 529),
        radius=12,
        fill=DARK
    )

    return image


def to_gif_frame(image):
    # Reserve palette index 255 for transparent pixels.
    rgba = image.convert("RGBA")
    alpha = rgba.getchannel("A")

    frame = rgba.convert("RGB").quantize(
        colors=255,
        method=Image.Quantize.MEDIANCUT
    )

    frame.putpalette(
        frame.getpalette()[:765] + [0, 0, 0]
    )

    pixels = frame.load()
    mask = alpha.load()

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if mask[x, y] < 128:
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

    # Move horizontally toward the selected capsule.
    for step in range(13):
        t = step / 12
        x = round(start_x + (target_x - start_x) * t)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            x, start_y
        ))

    # Lower the claw.
    for step in range(11):
        t = step / 10
        y = round(start_y + (target_y - start_y) * t)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, y
        ))

    # Grab the capsule.
    for _ in range(5):
        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, target_y, grabbed=True
        ))

    # Lift it up.
    for step in range(13):
        t = step / 12
        y = round(target_y + (start_y - target_y) * t)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            target_x, y, grabbed=True
        ))

    # Return to the center.
    for step in range(13):
        t = step / 12
        x = round(target_x + (start_x - target_x) * t)

        frames.append(make_frame(
            machine_name, prizes, selected_index,
            x, start_y, grabbed=True
        ))

    frames.extend([frames[-1].copy() for _ in range(6)])

    gif_frames = [to_gif_frame(frame) for frame in frames]

    output = BytesIO()

    gif_frames[0].save(
        output,
        format="GIF",
        save_all=True,
        append_images=gif_frames[1:],
        duration=65,
        loop=0,
        optimize=False,
        disposal=2,
        transparency=255
    )

    output.seek(0)
    return output

