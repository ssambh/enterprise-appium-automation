from operator import truediv

import allure
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)


    def wait_for_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))


    def click(self, locator):
        self.wait_for_element(locator).click()


    def send_keys(self, locator, text):
        element = self.wait_for_element(locator)
        element.clear()
        element.send_keys(text)

    def is_checkbox_checked(self,webelement):
        if webelement.is_selected():
            return True
        else:
            return False