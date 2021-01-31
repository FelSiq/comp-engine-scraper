"""Scrape time-series from 'comp-engine.org' using Selenium."""
import time
import os
import argparse
import multiprocessing

import selenium
import selenium.webdriver
import selenium.common.exceptions
from selenium.webdriver.support import expected_conditions
import pyderman


def parse_args():
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

    parser.add_argument(
        "--num-cpu",
        type=int,
        default=4,
        help=(
            "Number of cores to download data in parallel. Set 0 to use "
            "all cores available, but beware about server timeouts."
        ),
    )

    args = parser.parse_args()

    assert (
        args.num_cpu >= 0
    ), f"Argument '--num-cores' must be >= 0 (got {args.num_core})."

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

    assert output_dir
    assert url_base

    if not url_base.endswith("/"):
        url_base += "/"

    try:
        os.mkdir(output_dir)
        print("Created output directory for .zip files.")

    except FileExistsError:
        print("Output directory found.")

    return url_base, start_on_page, end_on_page, output_dir, headless, args.num_cpu


def get_selenium_path_and_options(id: int, output_dir: str, headless: bool):
    path = pyderman.install(
        browser=pyderman.firefox,
        file_directory=f"./pyderman/firefox_{id}",
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

    return path, options


def get_pages(
    id: int,
    output_dir: str,
    headless: bool,
    id_queue: multiprocessing.Queue,
    processed_ids: multiprocessing.Queue,
    print_lock: multiprocessing.Lock,
    total_pages: int,
    url_base: str,
    xpath: str,
    delay_after_download: float,
    fail_ids: multiprocessing.Queue,
):
    path, options = get_selenium_path_and_options(id, output_dir, headless)
    driver = selenium.webdriver.Firefox(options=options, executable_path=path)

    while not id_queue.empty():
        i = id_queue.get()

        driver.get(url_base + str(i))

        try:
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

        except selenium.common.exceptions.TimeoutException:
            fail_ids.put(i)
            processed_ids.put(i)
            continue

        download_button = driver.find_element_by_xpath(xpath)
        assert download_button.text == "DOWNLOAD ALL ON PAGE"
        download_button.click()
        time.sleep(delay_after_download)
        processed_ids.put(i)
        print_lock.acquire()

        try:
            print(
                f"Got {processed_ids.qsize():4d} of {total_pages} pages (worker id {os.getpid()})"
                f"({100 * (processed_ids.qsize()) / (total_pages):.2f}%)."
            )

        finally:
            print_lock.release()

    print(f"Worker (id {os.getpid()}) finished its work. Will quit in 60 seconds.")
    time.sleep(60)
    return True


def run():
    url_base, start_on_page, end_on_page, output_dir, headless, num_cpu = parse_args()

    print_lock = multiprocessing.Lock()
    id_queue = multiprocessing.Queue()
    processed_ids = multiprocessing.Queue()
    fail_ids = multiprocessing.Queue()
    processes = []
    xpath = "//*[contains(text(), 'Download all on page')]"
    delay_after_download = 0.05

    for i in range(start_on_page, end_on_page + 1):
        id_queue.put(i)

    total_pages = id_queue.qsize()
    num_cpu = min(
        multiprocessing.cpu_count(),
        num_cpu if num_cpu else multiprocessing.cpu_count(),
        id_queue.qsize(),
    )

    print(f"Will run on {num_cpu} cpu(s) (of {multiprocessing.cpu_count()} available).")

    # Note: create one driver and get pages in parallel
    for i in range(num_cpu):
        p = multiprocessing.Process(
            target=get_pages,
            args=(
                i,
                output_dir,
                headless,
                id_queue,
                processed_ids,
                print_lock,
                total_pages,
                url_base,
                xpath,
                delay_after_download,
                fail_ids,
            ),
        )
        processes.append(p)
        p.start()

    # Note: join processes and await each one finishes
    for p in processes:
        p.join()

    print("All done! Will end process soon.")

    if fail_ids.qsize():
        print(f"Failed in {fail_ids.qsize()} pages. Maybe try again later?")


if __name__ == "__main__":
    run()
