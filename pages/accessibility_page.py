import allure
from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class AccessibilityPage(BasePage):
    def __init__(self,driver):
        self.driver = driver
        super().__init__(driver)

    #Accessibility page home buttons
    accessibility_node_provider_btn = (AppiumBy.ACCESSIBILITY_ID,'Accessibility Node Provider')
    accessibility_node_querying_btn = (AppiumBy.ACCESSIBILITY_ID, 'Accessibility Node Querying')
    accessibility_service_btn = (AppiumBy.ACCESSIBILITY_ID, 'Accessibility Service')
    accessibility_custom_view_btn = (AppiumBy.ACCESSIBILITY_ID, 'Custom View')
    #accessibility node provider page objects
    accessibility_node_provider_text = (AppiumBy.ACCESSIBILITY_ID, 'Enable TalkBack and Explore-by-touch from accessibility settings. Then touch the colored squares.')
    #Accessibility node querying page objects
    accessibility_node_querying_text = (AppiumBy.ACCESSIBILITY_ID, '1. Enable QueryBack (Settings -> Accessibility -> QueryBack). \n\n2. Enable Explore-by-Touch (Settings -> Accessibility -> Explore by Touch). \n\n3. Touch explore the list.')
    #accessibility_node_querying_take_out_trash_checkbox = (AppiumBy.XPATH, '(//android.widget.CheckBox[@resource-id="io.appium.android.apis:id/tasklist_finished"])[1]')
    #accessibility_node_querying_do_laundry_checkbox = (AppiumBy.XPATH, '(//android.widget.CheckBox[@resource-id="io.appium.android.apis:id/tasklist_finished"])[2]')
    accessibility_node_querying_checkboxes = (AppiumBy.ID,'io.appium.android.apis:id/tasklist_finished')

    @allure.step("Validating the Accessibility node provider page")
    def validate_accessibility_node_provider_btn(self):
        self.click(self.accessibility_node_provider_btn)
        self.wait_for_element(self.accessibility_node_provider_text)

    @allure.step("Validating Accessibility node querying page")
    def validate_accessibility_node_querying_btn(self):
        self.click(self.accessibility_node_querying_btn)
        self.wait_for_element(self.accessibility_node_querying_text)
        all_checkboxes = self.driver.find_elements(*self.accessibility_node_querying_checkboxes)
        for checkbox in all_checkboxes:
            if self.is_checkbox_checked(checkbox):
                checkbox.click()
