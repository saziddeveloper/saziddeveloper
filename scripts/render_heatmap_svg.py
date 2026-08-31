from pathlib import Path
from datetime import date, timedelta
import json
import html


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


# ------------------------------------------------------------
# CANVAS
# ------------------------------------------------------------

WIDTH = 1000
HEIGHT = 330

BG = "#090909"
PANEL = "#0D0D0D"
BORDER = "#292929"

TEXT = "#B8B8B8"
MUTED = "#666666"

GOLD_1 = "#17140B"
GOLD_2 = "#51451C"
GOLD_3 = "#8F7727"
GOLD_4 = "#D4AF37"


# ------------------------------------------------------------
# LOAD DATA
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# COLOR
# ------------------------------------------------------------

def contribution_color(level):

    level = int(level or 0)

    if level <= 0:
        return GOLD_1

    if level == 1:
        return GOLD_2

    if level == 2:
        return GOLD_3

    return GOLD_4


# ------------------------------------------------------------
# CALENDAR RANGE
# ------------------------------------------------------------

def calendar_range(contributions):

    if not contributions:
        today = date.today()

        while today.weekday() != 6:
            today -= timedelta(days=1)

        first_day = today - timedelta(days=52 * 7)

        return first_day, today

    dates = [
        date.fromisoformat(
            item["date"]
        )
        for item in contributions
    ]

    latest = max(dates)

    # End on Saturday so the calendar is complete.
    end = latest

    while end.weekday() != 5:
        end += timedelta(days=1)

    # 53 weeks × 7 days.
    first = end - timedelta(days=(53 * 7) - 1)

    return first, end


# ------------------------------------------------------------
# HEATMAP CELLS
# ------------------------------------------------------------

def create_cells(contributions):

    cell_size = 12
    gap = 4

    # Space for weekday labels.
    left = 58
    top = 105

    columns = 53

    by_date = {
        item["date"]: item
        for item in contributions
    }

    first_day, last_day = calendar_range(
        contributions
    )

    cells = []

    total_cells = columns * 7

    for index in range(total_cells):

        current = first_day + timedelta(
            days=index
        )

        item = by_date.get(
            current.isoformat()
        )

        level = (
            item.get("level", 0)
            if item
            else 0
        )

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
            level
        )

        if item:
            tooltip = (
                f"{current.isoformat()} — "
                f"GitHub activity level {level}/4"
            )
        else:
            tooltip = (
                f"{current.isoformat()} — "
                f"No activity data"
            )

        delay = index * 0.003

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
                        dur="0.35s"
                        begin="{delay:.3f}s"
                        fill="freeze"
                    />
                </rect>
            </g>
            """
        )

    return "\n".join(cells)


# ------------------------------------------------------------
# MONTH LABELS
# ------------------------------------------------------------

def month_labels(contributions):

    cell_size = 12
    gap = 4

    left = 58
    top = 88

    first_day, last_day = calendar_range(
        contributions
    )

    labels = []

    current = date(
        first_day.year,
        first_day.month,
        1
    )

    while current <= last_day:

        days_from_start = (
            current - first_day
        ).days

        week = days_from_start // 7

        x = (
            left
            + week * (cell_size + gap)
        )

        labels.append(
            f"""
            <text
                x="{x}"
                y="{top}"
                class="month"
            >
                {current.strftime("%b")}
            </text>
            """
        )

        if current.month == 12:

            current = date(
                current.year + 1,
                1,
                1
            )

        else:

            current = date(
                current.year,
                current.month + 1,
                1
            )

    return "\n".join(labels)


# ------------------------------------------------------------
# WEEKDAY LABELS
# ------------------------------------------------------------

def weekday_labels():

    left = 16
    top = 114

    names = [
        "Sun",
        "",
        "Tue",
        "",
        "Thu",
        "",
        "Sat",
    ]

    labels = []

    for index, name in enumerate(names):

        if not name:
            continue

        y = (
            top
            + index * 16
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


# ------------------------------------------------------------
# MAIN SVG
# ------------------------------------------------------------

def create_svg(data):

    contributions = data.get(
        "contributions",
        []
    )

    metrics = data.get(
        "metrics",
        {}
    )

    username = data.get(
        "username",
        "saziddeveloper"
    )

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

    cells = create_cells(
        contributions
    )

    months = month_labels(
        contributions
    )

    weekdays = weekday_labels()

    return f"""<?xml version="1.0" encoding="UTF-8"?>

