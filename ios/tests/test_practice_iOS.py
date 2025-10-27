import allure
import pytest

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