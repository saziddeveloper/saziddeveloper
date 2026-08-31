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
    print(f"Fetching contribution calendar for @{USERNAME}...")

    response = requests.get(
        URL,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.text


def parse_contributions(html):
    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    days = soup.select(
        "td.ContributionCalendar-day"
    )

    if not days:
        raise RuntimeError(
            "Could not find GitHub contribution cells."
        )

    contributions = []

    for cell in days:

        date_value = cell.get("data-date")

        if not date_value:
            continue

        count = 0

        # GitHub usually stores the contribution count
        # inside an aria-label.
        aria_label = cell.get(
            "aria-label",
            ""
        )

        match = re.search(
            r"(\d+)\s+contribution",
            aria_label
        )

        if match:
            count = int(match.group(1))

        # Determine contribution level.
        level = cell.get(
            "data-level",
            "0"
        )

        contributions.append(
            {
                "date": date_value,
                "count": count,
                "level": int(level),
            }
        )

    return contributions


def calculate_metrics(contributions):

    if not contributions:
        return {
            "total": 0,
            "current_streak": 0,
            "longest_streak": 0,
            "best_day": 0,
            "best_day_date": None,
        }

    total = sum(
        item["count"]
        for item in contributions
    )

    best = max(
        contributions,
        key=lambda item: item["count"]
    )

    # Sort chronologically.
    contributions = sorted(
        contributions,
        key=lambda item: item["date"]
    )

    longest_streak = 0
    current_streak = 0
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
                running_streak
            )

        else:
            running_streak = 0

        previous_date = current_date

    # Calculate current streak from the end.
    for item in reversed(contributions):

        if item["count"] > 0:
            current_streak += 1
        else:
            break

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best["count"],
        "best_day_date": best["date"],
    }


def save_data(contributions, metrics):

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
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
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"Saved contribution data to {OUTPUT}"
    )


def main():

    print("=" * 50)
    print("       GITHUB CONTRIBUTION FETCHER")
    print("=" * 50)

    html = fetch_page()

    print("Parsing contribution calendar...")

    contributions = parse_contributions(
        html
    )

    print(
        f"Found {len(contributions)} contribution days."
    )

    metrics = calculate_metrics(
        contributions
    )

    print()
    print(
        f"Total contributions: "
        f"{metrics['total']}"
    )

    print(
        f"Current streak: "
        f"{metrics['current_streak']} days"
    )

    print(
        f"Longest streak: "
        f"{metrics['longest_streak']} days"
    )

    print(
        f"Best day: "
        f"{metrics['best_day']} contributions"
    )

    save_data(
        contributions,
        metrics
    )

    print()
    print("Done!")


if __name__ == "__main__":
    main()