# Import the locator strategies (e.g., ID, ACCESSIBILITY_ID) from Appium.
import allure
from appium.webdriver.common.appiumby import AppiumBy
# Import the BasePage so our new class can inherit from it.
from pages.base_page import BasePage

class HomePage(BasePage):

    def __init__(self,driver):
        super().__init__(driver)

    accessibility_btn = (AppiumBy.ACCESSIBILITY_ID,'Access\'ibility')

    @allure.step("Click the Accessibility button")
    def click_accessibility_btn(self):
        self.click(self.accessibility_btn)



