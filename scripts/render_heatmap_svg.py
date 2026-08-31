from pathlib import Path
from datetime import date, timedelta
import json
import html


INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")

# ============================================================
# THEME
# ============================================================

BG = "#090909"
PANEL = "#0D0D0D"
BORDER = "#292929"

TEXT = "#B8B8B8"
MUTED = "#666666"

GOLD_1 = "#17140B"
GOLD_2 = "#51451C"
GOLD_3 = "#8F7727"
GOLD_4 = "#D4AF37"


# ============================================================
# LOAD DATA
# ============================================================

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


# ============================================================
# COLORS
# ============================================================

def contribution_color(level):

    level = int(level or 0)

    if level <= 0:
        return GOLD_1

    if level == 1:
        return GOLD_2

    if level == 2:
        return GOLD_3

    return GOLD_4


# ============================================================
# CALENDAR
# ============================================================

def build_calendar(contributions):

    by_date = {
        item["date"]: item
        for item in contributions
    }

    dates = [
        date.fromisoformat(item["date"])
        for item in contributions
    ]

    if not dates:
        raise RuntimeError(
            "No contribution data available."
        )

    latest = max(dates)

    # GitHub calendar ends on Saturday.
    while latest.weekday() != 5:
        latest += timedelta(days=1)

    # 53 complete weeks.
    first = latest - timedelta(
        days=(53 * 7) - 1
    )

    cells = []

    current = first

    while current <= latest:

        item = by_date.get(
            current.isoformat(),
            {
                "level": 0
            }
        )

        cells.append({
            "date": current,
            "level": int(
                item.get("level", 0)
            )
        })

        current += timedelta(days=1)

    return cells, first, latest


# ============================================================
# SVG GENERATOR
# ============================================================

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

    cells, first_day, last_day = build_calendar(
        contributions
    )

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    CELL = 11
    GAP = 3
    STEP = CELL + GAP

    WEEKDAY_WIDTH = 38

    COLUMNS = 53
    ROWS = 7

    GRID_WIDTH = (
        COLUMNS * CELL
        + (COLUMNS - 1) * GAP
    )

    GRID_HEIGHT = (
        ROWS * CELL
        + (ROWS - 1) * GAP
    )

    GRID_X = 64
    GRID_Y = 105

    RIGHT_MARGIN = 28

    WIDTH = (
        GRID_X
        + GRID_WIDTH
        + RIGHT_MARGIN
    )

    HEIGHT = 325

    # --------------------------------------------------------
    # METRICS
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CELLS
    # --------------------------------------------------------

    rendered_cells = []

    for index, cell in enumerate(cells):

        current = cell["date"]

        day_index = (
            current - first_day
        ).days

        week = day_index // 7
        weekday = day_index % 7

        x = (
            GRID_X
            + week * STEP
        )

        y = (
            GRID_Y
            + weekday * STEP
        )

        level = cell["level"]

        fill = contribution_color(
            level
        )

        tooltip = (
            f"{current.isoformat()} — "
            f"activity level {level}/4"
        )

        delay = index * 0.002

        rendered_cells.append(
            f"""
            <g>
                <title>{html.escape(tooltip)}</title>

                <rect
                    x="{x}"
                    y="{y}"
                    width="{CELL}"
                    height="{CELL}"
                    rx="2.5"
                    fill="{fill}"
                    class="cell"
                >
                    <animate
                        attributeName="opacity"
                        from="0"
                        to="1"
                        dur="0.3s"
                        begin="{delay:.3f}s"
                        fill="freeze"
                    />
                </rect>
            </g>
            """
        )

    # --------------------------------------------------------
    # MONTH LABELS
    # --------------------------------------------------------

    month_labels = []

    cursor = date(
        first_day.year,
        first_day.month,
        1
    )

    # Keep month labels safely inside SVG.
    MIN_MONTH_X = GRID_X
    MAX_MONTH_X = (
        GRID_X
        + GRID_WIDTH
        - 25
    )

    while cursor <= last_day:

        days_from_start = (
            cursor - first_day
        ).days

        week = days_from_start // 7

        x = (
            GRID_X
            + week * STEP
        )

        # Prevent labels from leaving the SVG.
        x = max(
            MIN_MONTH_X,
            min(x, MAX_MONTH_X)
        )

        month_labels.append(
            f"""
            <text
                x="{x}"
                y="91"
                class="month"
            >
                {cursor.strftime("%b")}
            </text>
            """
        )

        if cursor.month == 12:

            cursor = date(
                cursor.year + 1,
                1,
                1
            )

        else:

            cursor = date(
                cursor.year,
                cursor.month + 1,
                1
            )

    # --------------------------------------------------------
    # WEEKDAY LABELS
    # --------------------------------------------------------

    weekday_names = [
        "Sun",
        "",
        "Tue",
        "",
        "Thu",
        "",
        "Sat"
    ]

    weekday_labels = []

    for index, name in enumerate(
        weekday_names
    ):

        if not name:
            continue

        y = (
            GRID_Y
            + index * STEP
            + 9
        )

        weekday_labels.append(
            f"""
            <text
                x="18"
                y="{y}"
                class="weekday"
            >
                {name}
            </text>
            """
        )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    footer_y = 300

    legend_x = (
        WIDTH - 235
    )

    # --------------------------------------------------------
    # SVG
    # --------------------------------------------------------

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
    font-size: 17px;
    font-weight: bold;
    letter-spacing: 1px;
}}

