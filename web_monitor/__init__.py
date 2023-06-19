#!/usr/bin/env python3
import sys
import re
from os.path import expanduser, isfile
from collections import namedtuple
from typing import ChainMap
import requests
from bs4 import BeautifulSoup
import logging
import subprocess
import argparse
import configparser
from decimal import Decimal as D
import re

logger = logging.getLogger("webmonitor")
handler = logging.StreamHandler(sys.stderr)
logger.addHandler(handler)


PageMonitorData = namedtuple(
    "PageMonitorData", ["url", "selector", "max_price", "cookies", "currency"]
)

defaults = {"cookies": "", "currency": "PLN"}


def main():
    """
    Read a data file for records of the form <url> <css-selector> <price>, and check all
    the corresponding DOM elements. If they are below the prices, output a notice. Also
    output a notice if the text of the element is not a number.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log-level", type=int, default=logging.INFO)
    args = parser.parse_args(sys.argv[1:])
    logger.setLevel(level=args.log_level)

    config = configparser.ConfigParser()
    config.read(get_config_file())

    for product in config:
        if product != "DEFAULT":
            logger.debug(f"Processing {product}")
            section = config[product]
            section = ChainMap(section, defaults)
            #  gettowskie parsowanie
            cookies = [kv.split("=") for kv in section["cookies"].split()]
            print(cookies)
            cookies = {kv[0]: kv[1] for kv in cookies}
            data = PageMonitorData(
                section["url"],
                section["selector"],
                D(section["max_price"]),
                cookies,
                section["currency"],
            )
            query_page(data)


def get_config_file() -> str:
    """
    Find the config file carrying web monitor records. The first existing file is
    returned
    """
    config_options = ["~/.webmonitorrc", "~/webmonitorrc"]
    for file in config_options:
        if isfile(expanduser(file)):
            return expanduser(file)
    raise FileNotFoundError("No config file found")


def query_page(data: PageMonitorData):
    """Query the page page described in the monitor data"""
    response = requests.get(data.url, cookies=data.cookies)
    assert (
        response.status_code == 200
    ), f"http request to {data.url} failed with {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    elements = soup.select(data.selector)
    assert len(elements) == 1, f"Selector '{data.selector}' returned too many elements"
    text: str = elements[0].text
    text = text.replace(",", ".")  #  nie chcę mieszać się z lokalami
    price = D(text)
    logger.debug(
        f"Found price on page {data.url} with selector {data.selector}: {price}"
    )
    if price <= data.max_price:
        notify_success(data, price)


def notify_success(data: PageMonitorData, price: D):
    """Notify that a deal has been found"""
    message = (
        f"Sprzedaż u {data.url} za {price:.2f} {data.currency}"
        f" (próg {data.max_price:.2f} {data.currency})"
    )
    logger.info(message)
    subprocess.run(["notify-send", message])


if __name__ == "__main__":
    main()
