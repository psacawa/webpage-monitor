#!/usr/bin/env python3
import sys
import re
from os.path import expanduser, isfile
from collections import namedtuple
import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

PageMonitorData = namedtuple("PageMonitorData", ["url", "selector", "max_price"])


def main():
    """
    Read a data file for records of the form <url> <css-selector> <price>, and check all
    the corresponding DOM elements. If they are below the prices, output a notice. Also
    output a notice if the text of the element is not a number.
    """
    records = open(config_file()).readlines()
    for record in records:
        logging.debug(f"Processing {record}")
        try:
            record = record.strip()
            data = parse_record(record)
            query_page(data)
        except Exception as e:
            logging.error(e)
            continue

def config_file() -> str:
    """
    Find the config file carrying web monitor records. The first existing file is
    returned
    """
    config_options = [
        "~/.webmonitorrc",
        "~/webmonitorrc"
    ]
    for file in config_options:
        if isfile(expanduser(file)):
            return expanduser(file)
    raise FileNotFoundError("No config file found")

def parse_record(record) -> PageMonitorData:
    """extract tuple (url,selector,max-price)"""
    fields = re.split(r"\s+", record)
    assert len(fields) == 3, f"Improper record: {record}"
    url = fields[0]
    #  TODO 06/12/20 psacawa: validate URL
    selector = fields[1]
    max_price = float(fields[2])
    return PageMonitorData(url, selector, max_price)


def query_page(data: PageMonitorData):
    """Query the page page described in the monitor data"""
    response = requests.get(data.url)
    assert (
        response.status_code == 200
    ), "http request to {data.url} failed with {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.select(data.selector)
    assert len(elements) == 1, f"Selector '{data.selector}' returned too many elements"
    text: str = elements[0].text
    price = float(text)
    if price <= data.max_price:
        notify_success(data, price)


def notify_success(data: PageMonitorData, price: float):
    """Notify that a deal has been found"""
    print(f"Deal found at {data.url} for ${price:.2f} (threshold ${data.max_price:.2f})")


if __name__ == "__main__":
    main()
