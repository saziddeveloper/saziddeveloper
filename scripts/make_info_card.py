from pathlib import Path
from html import escape


OUTPUT = Path("info-card.svg")

WIDTH = 900
HEIGHT = 900

BG = "#090909"
PANEL = "#0d0d0d"
BORDER = "#292929"

GOLD = "#D4AF37"
GOLD_DARK = "#8F7727"

TEXT = "#C7C7C7"
MUTED = "#777777"


PROFILE = {
    "name": "Ashaduzzaman Sazid",
    "role": "AI-Powered Full-Stack Software Engineer",
    "location": "Bangladesh",
    "os": "Fedora Linux",

        "frontend": (
        "React • Next.js • TypeScript • JavaScript • Tailwind"
    ),

    "backend": (
        "Node.js • Express.js • REST API"
    ),

    "database": (
        "MongoDB • PostgreSQL • Prisma • MySQL"
    ),

    "ai": (
        "LLMs • RAG • AI Agents • Embeddings • Tool Calling"
    ),

    "cloud": (
        "Vercel • AWS • Docker • GitHub Actions"
    ),

    "tools": (
        "Git • GitHub • VS Code • Postman • npm • Vite"
    ),

    "design": (
        "Figma • Canva"
    ),

    "deployment": (
        "Vercel • Netlify • GitHub Actions"
    ),

    "github": "github.com/saziddeveloper",

    "portfolio": "saziddeveloper.github.io",

    "email": "saziddeveloper@gmail.com",
}


def make_row(
    label,
    value,
    y,
    delay,
):
    """
    Create one animated information row.
    """

    return f"""
    <g
        class="info-row"
        style="animation-delay:{delay:.2f}s"
    >

        <text
            x="55"
            y="{y}"
            class="label"
        >
            {escape(label)}
        </text>

        <text
            x="220"
            y="{y}"
            class="value"
        >
            {escape(value)}
        </text>

    </g>
    """


def create_svg():

    rows = []

    rows.append(
        make_row(
            "NAME",
            PROFILE["name"],
            180,
            0.15,
        )
    )

    rows.append(
        make_row(
            "ROLE",
            PROFILE["role"],
            230,
            0.25,
        )
    )

    rows.append(
        make_row(
            "LOCATION",
            PROFILE["location"],
            280,
            0.35,
        )
    )

    rows.append(
        make_row(
            "OS",
            PROFILE["os"],
            330,
            0.40,
        )
    )

    rows.append(
        make_row(
            "FRONTEND",
            PROFILE["frontend"],
            410,
            0.45,
        )
    )

    rows.append(
        make_row(
            "BACKEND",
            PROFILE["backend"],
            460,
            0.55,
        )
    )

    rows.append(
        make_row(
            "TOOLS",
            PROFILE["tools"],
            510,
            0.65,
        )
    )

    rows.append(
        make_row(
            "DESIGN",
            PROFILE["design"],
            560,
            0.75,
        )
    )

    rows.append(
        make_row(
            "DEPLOY",
            PROFILE["deployment"],
            610,
            0.85,
        )
    )

    rows.append(
        make_row(
            "GITHUB",
            PROFILE["github"],
            700,
            0.95,
        )
    )

    rows.append(
        make_row(
            "PORTFOLIO",
            PROFILE["portfolio"],
            750,
            1.05,
        )
    )

    rows.append(
        make_row(
            "EMAIL",
            PROFILE["email"],
            800,
            1.15,
        )
    )

    rows_html = "\n".join(rows)

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>

<defs>

    <linearGradient
        id="goldLine"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%"
    >

        <stop
            offset="0%"
            stop-color="#6F5B1D"
        />

        <stop
            offset="50%"
            stop-color="{GOLD}"
        />

        <stop
            offset="100%"
            stop-color="#6F5B1D"
        />

    </linearGradient>


    <style>

        .info-row {{
            opacity: 0;

            animation:
                fadeIn
                0.5s
                ease-out
                forwards;
        }}


        .label {{
            fill: {GOLD};

            font-family:
                "DejaVu Sans Mono",
                "Liberation Mono",
                monospace;

            font-size: 16px;

            font-weight: 700;

            letter-spacing: 1px;
        }}


        .value {{
            fill: {TEXT};

            font-family:
                "DejaVu Sans Mono",
                "Liberation Mono",
                monospace;

            font-size: 15px;

            font-weight: 400;
        }}


        @keyframes fadeIn {{

            from {{
                opacity: 0;
                transform:
                    translateY(6px);
            }}

            to {{
                opacity: 1;
                transform:
                    translateY(0);
            }}

        }}

    </style>

</defs>


<!-- Main terminal -->

<rect
    x="1"
    y="1"
    width="898"
    height="898"
    rx="28"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="2"
/>


<!-- Inner panel -->

<rect
    x="14"
    y="14"
    width="872"
    height="872"
    rx="20"
    fill="{PANEL}"
/>


<!-- Terminal buttons -->

<circle
    cx="34"
    cy="34"
    r="7"
    fill="#ff5f57"
/>

<circle
    cx="58"
    cy="34"
    r="7"
    fill="#febc2e"
/>

<circle
    cx="82"
    cy="34"
    r="7"
    fill="#28c840"
/>


<!-- Terminal title -->

<text
    x="112"
    y="40"
    fill="{TEXT}"
    font-family="monospace"
    font-size="17"
    letter-spacing="1"
>
    SAZIDDEVELOER
</text>


<text
    x="755"
    y="40"
    fill="{GOLD_DARK}"
    font-family="monospace"
    font-size="11"
>
    SYSTEM.INFO
</text>


<!-- Separator -->

<line
    x1="30"
    y1="65"
    x2="870"
    y2="65"
    stroke="{BORDER}"
/>


<!-- Command -->

<text
    x="55"
    y="105"
    fill="{GOLD}"
    font-family="monospace"
    font-size="15"
>
    $ fedora
</text>


<text
    x="55"
    y="130"
    fill="{MUTED}"
    font-family="monospace"
    font-size="12"
>
    saziddeveloper.profile
</text>


<!-- Information -->

{rows_html}


<!-- Bottom status -->

<line
    x1="30"
    y1="850"
    x2="870"
    y2="850"
    stroke="{BORDER}"
/>


<text
    x="55"
    y="878"
    fill="{MUTED}"
    font-family="monospace"
    font-size="11"
>
    STATUS
</text>


<text
    x="110"
    y="878"
    fill="{GOLD}"
    font-family="monospace"
    font-size="11"
>
    ONLINE
</text>


<text
    x="720"
    y="878"
    fill="{MUTED}"
    font-family="monospace"
    font-size="11"
>
    v1.0.0
</text>


</svg>
"""


def main():

    print("====================================")
    print("       INFO CARD GENERATOR")
    print("====================================")

    print("Generating profile information...")

    svg = create_svg()

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    main()