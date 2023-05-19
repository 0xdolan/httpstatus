#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys

import requests
from rich import print as rprint
from rich.console import Console
from rich.progress import track
from rich.table import Table

from src.httpstatus import HttpStatus

console = Console()

STATUS_COLORS = {
    range(100, 200): {"hex_code": "#7ac852"},  # the hex code is close to green
    range(200, 300): {"hex_code": "#ff9b2b"},  # the hex code is close to orange
    range(300, 400): {"hex_code": "#ec6f46"},  # the hex code is close to red
    range(400, 500): {"hex_code": "#3c78d5"},  # the hex code is close to blue
    range(500, 600): {"hex_code": "#9809f9"},  # the hex code is close to purple
}


DATA_PATH = os.path.join(os.path.dirname(__file__), "src", "data")
http_status_file = os.path.join(DATA_PATH, "httpstatus.json")


def update_data(first_time=False):
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)

    if first_time:
        rprint(
            "[red]HTTP status data file not found!\nThis process may take a while. It is one time process. Please wait...[/]"
        )
    else:
        rprint(
            "[red]Updating HTTP status data.\nThis process may take a while. Please wait...[/]"
        )

    results = []
    for i in track(range(100, 601), description="Fetching HTTP status data..."):
        http_status = HttpStatus(i)
        if http_status.get_status_details() is not None:
            results.append(http_status.get_all_details())

    with open(http_status_file, "w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=True)

    return "[green]HTTP status data fetched successfully![/]"


def read_data():
    if not os.path.exists(http_status_file):
        update_data(first_time=True)
    with open(http_status_file, "r", encoding="utf-8") as rf:
        http_status_data = json.load(rf)
    return http_status_data


data = read_data()


def get_default(status_code):
    result = list()
    for key, value in STATUS_COLORS.items():
        if status_code in key:
            color = value["hex_code"]
            status_title = json.loads(get_json(status_code))["status_title"]
            response_range = json.loads(get_json(status_code))["response_range"]
            result.append(f"\nSattus Code:\t[bold {color}]{status_code}[/]")
            result.append(f"Status Title:\t[bold  {color}]{status_title}[/]")
            result.append(f"Response Range:\t[bold  {color}]{response_range}[/]\n")

    return rprint("\n".join(result))


def get_json(status_code):
    for status in data:
        if status["status_code"] == int(status_code):
            return json.dumps(
                {
                    "status_code": status["status_code"],
                    "status_title": status["status_title"],
                    "status_body": status["status_body"],
                    "response_range": status["response_range"],
                    "response_range_body": status["response_range_body"],
                },
                ensure_ascii=True,
            )


def get_table(status_code):
    table = Table(title="\nHTTP Status Code")
    table.add_column("Status Code", justify="left")
    table.add_column("Status Title", justify="left")
    table.add_column("Status Body", justify="left")
    table.add_column("Response Range", justify="left")
    table.add_column("Response Range Body", justify="left")

    for status in data:
        if status["status_code"] == int(status_code):
            status_code = status["status_code"]
            status_title = status["status_title"]
            status_body = status["status_body"]
            response_range = status["response_range"]
            response_range_body = status["response_range_body"]
            for key, value in STATUS_COLORS.items():
                if status_code in key:
                    table.add_row(
                        f"[{value['hex_code']}]{status_code}[/]",
                        f"[{value['hex_code']}]{status_title}[/]",
                        f"[{value['hex_code']}]{status_body}[/]",
                        f"[{value['hex_code']}]{response_range}[/]",
                        f"[{value['hex_code']}]{response_range_body}[/]",
                    )

    console.print(table)


def get_url(url):
    try:
        response = requests.get(url)
        return response.status_code
    except requests.exceptions.ConnectionError:
        return "Error: Please check your internet connection"


def print_usage():
    rprint("Usage: python main.py <status_code> [--json | --table | --url <url>]")
    rprint("Options:")
    rprint("  --help, -h\t\t\tShow this help message and exit")
    rprint("  --update, -up\t\t\tUpdate HTTP status data")
    rprint("  --json, -j\t\t\tShow HTTP status data in JSON format")
    rprint("  --table, -t\t\t\tShow HTTP status data in table format")
    rprint("  --url, -u <url>\t\tShow HTTP status code of the given URL")
    rprint("  --version, -v\t\t\tShow version number and exit")


def main():
    if not os.path.exists(http_status_file):
        update_data()

    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    arg1 = sys.argv[1]

    if arg1 == "--version" or arg1 == "-v":
        rprint("HTTP Status Code v1.0.0")
        sys.exit(1)

    if arg1 == "--help" or arg1 == "-h":
        print_usage()
        sys.exit(1)

    elif arg1 == "--update" or arg1 == "-up":
        update_data()
        sys.exit(1)

    elif arg1 == "--url" or arg1 == "-u":
        if len(sys.argv) < 3:
            print("Please enter a valid URL.")
            sys.exit(1)

        url = sys.argv[2]

        if url.startswith("http://") or url.startswith("https://"):
            get_default(get_url(url))
        elif "." in url:
            url = "http://" + url

            if len(sys.argv) > 3:
                arg3 = sys.argv[3]
                if arg3 == "--json" or arg3 == "-j":
                    console.print_json(get_json(get_url(url)))
                elif arg3 == "--table" or arg3 == "-t":
                    get_table(get_url(url))
            else:
                get_default(get_url(url))
        else:
            print("Please enter a valid URL.")
        sys.exit(1)

    status_code = int(arg1)

    if len(sys.argv) > 2:
        arg2 = sys.argv[2]
        if arg2 == "--json" or arg2 == "-j":
            console.print_json(get_json(status_code))
        elif arg2 == "--table" or arg2 == "-t":
            get_table(status_code)
    else:
        get_default(status_code)


if __name__ == "__main__":
    main()
