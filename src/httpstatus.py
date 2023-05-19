#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

import requests
from bs4 import BeautifulSoup


class HttpStatus:
    """Get the status text for a given status code."""

    MDN_URL = "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"

    def __init__(self, status_code):
        """Initialize the class."""
        if status_code not in range(100, 601):
            raise IndexError("Status code must be between 100 and 600")

        self.status_code = status_code
        self.url = f"{self.MDN_URL}/{status_code}"
        self.response = requests.get(self.url)

    def get_status_details(self):
        if self.response.status_code != 200:
            return None

        soup = BeautifulSoup(self.response.text, "lxml")
        status_title = soup.select("#content > article > h1")[0].text
        status_title = re.sub(r"\d{3}\s", "", status_title).strip()

        status_body = soup.select("#content > article > div")[0].text.strip()
        status_body = status_body.replace("\n", " ").replace("\r", " ")
        status_body = re.sub(r"\s{2,}", " ", status_body)

        return {
            "status_title": status_title,
            "status_body": status_body,
        }

    def get_response_details(self):
        status_code = self.status_code
        results = []
        if status_code not in range(100, 601):
            return results

        req = requests.get(self.MDN_URL)
        if req.status_code != 200:
            return results

        soup = BeautifulSoup(req.text, "lxml")
        section_indexes = {
            range(100, 200): 3,
            range(200, 300): 4,
            range(300, 400): 5,
            range(400, 500): 6,
            range(500, 600): 7,
        }

        for status_range, index in section_indexes.items():
            if status_code in status_range:
                response_ranges = soup.select(
                    f"#content > article > section:nth-child({index}) > h2"
                )
                if not response_ranges:
                    return results

                response_range = response_ranges[0].text.strip()
                selector = f"#content > article > section:nth-child({index}) > div > dl"
                dls = soup.select(selector)
                for dl in dls:
                    dt = dl.select("dt")
                    dd = dl.select("dd")
                    for sc, body in zip(dt, dd):
                        sc = re.match(r"\d{3}", sc.text).group().strip()
                        if status_code == int(sc):
                            body = body.text.strip()
                            body = body.replace("\n", " ").replace("\r", " ")
                            body = re.sub(r"\s{2,}", " ", body)
                            results.append(
                                {
                                    status_code: {
                                        "response_range": response_range,
                                        "response_range_body": body,
                                    }
                                }
                            )
                break

        return results

    def get_all_details(self):
        return {
            "status_code": self.status_code,
            **self.get_status_details(),
            **self.get_response_details()[0][self.status_code],
        }
