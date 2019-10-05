from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support.ui import Select
from time import time
from datetime import date

# Create a Firefox Session
binary = FirefoxBinary(r'C:\Program Files\Mozilla Firefox\firefox.exe')
driver = webdriver.Firefox(firefox_binary=binary)

driver.implicitly_wait(30)
driver.maximize_window()

driver.get("https://inscription.ymcaquebec.org/Facilities/FacilitiesSearchWizard.asp")

# Type in search date.

field_facility_booking = driver.find_element_by_id("search-facbook-radio")
field_facility_booking.click()

field_facility_function = Select(driver.find_element_by_id("FacilityFunctions"))
field_facility_function.select_by_visible_text('CV Badminton')


field_centre = driver.find_element_by_xpath('//*[@title="Centre-ville"]')
field_centre.click()

# Get the current date:
today = date.today()
print(f"{today.year}, {today.day}, {today.month}")

date_operations = [
    ("YearFrom", today.year),
    ("MonthFrom", today.strftime("%b")),
    ("DayFrom", today.day),
    ("YearTo", today.year),
    ("MonthTo", today.strftime("%b")),
    ("DayTo", today.day),
]

for operation in date_operations:
    field_year = Select(driver.find_element_by_id(operation[0]))
    field_year.select_by_visible_text(str(operation[1]))



"""

field_search.send_keys("Selenium WebDriver Interview")
field_search.submit()

lists = driver.find_element_by_class_name("_Rm")
print(lists)
for listitem in lists:
    #do somethin
"""
#dri
# ver.quit()