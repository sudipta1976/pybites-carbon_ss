import os
from time import sleep
from urllib.parse import quote_plus

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

load_dotenv()

CARBON_URL = (
    "https://carbon.now.sh?l={language}&code={code}"
    "&bg={background}&t={theme}&wt={wt}"
)

# in case of a slow connection it might take a bit longer to download the image
SECONDS_SLEEP_BEFORE_DOWNLOAD = int(os.environ.get("SECONDS_SLEEP_BEFORE_DOWNLOAD", 3))


def _create_carbon_url(code, **carbon_options: str) -> str:
    language = carbon_options["language"]
    background = carbon_options["background"]
    theme = carbon_options["theme"]
    wt = carbon_options["wt"]

    url = CARBON_URL.format(
        language=quote_plus(language),
        code=quote_plus(code),
        background=quote_plus(background),
        theme=quote_plus(theme),
        wt=quote_plus(wt),
    )
    return url


def create_code_image(code: str, **kwargs: str) -> None:
    """Generate a beautiful Carbon code image"""
    options = Options()
    if not bool(kwargs.get("interactive", False)):
        options.add_argument("--headless")

    service = (
        Service(executable_path=kwargs["driver_path"])
        if kwargs["driver_path"]
        else Service()
    )

    destination = kwargs.get("destination", os.getcwd())
    prefs = {"download.default_directory": destination}
    options.add_experimental_option("prefs", prefs)

    if kwargs.get("disable-dev-shm", False):
        options.add_argument("disable-dev-shm-usage")

    url = _create_carbon_url(code, **kwargs)
    with webdriver.Chrome(service=service, options=options) as driver:
        driver.get(url)
        driver.find_element(By.ID, "export-menu").click()
        driver.find_element(By.ID, "export-png").click()
        # make sure it has time to download the image
        sleep(SECONDS_SLEEP_BEFORE_DOWNLOAD)