.subtitle {{
    fill: {MUTED};
    font-family: monospace;
    font-size: 10px;
}}

.month {{
    fill: {MUTED};
    font-family: monospace;
    font-size: 9px;
}}

.weekday {{
    fill: {MUTED};
    font-family: monospace;
    font-size: 8px;
}}

.metric-label {{
    fill: {MUTED};
    font-family: monospace;
    font-size: 8px;
    letter-spacing: 1px;
}}

.metric-value {{
    fill: {GOLD_4};
    font-family: monospace;
    font-size: 16px;
    font-weight: bold;
}}

.cell {{
    opacity: 0;
}}

</style>

</defs>


<!-- BACKGROUND -->

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="20"
    fill="{BG}"
    stroke="{BORDER}"
    stroke-width="2"
/>


<!-- HEADER -->

<text
    x="28"
    y="35"
    class="title"
>
    CONTRIBUTION MATRIX
</text>

<text
    x="28"
    y="55"
    class="subtitle"
>
    @{html.escape(username)} • GitHub activity
</text>


<!-- METRICS -->

<text
    x="{WIDTH - 300}"
    y="25"
    class="metric-label"
>
    TOTAL
</text>

<text
    x="{WIDTH - 300}"
    y="46"
    class="metric-value"
>
    {total}
</text>


<text
    x="{WIDTH - 205}"
    y="25"
    class="metric-label"
>
    STREAK
</text>

<text
    x="{WIDTH - 205}"
    y="46"
    class="metric-value"
>
    {current_streak}
</text>


<text
    x="{WIDTH - 100}"
    y="25"
    class="metric-label"
>
    BEST
</text>

<text
    x="{WIDTH - 100}"
    y="46"
    class="metric-value"
>
    {best_day}
</text>


<!-- MONTHS -->

{''.join(month_labels)}


<!-- WEEKDAYS -->

{''.join(weekday_labels)}


<!-- CONTRIBUTION CELLS -->

{''.join(rendered_cells)}


<!-- LEGEND -->

<text
    x="{legend_x}"
    y="279"
    class="subtitle"
>
    LESS
</text>

<rect
    x="{legend_x + 36}"
    y="270"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_1}"
/>

<rect
    x="{legend_x + 53}"
    y="270"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_2}"
/>

<rect
    x="{legend_x + 70}"
    y="270"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_3}"
/>

<rect
    x="{legend_x + 87}"
    y="270"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_4}"
/>

<text
    x="{legend_x + 104}"
    y="279"
    class="subtitle"
>
    MORE
</text>


<!-- FOOTER -->

<text
    x="28"
    y="{footer_y}"
    class="subtitle"
>
    Longest streak: {longest_streak} days
</text>

<text
    x="28"
    y="316"
    class="subtitle"
>
    Updated automatically • github.com/{html.escape(username)}
</text>


</svg>
"""


# ============================================================
# MAIN
# ============================================================

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
        f"Canvas: {WIDTH if 'WIDTH' in locals() else 'dynamic'}"
    )


if __name__ == "__main__":
    main()