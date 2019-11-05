'''
Created on Oct 2, 2019

@author: sourav2910
'''
from selenium import webdriver
from bs4 import BeautifulSoup

from datetime import datetime

from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException

import time


driver = webdriver.Chrome("C:\InstalledSoftwares\Python_packages\chromedriver_win32\chromedriver.exe") # path to chromedriver

driver.get("https://inscription.ymcaquebec.org/MyAccount/MyAccountUserLogin.asp?Referrer=&amp;AjaxRequest=true")

## sign in
text_area_Login_ID = self.driver.find_element_by_id('ClientBarcode')
text_area_Login_ID.send_keys("") # add client ID

text_area_Account_Pin = self.driver.find_element_by_id('AccountPIN')
text_area_Account_Pin.send_keys("") # add password

login_submit_button = self.driver.find_element_by_id('Enter')
login_submit_button.submit()

## court Reservation form
driver.get("https://inscription.ymcaquebec.org/Facilities/FacilitiesSearchWizard.asp")

facility_booking = self.driver.find_element_by_id('search-facbook-radio')
facility_booking.click()


time.sleep(5) ## to get for loaded completly

today = datetime.today()

today_date = today.strftime("%d-%m-%y")

today_day = today.strftime("%d")
today_month = today.strftime("%m")
today_year = today.strftime("%y")
today_weekDay = today.strftime('%A')
  
     
     
from_day = Select(driver.find_element_by_name('DayFrom'))
from_day.select_by_value(today_day.lstrip("0"))
     
from_month = Select(driver.find_element_by_name('MonthFrom'))
from_month.select_by_value(today_month.lstrip("0"))
 
till_date =  int(today_day) + 3
till_month =  int(today_month)
if (int(today_month) in [1,3,5,7,8,10,12]):
    if(till_date > 31):
        till_date  = till_date - 31
        till_month = till_month + 1
        if(till_month>12):
            till_month = till_month - int(from_month)
if (int(today_month) in [4,6,9,11]):
    if(till_date > 30):
        till_date  = till_date - 30
        till_month = till_month + 1
if (int(today_month) in [2]):
    if(till_date > 28):
        till_date  = till_date - 28 
        till_month = till_month + 1       
  
# from_year = Select(driver.find_element_by_name('YearFrom'))
# from_year.select_by_value(today_year)
     
to_day = Select(driver.find_element_by_name('DayTo'))
to_day.select_by_value(str(till_date).lstrip("0"))
      
to_month = Select(driver.find_element_by_name('MonthTo'))
to_month.select_by_value(str(till_month).lstrip("0"))
      
# to_year = Select(driver.find_element_by_name('YearTo'))
# to_year.select_by_value(today_year)
#      

select_day5 = self.driver.find_element_by_id('chkWeekDay5')
select_day5.click()
select_day7 = self.driver.find_element_by_id('chkWeekDay7')
select_day7.click()


TimeFrom = Select(driver.find_element_by_name('TimeFrom'))
TimeFrom.select_by_value('6')

AMPMFrom = Select(driver.find_element_by_name('AMPMFrom'))
AMPMFrom.select_by_value('1')

TimeTo = Select(driver.find_element_by_name('TimeTo'))
TimeTo.select_by_value('11')

AMPMTo = Select(driver.find_element_by_name('AMPMFrom'))
AMPMTo.select_by_value('1')

try:
    which_facility = Select(driver.find_element_by_name('FacilityFunctions'))
    which_facility.select_by_value('49')
except StaleElementReferenceException as Exception:
    which_facility = Select(driver.find_element_by_name('FacilityFunctions'))
    which_facility.select_by_value('49')


driver.find_element_by_name("Form_Criteria_Panel").submit()

time.sleep(10)

content = self.driver.page_source
soup = BeautifulSoup(content,"html.parser")

table = soup.find('table', attrs={'id':'fac-search-results'})
table_body = table.find('tbody')

rows = table_body.find_all('tr')

## THursday row Count

thursdayCourt = ''
saturdayCourt = ''
for row in rows:
    cols = row.find_all('td')
    if (cols[2].find(text=True) == 'Thu' and cols[4].find(text=True) == '21:10-22:10'):
        thursdayCourt =  cols[6].find('input').get('name')
        break
## Saturday row Count    

for row in rows:
    cols = row.find_all('td')
    if (cols[2].find(text=True) == 'Sat' and cols[4].find(text=True) == '18:30-19:30'):
        saturdayCourt = cols[6].find('input').get('name')
        break
            
print(thursdayCourt)
print(saturdayCourt)

if (thursdayCourt != ''):
    select_court = self.driver.find_element_by_id(thursdayCourt)
    select_court.click()
if (saturdayCourt != ''): 
    select_court = self.driver.find_element_by_id(saturdayCourt)
    select_court.click()   

time.sleep(5)    
driver.find_element_by_id('AddBookTop').click()

