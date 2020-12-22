"""Scrape time-series from 'comp-engine.org' using Selenium."""
import time
import os
import argparse

import selenium
import selenium.webdriver
from selenium.webdriver.support import expected_conditions
import pyderman


parser = argparse.ArgumentParser(description="Scrape data from 'comp-engine.org'.")

parser.add_argument(
    "data_type",
    type=str,
    help="Type of time-series to retrieve. Must be in {'real', 'synthetic', 'unassigned'}.",
)

parser.add_argument(
    "start_on_page",
    type=int,
    help="Index of comp-engine page to start from. Must be >= 1.",
)

parser.add_argument(
    "end_on_page",
    type=int,
    help="Index of comp-engine page to end. Must be >= start_on_page.",
)

parser.add_argument(
    "--render",
    action="store_true",
    help="If given, does not render firefox while retrieving data.",
)

args = parser.parse_args()

data_type = args.data_type

VALID_DATA_TYPE = {"synthetic", "real", "unassigned"}

assert (
    data_type in VALID_DATA_TYPE
), f"Given 'data_type' ('{data_type}') is invalid. Pick one from {VALID_DATA_TYPE}."

start_on_page = args.start_on_page
end_on_page = args.end_on_page

assert 0 < start_on_page <= end_on_page, (
    f"Condition not meet: 1 <= 'start_on_page' ({start_on_page}) <= 'end_on_page' ({end_on_page}). "
    "Please pick another page indices."
)

headless = not args.render

base_output_dir_path = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(base_output_dir_path, f"zip_files_{data_type}")

url_base = f"https://www.comp-engine.org/#!browse/category/{data_type}/"
delay_after_download = 0.05

assert output_dir
assert url_base
assert delay_after_download >= 0.0

if not url_base.endswith("/"):
    url_base += "/"

try:
    os.mkdir(output_dir)
    print("Created output directory for .zip files.")

except FileExistsError:
    print("Output directory found.")

path = pyderman.install(
    browser=pyderman.firefox,
    file_directory="./fire",
    verbose=True,
    chmod=True,
    overwrite=False,
)

options = selenium.webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.set_preference("browser.download.dir", output_dir)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "application/octet-stream"
)

if headless:
    options.add_argument("--headless")

driver = selenium.webdriver.Firefox(options=options, executable_path=path)
xpath = "//*[contains(text(), 'Download all on page')]"

for i in range(start_on_page, end_on_page + 1):
    print(
        f"Getting page {i} of {end_on_page} ({100. * (i - start_on_page) / (end_on_page - start_on_page + 1)}%) ...",
        end=" ",
    )

    driver.get(url_base + str(i))

    selenium.webdriver.support.ui.WebDriverWait(driver, 60).until(
        selenium.webdriver.support.expected_conditions.invisibility_of_element_located(
            (selenium.webdriver.common.by.By.CLASS_NAME, "app-loading")
        )
    )

    selenium.webdriver.support.ui.WebDriverWait(driver, 60).until(
        selenium.webdriver.support.expected_conditions.presence_of_element_located(
            (selenium.webdriver.common.by.By.XPATH, xpath)
        )
    )

    download_button = driver.find_element_by_xpath(xpath)

    assert download_button.text == "DOWNLOAD ALL ON PAGE"

    download_button.click()

    print("Ok.")

    time.sleep(delay_after_download)


print("All done! Will end process soon.")
time.sleep(10)
driver.quit()
