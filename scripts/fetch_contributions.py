from pathlib import Path
from datetime import date, timedelta
import json
import re

import requests
from bs4 import BeautifulSoup


USERNAME = "saziddeveloper"

OUTPUT = Path("data/contributions.json")

URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_page():

    print(
        f"Fetching GitHub contributions for @{USERNAME}..."
    )

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    elements = soup.select(
        "td.ContributionCalendar-day[data-date][data-level]"
    )

    print(
        f"Found {len(elements)} contribution days."
    )

    contributions = []

    for element in elements:

        date_value = element.get(
            "data-date"
        )

        level_value = element.get(
            "data-level",
            "0",
        )

        try:
            day = date.fromisoformat(
                date_value
            )
        except (TypeError, ValueError):
            continue

        try:
            level = int(level_value)
        except (TypeError, ValueError):
            level = 0

        # GitHub's public HTML currently exposes
        # contribution intensity as data-level.
        #
        # 0 = no contribution
        # 1 = low
        # 2 = medium-low
        # 3 = medium-high
        # 4 = high
        #
        # We store the level directly and use it
        # for the visual heatmap.

        contributions.append(
            {
                "date": day.isoformat(),
                "count": level,
                "level": level,
            }
        )

    contributions.sort(
        key=lambda item: item["date"]
    )

    if not contributions:

        raise RuntimeError(
            "No contribution days found."
        )

    return contributions


def calculate_metrics(contributions):

    total = sum(
        item["count"]
        for item in contributions
    )

    best_day = max(
        contributions,
        key=lambda item: item["count"],
    )

    longest_streak = 0
    running_streak = 0
    previous_date = None

    for item in contributions:

        current_date = date.fromisoformat(
            item["date"]
        )

        if item["count"] > 0:

            if (
                previous_date is not None
                and current_date
                == previous_date + timedelta(days=1)
            ):
                running_streak += 1
            else:
                running_streak = 1

            longest_streak = max(
                longest_streak,
                running_streak,
            )

        else:
            running_streak = 0

        previous_date = current_date

    current_streak = 0

    for item in reversed(contributions):

        if item["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day["count"],
        "best_day_date": best_day["date"],
    }


def save_data(
    contributions,
    metrics,
):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = {
        "username": USERNAME,
        "generated_at": date.today().isoformat(),
        "metrics": metrics,
        "contributions": contributions,
    }

    OUTPUT.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved data to {OUTPUT}"
    )


def main():

    print("=" * 55)
    print("       GITHUB CONTRIBUTION FETCHER")
    print("=" * 55)

    html = fetch_page()

    contributions = parse_contributions(
        html
    )

    metrics = calculate_metrics(
        contributions
    )

    print()
    print(
        f"Contribution days : {len(contributions)}"
    )

    print(
        f"Activity levels   : "
        f"{sum(x['level'] > 0 for x in contributions)}"
    )

    print(
        f"Activity score    : {metrics['total']}"
    )

    print(
        f"Current streak    : "
        f"{metrics['current_streak']} days"
    )

    print(
        f"Longest streak    : "
        f"{metrics['longest_streak']} days"
    )

    print(
        f"Best level        : "
        f"{metrics['best_day']}"
    )

    print(
        f"Best day          : "
        f"{metrics['best_day_date']}"
    )

    save_data(
        contributions,
        metrics,
    )

    print()
    print("SUCCESS")


if __name__ == "__main__":
    main()