<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{WIDTH}"
    height="{HEIGHT}"
    viewBox="0 0 {WIDTH} {HEIGHT}"
>

<defs>

    <filter
        id="goldGlow"
        x="-50%"
        y="-50%"
        width="200%"
        height="200%"
    >
        <feGaussianBlur
            stdDeviation="3"
            result="blur"
        />

        <feMerge>
            <feMergeNode
                in="blur"
            />

            <feMergeNode
                in="SourceGraphic"
            />
        </feMerge>
    </filter>

    <style>

        .title {{
            fill: {TEXT};
            font-family: monospace;
            font-size: 18px;
            font-weight: bold;
            letter-spacing: 1px;
        }}

        .subtitle {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 11px;
        }}

        .month {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 10px;
        }}

        .weekday {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 9px;
        }}

        .metric-label {{
            fill: {MUTED};
            font-family: monospace;
            font-size: 9px;
            letter-spacing: 1px;
        }}

        .metric-value {{
            fill: {GOLD_4};
            font-family: monospace;
            font-size: 18px;
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
    rx="22"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="2"
/>


<!-- Subtle inner panel -->

<rect
    x="12"
    y="12"
    width="{WIDTH - 24}"
    height="{HEIGHT - 24}"
    rx="17"
    fill="{PANEL}"
    opacity="0.45"
/>


<!-- Header -->

<text
    x="32"
    y="38"
    class="title"
>
    CONTRIBUTION MATRIX
</text>


<text
    x="32"
    y="59"
    class="subtitle"
>
    @{html.escape(username)} • GitHub activity
</text>


<!-- Metrics -->

<text
    x="690"
    y="28"
    class="metric-label"
>
    TOTAL
</text>

<text
    x="690"
    y="50"
    class="metric-value"
>
    {total}
</text>


<text
    x="785"
    y="28"
    class="metric-label"
>
    STREAK
</text>

<text
    x="785"
    y="50"
    class="metric-value"
>
    {current_streak}
</text>


<text
    x="885"
    y="28"
    class="metric-label"
>
    BEST
</text>

<text
    x="885"
    y="50"
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
    x="730"
    y="270"
    class="subtitle"
>
    ACTIVITY
</text>


<text
    x="790"
    y="270"
    class="subtitle"
>
    LESS
</text>


<rect
    x="825"
    y="261"
    width="12"
    height="12"
    rx="3"
    fill="{GOLD_1}"
/>


<rect
    x="844"
    y="261"
    width="12"
    height="12"
    rx="3"
    fill="{GOLD_2}"
/>


<rect
    x="863"
    y="261"
    width="12"
    height="12"
    rx="3"
    fill="{GOLD_3}"
/>


<rect
    x="882"
    y="261"
    width="12"
    height="12"
    rx="3"
    fill="{GOLD_4}"
/>


<text
    x="902"
    y="270"
    class="subtitle"
>
    MORE
</text>


<!-- Footer information -->

<text
    x="32"
    y="306"
    class="subtitle"
>
    Longest streak: {longest_streak} days
</text>


<text
    x="32"
    y="322"
    class="subtitle"
>
    Updated automatically • github.com/{html.escape(username)}
</text>


</svg>
"""


# ------------------------------------------------------------
# WRITE FILE
# ------------------------------------------------------------

def main():

    data = load_data()

    svg = create_svg(
        data
    )

    OUTPUT.write_text(
        svg,
        encoding="utf-8"
    )

    print(
        f"Generated {OUTPUT}"
    )

    print(
        f"Size: {WIDTH} × {HEIGHT}"
    )


if __name__ == "__main__":
    main()