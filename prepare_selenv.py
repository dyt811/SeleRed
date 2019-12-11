import os
from selenium import webdriver
import logging
from pathlib import Path

def PrepareTravisDriver(path_binary):
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    chrome_options.binary_location = str(path_binary)
    chrome_options.headless = True
    chrome_options.add_argument("--no-sandbox")  # This make Chromium reachable
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def PrepareHeorkuDriver(GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH):
    from selenium.webdriver.chrome.options import Options


    chrome_options = Options()
    chrome_options.binary_location = GOOGLE_CHROME_PATH
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(
        executable_path=CHROMEDRIVER_PATH,
        options=chrome_options
    )
    return driver

def PrepareLocalChromeDriver(path_binary):
    """
    Create a Chrome Session
    :param path_ChromeBinary:
    :return:
    """
    logging.debug(f"ChromeBinary Path:{path_binary}")
    driver = webdriver.Chrome(path_binary)  # path to chromedriver
    return driver

def PrepareLocalFirefoxDriver(path_binary):
    """
    Create a Firefox Session
    :param path_FirefoxBinary:
    :return:
    """
    from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
    binary = FirefoxBinary(str(path_binary))
    driver = webdriver.Firefox(firefox_binary=binary)
    return driver



def handle_environment() -> (Path, webdriver):
    """
    Properly handle the environment by setting the two key variable: self.path_binary and self.driver.
    :return:
    """
    # If on travis, .travis.yml already took care of the dependency.
    if "TRAVIS" in os.environ:
        path_binary = Path(r"/usr/bin/google-chrome")
        assert path_binary.exists()
        logging.debug("TravisCI environment encountered.")

        return path_binary, PrepareTravisDriver(path_binary)

    if 'on_heroku' in os.environ:
        logging.debug("Heroku App environment encountered.")
        # Per Source: https://medium.com/@mikelcbrowne/running-chromedriver-with-python-selenium-on-heroku-acc1566d161c
        GOOGLE_CHROME_PATH = os.getenv("GOOGLE_CHROME_PATH")
        CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
        return GOOGLE_CHROME_PATH, PrepareHeorkuDriver(GOOGLE_CHROME_PATH, CHROMEDRIVER_PATH)  # Heroku uses GOOGLE_CHROME_PATH


    # Only local scenario going forward.
    if "browser_path" not in os.environ:
        message = "Browser path not specified!"
        logging.critical(message)
        raise ValueError(message)

    # Set the variable to check.
    path_binary = str(Path(os.getenv("browser_path"))).lower()
    assert Path(path_binary).exists()

    if "firefox" in path_binary:
        logging.debug("Local firefox environment encountered.")

        return path_binary, PrepareLocalFirefoxDriver(path_binary)
    elif "chrome" in path_binary:
        logging.debug("Local chrome Driver environment encountered.")
        return path_binary, PrepareLocalChromeDriver(path_binary)
    else:
        message = "Binary path does not contain firefox OR Chrome!"
        logging.critical(message)
        raise ValueError(message)
