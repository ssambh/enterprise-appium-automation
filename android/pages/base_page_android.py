from utils.base_page import BasePage

class BasePageAndroid(BasePage):
    def __init__(self, driver):
        super().__init__(driver)

    # You can add Android-specific helper methods here in the future
    # For example:
    # def scroll_to_text(self, text):
    #     # Android-specific scroll logic
    #     pass
