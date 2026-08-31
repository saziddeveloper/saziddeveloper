from pathlib import Path
from PIL import Image

INPUT = Path("source-prepped.png")
OUTPUT = Path("hxni-ascii.svg")

# Dark → bright character density
RAMP = " .:-=+*cs#%@"

# SVG dimensions
WIDTH = 800
HEIGHT = 800

# Character size
CHAR_WIDTH = 7
CHAR_HEIGHT = 12

# Theme
BG = "#0d0d0d"
GOLD = "#EBE1DF"
BORDER = "#3a3a3a"


def brightness_to_char(value):
    """Convert brightness 0-255 into an ASCII character."""
    index = int(value / 256 * len(RAMP))

    if index >= len(RAMP):
        index = len(RAMP) - 1

    return RAMP[index]


def image_to_ascii(image):
    """Convert image pixels into ASCII characters."""

    image = image.convert("L")

    # Keep the ASCII output reasonably sized
    target_width = 110

    aspect_ratio = image.height / image.width

    # Characters are taller than they are wide,
    # so compensate for terminal character proportions.
    target_height = int(target_width * aspect_ratio * 0.5)

    image = image.resize(
        (target_width, target_height)
    )

    pixels = image.load()

    lines = []

    for y in range(target_height):
        line = []

        for x in range(target_width):
            brightness = pixels[x, y]

            char = brightness_to_char(brightness)

            line.append(char)

        lines.append("".join(line))

    return lines


def escape_xml(text):
    """Escape text so it is safe inside SVG."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def create_svg(lines):

    line_height = 12

    top_padding = 80

    content_height = len(lines) * line_height

    svg_height = max(
        HEIGHT,
        content_height + top_padding + 40
    )

    svg_width = WIDTH

    svg_lines = []

    for i, line in enumerate(lines):

        y = top_padding + (i * line_height)

        safe_line = escape_xml(line)

        delay = i * 0.025

        svg_lines.append(
            f"""
            <text
                x="40"
                y="{y}"
                class="ascii-line"
                style="animation-delay:{delay:.3f}s"
            >{safe_line}</text>
            """
        )

    ascii_content = "\n".join(svg_lines)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{svg_width}"
    height="{svg_height}"
    viewBox="0 0 {svg_width} {svg_height}"
>

    <defs>

        <clipPath id="asciiClip">
            <rect
                x="0"
                y="0"
                width="{svg_width}"
                height="{svg_height}"
            >
                <animate
                    attributeName="width"
                    from="0"
                    to="{svg_width}"
                    dur="2.2s"
                    begin="0s"
                    fill="freeze"
                />
            </rect>
        </clipPath>

        <filter id="glow">
            <feGaussianBlur
                stdDeviation="1.5"
                result="blur"
            />

            <feMerge>
                <feMergeNode in="blur"/>
                <feMergeNode in="SourceGraphic"/>
            </feMerge>
        </filter>

    </defs>

    <rect
        width="100%"
        height="100%"
        rx="28"
        fill="{BG}"
        stroke="{BORDER}"
        stroke-width="2"
    />

    <!-- Terminal header -->

    <circle cx="32" cy="32" r="7" fill="#ff5f57"/>
    <circle cx="56" cy="32" r="7" fill="#febc2e"/>
    <circle cx="80" cy="32" r="7" fill="#28c840"/>

    <text
        x="110"
        y="38"
        fill="#888888"
        font-family="monospace"
        font-size="18"
    >
        SAZIDDEVELOPER
    </text>

    <!-- ASCII portrait -->

    <g
        clip-path="url(#asciiClip)"
        filter="url(#glow)"
    >

        <style>
            .ascii-line {{
                fill: {GOLD};
                font-family: "Courier New", monospace;
                font-size: 11px;
                font-weight: 700;
                white-space: pre;
                opacity: 0;
                animation: fin 0.35s ease-out forwards;
            }}

            @keyframes fin {{
                from {{
                    opacity: 0;
                    transform: translateX(-8px);
                }}

                to {{
                    opacity: 1;
                    transform: translateX(0);
                }}
            }}
        </style>

        {ascii_content}

    </g>

</svg>
"""

    return svg


def main():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Cannot find {INPUT}"
        )

    print(f"Loading {INPUT}...")

    image = Image.open(INPUT)

    print("Converting portrait to ASCII...")

    lines = image_to_ascii(image)

    print(
        f"Generated {len(lines)} ASCII lines."
    )

    print(
        f"Writing {OUTPUT}..."
    )

    OUTPUT.write_text(
        create_svg(lines),
        encoding="utf-8"
    )

    print("Done!")
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()