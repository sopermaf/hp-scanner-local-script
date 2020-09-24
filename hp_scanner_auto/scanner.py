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

from selenium import webdriver


HOME_DIR = os.path.expanduser('~')
DOWNLOADED_FILE = f"{HOME_DIR}/Downloads/NextDocument.pdf"


def automate_scan_process(printer_ip: str, filepath: str) -> None:
    """Scan document and save at `filename`"""
    scan_and_save(printer_ip)

    sleep(2)

    mv_downloaded_scan(filepath)


def scan_and_save(printer_ip: str) -> None:
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


def setup_destination() -> str:
    """Prompt user to setup a destination to move file"""
    # existing choice?
    try:
        with open('folders.json') as fp:
            prev_folders = json.load(fp)
    except FileNotFoundError:
        prev_folders = []
        choice = None
    else:
        print("###Previous paths below###")
        print(*enumerate(prev_folders), sep='\n')
        print(f'\nSelect index digit of choice(0-{len(prev_folders)})')
        choice = input('Enter digit or press enter to skip: ')

    # try to use existing choice if possible
    try:
        folder = prev_folders[int(choice)]
    except (ValueError, TypeError):
        print("\nCONFIGURING NEW PATH")
        folder = input('\tSet up new folder path from home: ')
        
        # add new folder to the list of previous folders
        prev_folders.append(folder)
        prev_folders.sort()

        with open('folders.json', 'w+') as fp:
            json.dump(prev_folders, fp, indent=4, sort_keys=True)

    # get name of the file
    filename = input('New pdf name: ')
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    
    return f'{folder}/{filename}'


if __name__ == "__main__":
    # setup argument parser
    parser = ArgumentParser()
    parser.add_argument('destination_fp', nargs='?', help="relative path to new file")

    args = parser.parse_args()

    if not args.destination_fp:
        args.destination_fp = setup_destination()

    # create the scanned document
    printer_ip = os.environ['PRINTER_IP']
    print(f'\nPrinter IP: {printer_ip}')

    scan_and_save(printer_ip)
    sleep(2)

    # move to the desired folder
    mv_downloaded_scan(args.destination_fp)

    print(f'Successfully scanned to {args.destination_fp}')
