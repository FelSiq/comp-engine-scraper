import time

import selenium
import selenium.webdriver
from selenium.webdriver.support import expected_conditions
import pyderman


num_pages = 1018
output_dir = "~/time_series_data/zip_files_synthetic"
url_base = "https://www.comp-engine.org/#!browse/category/synthetic/"
delay_after_download = 0.05


if not url_base.endswith("/"):
    url_base += "/"


path = pyderman.install(
    browser=pyderman.firefox,
    file_directory="./fire",
    verbose=True,
    chmod=True,
    overwrite=False,
)

options = selenium.webdriver.FirefoxOptions()
options.set_preference("browser.download.folderList", 2)
options.add_argument("--headless")
options.set_preference("browser.download.dir", output_dir)
options.set_preference("browser.download.manager.showWhenStarting", False)
options.set_preference(
    "browser.helperApps.neverAsk.saveToDisk", "application/octet-stream"
)

driver = selenium.webdriver.Firefox(options=options, executable_path=path)
xpath = "//*[contains(text(), 'Download all on page')]"

for i in range(1, num_pages + 1):
    print(f"Getting page {i}...", end=" ")

    driver.get(url_base + str(i))

    selenium.webdriver.support.ui.WebDriverWait(driver, 10).until(
        selenium.webdriver.support.expected_conditions.invisibility_of_element_located(
            (selenium.webdriver.common.by.By.CLASS_NAME, "app-loading")
        )
    )

    selenium.webdriver.support.ui.WebDriverWait(driver, 10).until(
        selenium.webdriver.support.expected_conditions.presence_of_element_located(
            (selenium.webdriver.common.by.By.XPATH, xpath)
        )
    )

    download_button = driver.find_element_by_xpath(xpath)

    assert download_button.text == "DOWNLOAD ALL ON PAGE"

    download_button.click()

    print("Ok.")

    time.sleep(delay_after_download)


time.sleep(10)
driver.quit()
