from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options

from selenium.common.exceptions import StaleElementReferenceException
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import os
import logging

url_signin = "https://inscription.ymcaquebec.org/MyAccount/MyAccountUserLogin.asp?Referrer=&amp;AjaxRequest=true"
url_booking = "https://inscription.ymcaquebec.org/Facilities/FacilitiesSearchWizard.asp"
working_days = ["Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

load_dotenv(verbose=True)
logger = logging.getLogger()
logging.basicConfig(level=logging.INFO)

class AutomateBooking:

    def __init__(self):
        """
        :param path_binary: Binary to either Chrome self.driver or Firefox.
        """
        logger.debug("Main program path begings.")
        # If on travis, .travis.yml already took care of the dependency.
        if "TRAVIS" in os.environ:
            self.path_binary = Path(r"/usr/lib/chromium-browser/chromedriver")
        else:
            self.path_binary = Path(os.getenv("browser_path"))
        assert self.path_binary.exists()

        # Get the current date information:
        self.today = datetime.today()
        self.today = datetime.today()
        self.today_date = self.today.strftime("%d-%m-%y")
        self.today_day = self.today.strftime("%d").lstrip("0")
        self.today_month = self.today.strftime("%m").lstrip("0")
        self.today_year = self.today.strftime("%y")
        self.today_weekDay = self.today.strftime('%A')

        # Data check.
        if self.today_weekDay not in working_days:
            print("This app only runs between Tuesday and Saturday to grab the first spot of YMCA courts.")
            return

        self.driver: webdriver = None
        if "TRAVIS" in os.environ:
            self.PrepareTravisFireFoxDriver()
        elif "firefox" in str(self.path_binary).lower():
            self.PrepareFirefoxDriver()
        elif "chrome" in str(self.path_binary).lower():
            self.PrepareChromeDriver()
        else:
            raise ValueError("Binary path does not contain firefox OR Chrome!")
        
        self.driver.maximize_window()
        self.SignIn()
        self.InitiateSearch()
        self.ProcessResults()
        self.GoToCheckOut()
        book = int(os.getenv("CompleteTransaction"))

        if book == 1:
            self.CompleteTransaction()
        elif book == 0:
            logger.info("Mock completing transaction for debugging purposes!")
        else:
            logger.critical("Unreachable code detected. OS ENV variable CompleteTransaction may not have been set in the TravisCI test environment, or the HerokuApplication.")

        logger.debug("Main program path end reached.")

    def GoToCheckOut(self):
        self.driver.find_element_by_xpath('//*[@title="Click to Checkout"]').click()
        logger.info("Clicked on Checkout!")
        time.sleep(3)

    def CompleteTransaction(self):
        self.driver.find_element_by_id("completeTransactionButton").click()
        logger.info("Completed the transaction!")
        time.sleep(3)

    def PrepareTravisFireFoxDriver(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = Firefox(firefox_options=options)

    def PrepareChromeDriver(self):
        """
        Create a Chrome Session
        :param path_ChromeBinary:
        :return:
        """
        logger.info(self.path_binary)
        self.driver = webdriver.Chrome(self.path_binary)  # path to chromedriver

        time.sleep(5)

    def PrepareFirefoxDriver(self):
        """
        Create a Firefox Session
        :param path_FirefoxBinary:
        :return:
        """
        from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
        binary = FirefoxBinary(str(self.path_binary))
        self.driver = webdriver.Firefox(firefox_binary=binary)
        time.sleep(5)

    def SignIn(self):
        """
        Run the sign in operation.
        """
        self.driver.get(url_signin)

        str_barcode = os.getenv("barcode")
        str_PINID = os.getenv("PINID")
        ## sign in
        from selenium.common.exceptions import NoSuchElementException
        try:
            text_area_Login_ID = self.driver.find_element_by_id('ClientBarcode')
            text_area_Login_ID.send_keys(str_barcode)

            text_area_Account_Pin = self.driver.find_element_by_id('AccountPIN')
            text_area_Account_Pin.send_keys(str_PINID)

            login_submit_button = self.driver.find_element_by_id('Enter')
            login_submit_button.submit()
            logger.info("Sign in action complete!")

        except NoSuchElementException:
            raise (TimeoutError("It seems the YMCA website might be DOWN"))

    def Select_BookingSearch(self):
        """
        Choose Search Booking
        """
        field_facility_booking = self.driver.find_element_by_id("search-facbook-radio")
        field_facility_booking.click()

    def Select_FacilityFunction(self):
        """
        Select Badminton
        """
        try:
            field_facility_function = Select(self.driver.find_element_by_id("FacilityFunctions"))
            field_facility_function.select_by_visible_text('CV Badminton')
            #which_facility = Select(self.driver.find_element_by_name('FacilityFunctions'))
            #which_facility.select_by_value('49')
        except StaleElementReferenceException as Exception:
            field_facility_function = Select(self.driver.find_element_by_id("FacilityFunctions"))
            field_facility_function.select_by_visible_text('CV Badminton')
            # which_facility = Select(self.driver.find_element_by_name('FacilityFunctions'))
            # which_facility.select_by_value('49')

    def Select_Location(self):
        # Select Centre-Ville to avoid booking other places.
        field_centre = self.driver.find_element_by_xpath('//*[@title="Centre-ville"]')
        field_centre.click()

    def Select_SetDateRange(self):
        # Select today?
        from_day = Select(self.driver.find_element_by_name('DayFrom'))
        from_day.select_by_value(self.today_day)

        # Select this month?
        from_month = Select(self.driver.find_element_by_name('MonthFrom'))
        from_month.select_by_value(self.today_month)

        # Day to search for.
        till_date = int(self.today_day) + 3
        # Month to search for.
        till_month = int(self.today_month)
        if (int(self.today_month) in [1, 3, 5, 7, 8, 10, 12]):
            if (till_date > 31):
                till_date = till_date - 31
                till_month = till_month + 1
                if (till_month > 12):
                    till_month = till_month - int(from_month)
        if (int(self.today_month) in [4, 6, 9, 11]):
            if (till_date > 30):
                till_date = till_date - 30
                till_month = till_month + 1
        if (int(self.today_month) in [2]):
            if (till_date > 28):
                till_date = till_date - 28
                till_month = till_month + 1

        to_day = Select(self.driver.find_element_by_name('DayTo'))
        to_day.select_by_value(str(till_date).lstrip("0"))

        to_month = Select(self.driver.find_element_by_name('MonthTo'))
        to_month.select_by_value(str(till_month).lstrip("0"))

    def Select_Thurday(self):
        """
        Choose Thursday in the proper element ID.
        """
        select_day5 = self.driver.find_element_by_id('chkWeekDay5')
        select_day5.click()

    def Select_Saturday(self):
        """
        Choose Saturday in the proper element ID.
        """
        select_day7 = self.driver.find_element_by_id('chkWeekDay7')
        select_day7.click()

    def Select_ThursdayTime(self):
        """
        Select from 6 to 8 PM for Saturday to reduce number of rows to be parsed later on.
        :return:
        """
        TimeFrom = Select(self.driver.find_element_by_name('TimeFrom'))
        TimeFrom.select_by_value('9')

        # Select PM
        AMPMFrom = Select(self.driver.find_element_by_name('AMPMFrom'))
        AMPMFrom.select_by_value('1')

        TimeTo = Select(self.driver.find_element_by_name('TimeTo'))
        TimeTo.select_by_value('11')

        # Select PM
        AMPMTo = Select(self.driver.find_element_by_name('AMPMFrom'))
        AMPMTo.select_by_value('1')

    def Select_SaturdayTime(self):
        """
        Select from 6 to 8 PM for Saturday to reduce number of rows to be parsed later on.
        :return:
        """

        TimeFrom = Select(self.driver.find_element_by_name('TimeFrom'))
        TimeFrom.select_by_value('6')

        # Select PM
        AMPMFrom = Select(self.driver.find_element_by_name('AMPMFrom'))
        AMPMFrom.select_by_value('1')

        TimeTo = Select(self.driver.find_element_by_name('TimeTo'))
        TimeTo.select_by_value('8')

        # Select PM
        AMPMTo = Select(self.driver.find_element_by_name('AMPMFrom'))
        AMPMTo.select_by_value('1')

    def InitiateSearch(self):
        """
        Core function to initiate the search with the proper criteria to generate the list of table availability
        """

        self.driver.get(url_booking)
        time.sleep(5)  ## to get for loaded completly

        self.Select_BookingSearch()
        self.Select_FacilityFunction()
        self.Select_Location()
        self.Select_SetDateRange() # Required to ensure proper selection date/range for the next two steps.
        if self.today_weekDay in ["Tuesday", "Wednesday"]:
            self.Select_Thurday()
            self.Select_ThursdayTime()
        elif self.today_weekDay in ["Thursday", "Friday"]:
            self.Select_Saturday()
            self.Select_SaturdayTime()
        self.driver.find_element_by_name("Form_Criteria_Panel").submit()
        logger.info("Search action complete!")
        time.sleep(3)

    def ProcessResults(self):
        """
        Core Function to process the live search results and then find the right way to pass it to be booked.
        :return:
        """
        content = self.driver.page_source
        soup = BeautifulSoup(content, "html.parser")

        table = soup.find('table', attrs={'id': 'fac-search-results'})
        if table is None:
            raise PermissionError("It seems there are no known court availabilities. All courts might have been booked!! How?")


        table_body = table.find('tbody')

        rows = table_body.find_all('tr')

        if self.today_weekDay in ["Tuesday", "Wednesday"]:
            # Thursday row Count
            thursdayCourt = ''
            for row in rows:
                cols = row.find_all('td')
                if (cols[2].find(text=True) == 'Thu' and cols[4].find(text=True) == '21:10-22:10'):
                    thursdayCourt = cols[6].find('input').get('name')
                    break
            logger.info(thursdayCourt)
            logger.info("Thursday search complete!")
            if (thursdayCourt != ''):
                select_court = self.driver.find_element_by_id(thursdayCourt)
                select_court.click()


        elif self.today_weekDay in ["Thursday", "Friday"]:
            saturdayCourt = ''
            # Saturday row Count
            for row in rows:
                cols = row.find_all('td')
                if (cols[2].find(text=True) == 'Sat' and cols[4].find(text=True) == '18:30-19:30'):
                    saturdayCourt = cols[6].find('input').get('name')
                    break
            print(saturdayCourt)
            logger.info("Saturday search complete!")
            if (saturdayCourt != ''):
                select_court = self.driver.find_element_by_id(saturdayCourt)
                select_court.click()

        time.sleep(5)
        self.driver.find_element_by_id('AddBookTop').click()
        logger.info("Add booking to card complete!")
        time.sleep(5)

if __name__=="__main__":
    testBooking = AutomateBooking()
