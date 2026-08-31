from pathlib import Path
from datetime import date
import json
import math
import html


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

WIDTH = 1200
HEIGHT = 430

BG = "#090909"
PANEL = "#0d0d0d"
BORDER = "#292929"

TEXT = "#B8B8B8"
MUTED = "#666666"

GOLD_1 = "#17140B"
GOLD_2 = "#51451C"
GOLD_3 = "#8F7727"
GOLD_4 = "#D4AF37"


def load_data():

    if not INPUT.exists():
        raise FileNotFoundError(
            f"Cannot find {INPUT}"
        )

    with INPUT.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def contribution_color(count, maximum):

    if count <= 0:
        return GOLD_1

    if maximum <= 0:
        return GOLD_1

    ratio = count / maximum

    if ratio < 0.25:
        return GOLD_2

    if ratio < 0.50:
        return GOLD_3

    return GOLD_4


def create_cells(contributions):

    cell_size = 13
    gap = 4

    left = 70
    top = 115

    columns = 53

    maximum = max(
        (
            item["count"]
            for item in contributions
        ),
        default=1
    )

    # Convert dates into a dictionary.
    by_date = {
        item["date"]: item
        for item in contributions
    }

    today = date.today()

    # GitHub calendar: approximately one year.
    start = today

    # Move backward until Sunday.
    start = start.replace(
        day=start.day
    )

    while start.weekday() != 6:
        start = start.fromordinal(
            start.toordinal() - 1
        )

    # One year of weeks.
    first_day = start.fromordinal(
        start.toordinal()
        - (columns * 7 - 1)
    )

    cells = []

    for index in range(columns * 7):

        current = first_day.fromordinal(
            first_day.toordinal() + index
        )

        item = by_date.get(
            current.isoformat(),
            {
                "count": 0,
                "level": 0
            }
        )

        count = item["count"]

        week = index // 7
        weekday = index % 7

        x = (
            left
            + week * (cell_size + gap)
        )

        y = (
            top
            + weekday * (cell_size + gap)
        )

        fill = contribution_color(
            count,
            maximum
        )

        tooltip = (
            f"{current.isoformat()} — "
            f"{count} contributions"
        )

        cells.append(
            f"""
            <g>
                <title>
                    {html.escape(tooltip)}
                </title>

                <rect
                    x="{x}"
                    y="{y}"
                    width="{cell_size}"
                    height="{cell_size}"
                    rx="3"
                    fill="{fill}"
                    class="cell"
                >
                    <animate
                        attributeName="opacity"
                        from="0"
                        to="1"
                        dur="0.4s"
                        begin="{index * 0.004:.3f}s"
                        fill="freeze"
                    />
                </rect>
            </g>
            """
        )

    return "\n".join(cells)


def month_labels():

    labels = []

    left = 70
    top = 95

    cell_size = 13
    gap = 4

    # Approximate month positions.
    for month in range(1, 13):

        x = left + (
            (month - 1)
            * 4.4
            * (cell_size + gap)
        )

        labels.append(
            f"""
            <text
                x="{x:.1f}"
                y="{top}"
                class="month"
            >
                {date(2026, month, 1).strftime("%b")}
            </text>
            """
        )

    return "\n".join(labels)


def weekday_labels():

    labels = []

    left = 35
    top = 125

    names = [
        "Sun",
        "",
        "Tue",
        "",
        "Thu",
        "",
        "Sat",
    ]

    for index, name in enumerate(names):

        if not name:
            continue

        y = (
            top
            + index * 17
        )

        labels.append(
            f"""
            <text
                x="{left}"
                y="{y}"
                class="weekday"
            >
                {name}
            </text>
            """
        )

    return "\n".join(labels)


def create_svg(data):

    contributions = data.get(
        "contributions",
        []
    )

    metrics = data.get(
        "metrics",
        {}
    )

    cells = create_cells(
        contributions
    )

    months = month_labels()

    weekdays = weekday_labels()

    total = metrics.get(
        "total",
        0
    )

    current_streak = metrics.get(
        "current_streak",
        0
    )

    longest_streak = metrics.get(
        "longest_streak",
        0
    )

    best_day = metrics.get(
        "best_day",
        0
    )

    username = data.get(
        "username",
        "saziddeveloper"
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>

<defs>

    <style>

        .title {{
            fill: {TEXT};
            font-family: monospace;
            font-size: 18px;
            font-weight: bold;
        }}

        .subtitle {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 12px;
        }}

        .month {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 11px;
        }}

        .weekday {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 10px;
        }}

        .metric-label {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 10px;
        }}

        .metric-value {{
            fill: {GOLD_4};
            font-family: monospace;
            font-size: 20px;
            font-weight: bold;
        }}

        .cell {{
            opacity: 0;
        }}

    </style>

</defs>


<!-- Background -->

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="26"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="2"
/>


<!-- Header -->

<text
    x="40"
    y="45"
    class="title"
>
    CONTRIBUTION MATRIX
</text>


<text
    x="40"
    y="68"
    class="subtitle"
>
    @{html.escape(username)} • GitHub activity
</text>


<!-- Metrics -->

<text
    x="720"
    y="30"
    class="metric-label"
>
    TOTAL
</text>

<text
    x="720"
    y="55"
    class="metric-value"
>
    {total}
</text>


<text
    x="825"
    y="30"
    class="metric-label"
>
    STREAK
</text>

<text
    x="825"
    y="55"
    class="metric-value"
>
    {current_streak}
</text>


<text
    x="950"
    y="30"
    class="metric-label"
>
    BEST
</text>

<text
    x="950"
    y="55"
    class="metric-value"
>
    {best_day}
</text>


<!-- Month labels -->

{months}


<!-- Weekday labels -->

{weekdays}


<!-- Heatmap -->

{cells}


<!-- Legend -->

<text
    x="820"
    y="365"
    class="subtitle"
>
    LESS
</text>


<rect
    x="860"
    y="355"
    width="13"
    height="13"
    rx="3"
    fill="{GOLD_1}"
/>


<rect
    x="880"
    y="355"
    width="13"
    height="13"
    rx="3"
    fill="{GOLD_2}"
/>


<rect
    x="900"
    y="355"
    width="13"
    height="13"
    rx="3"
    fill="{GOLD_3}"
/>


<rect
    x="920"
    y="355"
    width="13"
    height="13"
    rx="3"
    fill="{GOLD_4}"
/>


<text
    x="945"
    y="365"
    class="subtitle"
>
    MORE
</text>


<!-- Footer -->

<text
    x="40"
    y="395"
    class="subtitle"
>
    Longest streak: {longest_streak} days
</text>


<text
    x="970"
    y="395"
    class="subtitle"
>
    AUTO UPDATED
</text>


</svg>
"""


def main():

    print("=" * 50)
    print("       CONTRIBUTION SVG RENDERER")
    print("=" * 50)

    print(
        f"Reading {INPUT}..."
    )

    data = load_data()

    print(
        "Rendering contribution heatmap..."
    )

    svg = create_svg(data)

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print()
    print("Done!")
    print(
        f"Created: {OUTPUT}"
    )


if __name__ == "__main__":
    main()