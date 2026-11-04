
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 800, 600
OUTPUT_FILE = "matchi_claw.gif"

GOLD = (218, 177, 91)
GOLD_LIGHT = (255, 230, 165)
JADE_DARK = (8, 43, 34)
GLASS = (12, 31, 27)


def blend(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def gradient(draw, box, top, bottom):
    x1, y1, x2, y2 = box
    height = max(1, y2 - y1)
    for y in range(y1, y2 + 1):
        draw.line(
            (x1, y, x2, y),
            fill=blend(top, bottom, (y - y1) / height)
        )


def draw_capsule(draw, x, y, color, held=False):
    rx, ry = (18, 22) if held else (21, 25)

    draw.ellipse(
        (x-rx+3, y+ry-3, x+rx+4, y+ry+5),
        fill=(5, 17, 14)
    )
    draw.ellipse(
        (x-rx, y-ry, x+rx, y+ry),
        fill=color,
        outline=(241, 220, 162),
        width=2
    )
    draw.line(
        (x-rx+3, y, x+rx-3, y),
        fill=(245, 225, 174),
        width=2
    )
    draw.arc(
        (x-rx+3, y-ry+3, x+rx-3, y+ry-3),
        205, 285, fill=(255, 250, 219), width=3
    )
    draw.ellipse(
        (x-rx+5, y-ry+5, x-rx+11, y-ry+18),
        fill=(238, 255, 240)
    )

    if held:
        draw.ellipse(
            (x-rx-4, y-ry-4, x+rx+4, y+ry+4),
            outline=GOLD_LIGHT, width=3
        )


def draw_background():
    im = Image.new("RGB", (WIDTH, HEIGHT), (7, 23, 19))
    d = ImageDraw.Draw(im)

    gradient(d, (0, 0, WIDTH, HEIGHT),
             (25, 53, 44), (4, 17, 14))

    d.ellipse((120, 25, 690, 590), fill=(15, 39, 32))
    d.ellipse((100, 515, 700, 580), fill=(3, 12, 10))
    d.line((80, 548, 720, 548), fill=(36, 69, 53), width=2)

    return im


def draw_machine():
    im = draw_background()
    d = ImageDraw.Draw(im)

    # Cabinet shadow
    d.ellipse((105, 510, 695, 579), fill=(2, 10, 8))

    # Angled side panel gives the cabinet visible depth
    d.polygon(
        [(600, 77), (660, 105), (660, 492), (600, 519)],
        fill=(8, 46, 35), outline=GOLD
    )
    d.polygon(
        [(615, 113), (645, 126), (645, 470), (615, 485)],
        fill=(12, 65, 48), outline=(119, 91, 48)
    )
    d.line((628, 130, 628, 463), fill=(164, 127, 65), width=2)

    # Outer cabinet and gold bevel
    d.rounded_rectangle(
        (132, 60, 620, 530), radius=34,
        fill=(4, 25, 20), outline=(246, 211, 133), width=5
    )
    d.rounded_rectangle(
        (143, 70, 610, 519), radius=27,
        fill=JADE_DARK, outline=GOLD, width=3
    )
    gradient(d, (151, 80, 601, 510),
             (39, 127, 90), (8, 51, 39))
    d.rounded_rectangle(
        (151, 80, 601, 510), radius=22,
        outline=(240, 205, 118), width=2
    )

    # Blank marquee
    d.rounded_rectangle(
        (179, 89, 573, 143), radius=15,
        fill=(6, 43, 33), outline=GOLD, width=3
    )
    d.rounded_rectangle(
        (188, 97, 564, 135), radius=10,
        outline=(100, 157, 111), width=2
    )
    d.line((205, 101, 547, 101), fill=(86, 148, 106), width=2)

    # Deep glass chamber
    d.rounded_rectangle(
        (170, 151, 581, 420), radius=17,
        fill=GLASS, outline=GOLD, width=4
    )
    d.rounded_rectangle(
        (179, 160, 572, 411), radius=12,
        outline=(91, 143, 111), width=2
    )

    # Reflections across the glass
    d.polygon(
        [(192, 166), (224, 166), (308, 405), (282, 405)],
        fill=(22, 48, 40)
    )
    d.polygon(
        [(526, 164), (548, 164), (484, 406), (466, 406)],
        fill=(18, 43, 36)
    )
    d.line((190, 174, 254, 346), fill=(83, 126, 101), width=2)
    d.line((552, 178, 515, 290), fill=(64, 105, 84), width=2)

    # Capsule platform
    d.rounded_rectangle(
        (183, 366, 568, 405), radius=8,
        fill=(7, 22, 19), outline=(107, 84, 47), width=2
    )
    d.line((190, 371, 561, 371), fill=(67, 101, 75), width=2)

    # Lower control section
    d.rounded_rectangle(
        (170, 429, 581, 500), radius=13,
        fill=(8, 46, 35), outline=GOLD, width=3
    )
    d.line((188, 438, 562, 438), fill=(83, 139, 98), width=2)

    # Joystick panel
    d.rounded_rectangle(
        (194, 446, 319, 483), radius=9,
        fill=(5, 25, 20), outline=(157, 120, 57), width=2
    )
    d.ellipse(
        (211, 453, 239, 479),
        fill=(30, 104, 75), outline=GOLD_LIGHT, width=2
    )
    d.line((225, 466, 239, 451), fill=GOLD_LIGHT, width=4)
    d.ellipse(
        (269, 455, 286, 472),
        fill=(191, 67, 57), outline=(255, 205, 153), width=2
    )
    d.ellipse(
        (291, 455, 308, 472),
        fill=(231, 185, 83), outline=(255, 235, 178), width=2
    )

    # Blank prize-return hatch
    d.rounded_rectangle(
        (407, 446, 550, 486), radius=8,
        fill=(4, 22, 19), outline=GOLD, width=3
    )
    d.rounded_rectangle(
        (418, 453, 539, 478), radius=5,
        outline=(67, 118, 83), width=2
    )

    # Small gold cabinet hardware
    for x, y in [(159, 88), (587, 88), (159, 493), (587, 493)]:
        d.ellipse((x-4, y-4, x+4, y+4), fill=GOLD_LIGHT)

    return im


CAPSULES = [
    (216, 384, (100, 178, 135)),
    (260, 391, (223, 207, 154)),
    (305, 382, (49, 132, 94)),
    (350, 392, (176, 207, 166)),
    (395, 382, (203, 167, 90)),
    (440, 391, (80, 155, 112)),
    (485, 382, (230, 220, 185)),
    (530, 391, (57, 119, 86)),
    (238, 360, (225, 214, 174)),
    (286, 365, (67, 151, 105)),
    (334, 359, (143, 191, 147)),
    (382, 365, (223, 192, 119)),
    (430, 359, (57, 128, 91)),
    (478, 365, (192, 211, 170)),
    (524, 359, (100, 171, 127)),
]


def draw_claw(draw, x, cable_end, closed=False):
    # Overhead carriage
    draw.rounded_rectangle(
        (x-30, 157, x+30, 174), radius=5,
        fill=(7, 22, 19), outline=GOLD, width=2
    )

    # Gold cable
    draw.rounded_rectangle(
        (x-11, 169, x+11, cable_end), radius=4,
        fill=(179, 145, 76), outline=GOLD_LIGHT, width=1
    )
    draw.line(
        (x-4, 173, x-4, cable_end-3),
        fill=(255, 230, 160), width=2
    )

    # Claw hub
    y = cable_end
    draw.ellipse(
        (x-14, y-7, x+14, y+9),
        fill=(232, 192, 99), outline=(255, 233, 165), width=2
    )
    draw.ellipse((x-5, y-3, x+5, y+4), fill=(91, 68, 35))

    if closed:
        left = [(x-8, y+3), (x-18, y+15),
                (x-13, y+27), (x-4, y+29)]
        right = [(x+8, y+3), (x+18, y+15),
                 (x+13, y+27), (x+4, y+29)]
    else:
        left = [(x-8, y+3), (x-25, y+15),
                (x-28, y+31), (x-15, y+34)]
        right = [(x+8, y+3), (x+25, y+15),
                 (x+28, y+31), (x+15, y+34)]

    draw.line(left, fill=(245, 211, 129), width=6, joint="curve")
    draw.line(right, fill=(245, 211, 129), width=6, joint="curve")
    draw.line(left, fill=(255, 238, 180), width=2, joint="curve")
    draw.line(right, fill=(255, 238, 180), width=2, joint="curve")


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def create_claw_gif(machine_name, prizes, selected_index):
    # Function signature stays compatible with the existing main.py.
    base = draw_machine()
    frames = []

    selected_slot = int(selected_index) % len(CAPSULES)
    target_x, target_y, target_color = CAPSULES[selected_slot]

    for frame_no in range(34):
        im = base.copy()
        d = ImageDraw.Draw(im)

        # Move down, grab, lift, and carry the capsule.
        if frame_no < 9:
            t = ease(frame_no / 8)
            claw_x = 375
            claw_y = int(205 + (target_y - 205) * t)
            closed = False
            holding = False

        elif frame_no < 13:
            claw_x = target_x
            claw_y = target_y - 5
            closed = frame_no >= 11
            holding = frame_no >= 12

        elif frame_no < 23:
            t = ease((frame_no - 13) / 9)
            claw_x = target_x
            claw_y = int((target_y - 5) + (225 - (target_y - 5)) * t)
            closed = True
            holding = True

        else:
            t = ease((frame_no - 23) / 10)
            claw_x = int(target_x + (478 - target_x) * t)
            claw_y = 225
            closed = True
            holding = True

        # Draw all capsules except the one being carried.
        for idx, (cx, cy, color) in enumerate(CAPSULES):
            if idx == selected_slot and holding:
                continue
            draw_capsule(d, cx, cy, color)

        # Small reflections inside the chamber
        d.ellipse((198, 184, 204, 190), fill=(180, 221, 178))
        d.ellipse((555, 202, 560, 207), fill=(137, 194, 149))

        draw_claw(d, claw_x, claw_y, closed)

        if holding:
            draw_capsule(
                d, claw_x, claw_y + 42, target_color, held=True
            )

        if frame_no in (12, 13, 14, 22, 23):
            sx, sy = claw_x + 28, claw_y + 28
            d.line((sx-5, sy, sx+5, sy), fill=GOLD_LIGHT, width=2)
            d.line((sx, sy-5, sx, sy+5), fill=GOLD_LIGHT, width=2)

        frames.append(im.convert(
            "P", palette=Image.Palette.ADAPTIVE, colors=128
        ))

    frames[0].save(
        OUTPUT_FILE,
        save_all=True,
        append_images=frames[1:],
        duration=65,
        loop=0,
        optimize=False,
        disposal=2,
    )

    return OUTPUT_FILE
