"""
Interact with HP Web Interface and perform
scan

Only expected Documents to be PDF
"""
import json
import os
from argparse import ArgumentParser
from enum import Enum
from pathlib import Path
from time import sleep

from selenium import webdriver


class FeedModes(Enum):
    GLASS = '//*[@id="tmpId2-Inp"]/option[1]'
    ADF = '//*[@id="tmpId2-Inp"]/option[2]'

HOME_DIR = os.path.expanduser('~')
DOWNLOADED_FILE = f"{HOME_DIR}/Downloads/NextDocument.pdf"


def automate_scan_process(printer_ip: str, filepath: str, feed: str) -> None:
    """Scan document and save at `filename`"""
    feed = FeedModes[feed.upper()]
    scan_and_save(printer_ip, feed)

    sleep(2)

    mv_downloaded_scan(filepath)


def scan_and_save(printer_ip: str, feed_mode: FeedModes=FeedModes.GLASS) -> None:
    """
    Saves as PDF in ~/Downloads/NextDocument.pdf
    """
    # create Chrome driver
    appState = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local",
                "account": ""
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
    }
    profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState)}
    options = webdriver.ChromeOptions()
    options.add_experimental_option('prefs', profile)
    options.add_argument("--disable-extensions")    # disabling extensions
    options.add_argument("--disable-gpu")           # applicable to windows os only
    options.add_argument("--disable-dev-shm-usage") # overcome limited resource problems
    options.add_argument("--no-sandbox")
    options.add_argument("--remote-debugging-port=9223")
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(60)

    # connect to scanner
    driver.get(f"http://{printer_ip}#hId-pgWebScan")
    

    # select scan options and start
    scan_feed = driver.find_element_by_xpath(feed_mode.value)
    scan_feed.click()

    start_scan = driver.find_element_by_xpath('//*[@id="app-page-btns"]/div/input[1]')
    start_scan.click()

    confirm = driver.find_element_by_xpath('/html/body/div[4]/div[2]/button')
    confirm.click()

    # switch focus to new tab
    driver.switch_to.window(driver.window_handles[1])
    sleep(30)
    driver.execute_script('window.print();')

    sleep(2)
    driver.quit()


def mv_downloaded_scan(destination_fp: str) -> None:
    """
    Moves the scanned pdf to a new location relative to the `HOME_DIR`
    """
    # define absolute path of destination
    abs_path = f'{HOME_DIR}/{destination_fp}'

    # create destination folders if required
    dest_folder = Path("/".join(abs_path.split('/')[:-1]))
    if ".pdf" not in dest_folder.as_posix():
        dest_folder.mkdir(parents=True, exist_ok=True)

    # move downloaded file to destination
    Path(DOWNLOADED_FILE).replace(abs_path)


if __name__ == "__main__":
    # setup argument parser
    parser = ArgumentParser()
    parser.add_argument('destination_fp', help="relative path to new file")
    parser.add_argument('feed_mode', nargs='?', help='mode for feeding pages to scan')
    args = parser.parse_args()

    # create the scanned document
    printer_ip = os.environ['PRINTER_IP']
    print(f'\nPrinter IP: {printer_ip}')

    feed_mode = args.feed_mode or FeedModes.ADF
    scan_and_save(printer_ip, feed_mode)
    sleep(2)

    # move to the desired folder
    mv_downloaded_scan(args.destination_fp)

    print(f'Successfully scanned to {args.destination_fp}')
