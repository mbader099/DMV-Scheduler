from concurrent import futures

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from time import sleep
from datetime import datetime
import maps
import time
import threading
import os
from objects import dmvappt
from objects.dmvappt import DMVAppt

knowledge_test_locations = []
motorcycle_skills_test_locations = []
drivers_license_skills_test_locations = []

DEBUG = False


class Scheduler:
    def __init__(self):
        # Lock to prevent thread race conditions at the end when it adds to the list of appts
        self._lock = threading.Lock()
        self.appts = []

    def searchLocationForAppointments(self, loc, startdate, enddate):
        firefoxConfig = webdriver.FirefoxOptions()

        if not DEBUG:
            firefoxConfig.headless = True

        browserdriver = webdriver.Firefox(executable_path=GeckoDriverManager().install(),
                                          service_log_path=os.path.devnull, firefox_options=firefoxConfig)
        dmv_appointments = []

        # Open browser to location link
        browserdriver.get(f"https://vadmvappointments.as.me/schedule.php?calendarID={loc}")

        # Go through all categories
        categories = browserdriver.find_elements_by_xpath(
            "//label[contains(normalize-space(@class), 'category-label')]")

        # Ensure drop down is closed prior to continuing
        if len(browserdriver.find_elements_by_xpath(
                "//div[contains(normalize-space(@class), 'select-category closed')]")) > 0:
            categories[0].click()

        for category in categories:
            category.click()

            # Get Category Information
            categoryId = category.get_attribute("for").replace("categoryType-", "")
            categoryName = category.text

            # Go through all appointment types
            apptTypes = browserdriver.find_elements_by_xpath(
                f"//div[contains(normalize-space(@class), 'select-item-box select-item from-category-{categoryId}')]")

            # Ensure drop down is closed prior to continuing
            if len(browserdriver.find_elements_by_xpath(
                    "//div[contains(normalize-space(@class), 'select-type closed')]")) > 0:
                apptTypes[0].click()

            for apptType in apptTypes:
                # Get Appointment Type Information
                apptTypeLabel = apptType.find_element_by_tag_name("label")
                apptTypeName = apptTypeLabel.text
                apptTypeId = apptTypeLabel.get_attribute("for").replace("appointmentType-", "")

                try:
                    apptTypeDesc = apptType.find_element_by_class_name("type-description").text
                except NoSuchElementException:
                    apptTypeDesc = ""

                # Look up all available appointment time slots between startdate and enddate
                apptType.click()

                # Loop through all available months
                try:
                    monthSelector = WebDriverWait(browserdriver, timeout=2).until(
                        lambda w: w.find_element_by_xpath("//select[@id='chooseMonthSched']"))
                    selectedMonthOption = monthSelector.find_element_by_xpath("//option[@selected='selected']")
                    selectedMonth = datetime.strptime(selectedMonthOption.get_attribute("value"), "%Y-%m-%d").date()
                except TimeoutError:
                    self._lock.acquire()
                    self.appts.extend(dmv_appointments)
                    self._lock.release()
                    return

                while (selectedMonth.year < enddate.year or
                       (selectedMonth.year == enddate.year and selectedMonth.month <= enddate.month)):
                    # Loop through all available days
                    dayTds = browserdriver.find_elements_by_xpath(
                        "//td[contains(normalize-space(@class), 'scheduleday activeday')]")

                    for dayTd in dayTds:
                        date = dayTd.get_attribute("day")
                        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
                        if startdate <= parsed_date <= enddate:
                            dayTd.click()

                            # Go through all open appointment time slots
                            # Make sure it has actually opened before continuing
                            try:
                                WebDriverWait(browserdriver, timeout=2).until(
                                    lambda w: w.find_element_by_xpath(
                                        "//input[contains(normalize-space(@class), 'time-selection')]").get_attribute("data-readable-date") == date
                                )
                                time_options = browserdriver.find_elements_by_xpath("//input[contains(normalize-space(@class), 'time-selection')]")
                            except TimeoutError:
                                print(f"ERROR: OPEN TIME SLOTS NOT FOUND")
                                time_options = []
                            i = 0
                            for timeLabel in time_options:
                                timeStr = timeLabel.get_attribute("value")
                                print(f"{date} [{i}]: Time Label Text is {timeStr}")
                                try:
                                    date_time = datetime.strptime(timeStr, "%Y-%m-%d %H:%M")
                                except ValueError:
                                    print(f"ERROR: {date} [{i}]: Time not found: {timeStr}")
                                    i += 1
                                    continue

                                i += 1
                                # Create appointment
                                appt = DMVAppt(date_time, 0, loc, categoryId, categoryName, apptTypeId, apptTypeName,
                                               apptTypeDesc)
                                dmv_appointments.append(appt)
                                # # Close time selection
                            # try:
                            #     close_time = browserdriver.find_element_by_xpath("//div[@class='choose-date']").click()
                            # except NoSuchElementException:
                            #     close_time = ''

                    # Select next month
                    monthSelector.click()
                    monthSelector.find_element_by_xpath(
                        "//option[@selected='selected']/following-sibling::option").click()

                    # Wait until calendar refreshes, then fetch element
                    try:
                        monthSelector = WebDriverWait(browserdriver, timeout=2).until(
                            lambda w: w.find_element_by_xpath("//select[@id='chooseMonthSched']"))
                        selectedMonthOption = monthSelector.find_element_by_xpath("//option[@selected='selected']")
                        selectedMonth = datetime.strptime(selectedMonthOption.get_attribute("value"), "%Y-%m-%d").date()
                    except TimeoutError:
                        browserdriver.quit()
                        self._lock.acquire()
                        self.appts.extend(dmv_appointments)
                        self._lock.release()
                        return

                apptType.click()

            category.click()

        browserdriver.quit()
        self._lock.acquire()
        self.appts.extend(dmv_appointments)
        self._lock.release()
        return

    def searchForAppointments(self, locations, startdate, enddate):
        self.appts = []

        if not DEBUG:
            # Multi-threading to improve performance
            with futures.ThreadPoolExecutor(max_workers=5) as executor:
                # Loop through all selected locations
                for loc in locations:
                    executor.submit(self.searchLocationForAppointments,
                                    loc, startdate, enddate)
        else:
            for loc in locations:
                self.searchLocationForAppointments(loc, startdate, enddate)

        # Return this data to user as a table/JSON format to be presented on the front end
        return self.appts
