"""
Interact with HP Web Interface and perform
scan

Only expected Documents to be PDF
"""
import json
import os
from argparse import ArgumentParser
from pathlib import Path
from time import sleep
from typing import Union

from selenium import webdriver


HOME_DIR = os.path.expanduser('~')
DOWNLOADED_FILE = f"{HOME_DIR}/Downloads/NextDocument.pdf"


def scan_and_save(printer_ip: str="192.168.0.178") -> None:
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
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(60)

    # scan page
    driver.get(f"http://{printer_ip}#hId-pgWebScan")
    start_scan = driver.find_element_by_xpath('//*[@id="app-page-btns"]/div/input[1]')
    start_scan.click()

    confirm = driver.find_element_by_xpath('/html/body/div[4]/div[2]/button')
    confirm.click()

    # switch focus to new tab
    # driver.switch_to_window(driver.window_handles[1])
    driver.switch_to.window(driver.window_handles[1])
    sleep(20)
    driver.execute_script('window.print();')

    sleep(2)
    driver.close()


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

    args = parser.parse_args()

    # create the scanned document
    scan_and_save()
    sleep(2)

    # move to the desired folder
    mv_downloaded_scan(args.destination_fp)

    print(f'Successfully scanned to {args.destination_fp}')
