from pathlib import Path
from datetime import date, timedelta
import json
import html


# ============================================================
# FILES
# ============================================================

INPUT = Path("data/contributions.json")
OUTPUT = Path("contrib-heatmap.svg")


# ============================================================
# SVG SIZE
# ============================================================

WIDTH = 820
HEIGHT = 320


# ============================================================
# THEME
# ============================================================

BG = "#090909"
BORDER = "#292929"

TEXT = "#B8B8B8"
MUTED = "#666666"

GOLD_1 = "#17140B"
GOLD_2 = "#51451C"
GOLD_3 = "#8F7727"
GOLD_4 = "#D4AF37"


# ============================================================
# LOAD CONTRIBUTION DATA
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
# CONTRIBUTION COLORS
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
# BUILD CALENDAR
# ============================================================

def build_calendar(contributions):

    by_date = {
        item["date"]: item
        for item in contributions
    }

    dates = []

    for item in contributions:

        try:

            dates.append(
                date.fromisoformat(
                    item["date"]
                )
            )

        except Exception:

            continue

    if not dates:

        raise RuntimeError(
            "No valid contribution dates found."
        )

    # Use the latest date from the fetched data.
    last_day = max(dates)

    # Move to Saturday.
    while last_day.weekday() != 5:

        last_day += timedelta(
            days=1
        )

    # 53 weeks.
    first_day = (
        last_day
        - timedelta(
            days=(53 * 7) - 1
        )
    )

    # Move to Sunday.
    while first_day.weekday() != 6:

        first_day -= timedelta(
            days=1
        )

    cells = []

    current = first_day

    while current <= last_day:

        item = by_date.get(
            current.isoformat(),
            {}
        )

        cells.append(
            {
                "date": current,
                "level": int(
                    item.get(
                        "level",
                        0
                    )
                ),
                "count": int(
                    item.get(
                        "count",
                        0
                    )
                )
            }
        )

        current += timedelta(
            days=1
        )

    return (
        cells,
        first_day,
        last_day
    )


# ============================================================
# CREATE SVG
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

    # --------------------------------------------------------
    # CALENDAR
    # --------------------------------------------------------

    cells, first_day, last_day = (
        build_calendar(
            contributions
        )
    )

    # --------------------------------------------------------
    # GRID
    # --------------------------------------------------------

    CELL = 11
    GAP = 3
    STEP = CELL + GAP

    COLUMNS = 53
    ROWS = 7

    GRID_X = 55
    GRID_Y = 104

    GRID_WIDTH = (
        COLUMNS * CELL
        + (COLUMNS - 1) * GAP
    )

    GRID_HEIGHT = (
        ROWS * CELL
        + (ROWS - 1) * GAP
    )

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
    # HEATMAP CELLS
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
        count = cell["count"]

        fill = contribution_color(
            level
        )

        tooltip = (
            f"{current.isoformat()} — "
            f"{count} contributions"
        )

        delay = index * 0.0015

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
                        dur="0.25s"
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

    # Width estimate for the longest
    # three-letter month name.
    LABEL_WIDTH = 25

    # Minimum distance between labels.
    LABEL_GAP = 9

    last_label_right = (
        GRID_X - LABEL_GAP
    )

    while cursor <= last_day:

        days_from_start = (
            cursor - first_day
        ).days

        week = (
            days_from_start // 7
        )

        x = (
            GRID_X
            + week * STEP
        )

        # Keep label inside the grid.
        max_x = (
            GRID_X
            + GRID_WIDTH
            - LABEL_WIDTH
        )

        x = max(
            GRID_X,
            min(x, max_x)
        )

        # Don't allow labels to overlap.
        if (
            x >=
            last_label_right
            + LABEL_GAP
        ):

            month_labels.append(
                f"""
                <text
                    x="{x}"
                    y="90"
                    class="month"
                >
                    {cursor.strftime("%b")}
                </text>
                """
            )

            last_label_right = (
                x + LABEL_WIDTH
            )

        # Move to next month.
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
                x="12"
                y="{y}"
                class="weekday"
            >
                {name}
            </text>
            """
        )

    # --------------------------------------------------------
    # LEGEND
    # --------------------------------------------------------

    legend_x = 575

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
    font-size: 16px;
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


<!-- ======================================================
     BACKGROUND
     ====================================================== -->

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


<!-- ======================================================
     HEADER
     ====================================================== -->

<text
    x="24"
    y="34"
    class="title"
>
    CONTRIBUTION MATRIX
</text>

<text
    x="24"
    y="54"
    class="subtitle"
>
    @{html.escape(username)} • GitHub activity
</text>


<!-- ======================================================
     METRICS
     ====================================================== -->

<text
    x="475"
    y="24"
    class="metric-label"
>
    TOTAL
</text>

<text
    x="475"
    y="46"
    class="metric-value"
>
    {total}
</text>


<text
    x="565"
    y="24"
    class="metric-label"
>
    STREAK
</text>

<text
    x="565"
    y="46"
    class="metric-value"
>
    {current_streak}
</text>


<text
    x="660"
    y="24"
    class="metric-label"
>
    BEST
</text>

<text
    x="660"
    y="46"
    class="metric-value"
>
    {best_day}
</text>


<!-- ======================================================
     MONTH LABELS
     ====================================================== -->

{''.join(month_labels)}


<!-- ======================================================
     WEEKDAY LABELS
     ====================================================== -->

{''.join(weekday_labels)}


<!-- ======================================================
     HEATMAP
     ====================================================== -->

{''.join(rendered_cells)}


<!-- ======================================================
     LEGEND
     ====================================================== -->

<text
    x="{legend_x}"
    y="280"
    class="subtitle"
>
    LESS
</text>

<rect
    x="{legend_x + 35}"
    y="271"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_1}"
/>

<rect
    x="{legend_x + 52}"
    y="271"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_2}"
/>

<rect
    x="{legend_x + 69}"
    y="271"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_3}"
/>

<rect
    x="{legend_x + 86}"
    y="271"
    width="11"
    height="11"
    rx="2"
    fill="{GOLD_4}"
/>

<text
    x="{legend_x + 103}"
    y="280"
    class="subtitle"
>
    MORE
</text>


<!-- ======================================================
     FOOTER
     ====================================================== -->

<text
    x="24"
    y="295"
    class="subtitle"
>
    Longest streak: {longest_streak} days
</text>

<text
    x="24"
    y="311"
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


if __name__ == "__main__":

    main()