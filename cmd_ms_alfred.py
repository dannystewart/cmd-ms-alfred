from __future__ import annotations

import csv
import json
import sys
from io import StringIO
from typing import Any

import requests

CSV_URL = "https://raw.githubusercontent.com/merill/cmd/refs/heads/main/website/config/commands.csv"


def fetch_commands() -> list[dict[str, Any]]:
    """Fetch and read the commands CSV from cmd.ms and return a list of Alfred-formatted items."""
    items = []
    try:
        response = requests.get(CSV_URL, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Create a StringIO object from the response content
        csv_file = StringIO(response.text)
        reader = csv.DictReader(csv_file)

        for row in reader:
            items.append({  # Create the main command item
                "uid": f"{row['Command']}_{row['Category']}",
                "title": row["Command"],
                "subtitle": f"{row['Description']} ({row['Category']})",
                "arg": row["Url"],
                "autocomplete": row["Command"],
                "icon": {"path": f"icons/{row['Category'].lower()}.png"},
            })
            if row["Alias"]:  # Process aliases if they exist
                items.extend(
                    {
                        "uid": f"{alias}_{row['Category']}",
                        "title": alias,
                        "subtitle": f"Alias for {row['Command']}: {row['Description']} ({row['Category']})",
                        "arg": row["Url"],
                        "autocomplete": alias,
                        "icon": {"path": f"icons/{row['Category'].lower()}.png"},
                    }
                    for alias in row["Alias"].split("|")
                )

    except requests.RequestException as e:
        return [{"title": "Error", "subtitle": f"Failed to fetch commands: {e!s}", "valid": False}]
    except Exception as e:
        return [{"title": "Error", "subtitle": f"Failed to process items: {e!s}", "valid": False}]

    return items


def main() -> None:
    """Main function to fetch and print the commands in Alfred's JSON format."""
    json_output = json.dumps(
        {
            "items": fetch_commands(),
            "cache": {"seconds": 3600, "loosereload": "true"},
            "skipknowledge": "true",
        },
        indent=2,
    )

    sys.stdout.write(json_output)


if __name__ == "__main__":
    main()
