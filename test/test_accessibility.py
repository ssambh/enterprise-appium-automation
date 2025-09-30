import allure
import pytest

from pages.HomePage import HomePage
from pages.accessibility_page import AccessibilityPage

allure.feature("Testing the Accessibility feature")
class TestingAccessibility:

    # This test is part of the 'smoke' suite.
    @pytest.mark.smoke
    @pytest.mark.regression
    # The test function automatically receives the 'driver' from conftest.py.
    def test_app_launch(self, driver):
        allure.dynamic.title("Testing app launch")
        """
        A simple test to verify that the app launches successfully.
        """
        pass

    @pytest.mark.smoke
    @pytest.mark.regression
    def test_accessibility_node_provider(self, driver):
        allure.dynamic.title("Testing accessibility node provider")
        obj_home_page = HomePage(driver)
        obj_accessibility_page = AccessibilityPage(driver)

        obj_home_page.click_accessibility_btn()
        obj_accessibility_page.validate_accessibility_node_provider_btn()

    @pytest.mark.smoke
    def test_accessibility_node_querying(self, driver):
        allure.dynamic.title("Testing Accessibility node querying")
        obj_home_page = HomePage(driver)
        obj_accessibility_page = AccessibilityPage(driver)

        obj_home_page.click_accessibility_btn()
        obj_accessibility_page.validate_accessibility_node_querying_btn()