from utils.base_page import BasePage

class BasePageIOS(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # You can add iOS-specific helper methods here in the future
    # For example:
    # def scroll_down(self):
    #     self.driver.execute_script("mobile: scroll", {"direction": "down"})
