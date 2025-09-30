import pytest
import json
import os
from appium import webdriver
from appium.options.common import AppiumOptions
# Import allure to handle attachments.
import allure

def pytest_addoption(parser):
    parser.addini("env", "test environment")

@pytest.fixture(scope="session")
def env(request):
    return request.config.getini("env")

@pytest.fixture
def driver(env):#This method depends on env() function
    # Get the absolute path to the project's root directory
    project_root = os.path.dirname(__file__)
    # Construct the absolute path to the capabilities.json file
    capabilities_path = os.path.join(project_root, 'config', 'capabilities.json')

    with open(capabilities_path) as f:
        capabilities = json.load(f)[env]
    options = AppiumOptions()
    options.load_capabilities(capabilities)
    appium_server = 'http://localhost:4723' if 'local' in env else None
    driver_instance = webdriver.Remote(appium_server, options=options)
    # This will pass the driver instance to the tests
    yield driver_instance
    # --- TEARDOWN ---This will automatically run after the test execution
    driver_instance.quit()

# This is a pytest hook that runs after each test finishes.
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to obtain the report object.
    outcome = yield
    report = outcome.get_result()

    # We only look at the report from the "call" phase (the actual test execution).
    if report.when == 'call' and report.failed:
        # 'item' is the test item that just ran. 'driver' is the name of our fixture.
        if 'driver' in item.fixturenames:
            # Get the driver instance from the test item.
            driver_instance = item.funcargs['driver']
            # Take a screenshot.
            screenshot = driver_instance.get_screenshot_as_png()
            # Attach the screenshot to the Allure report.
            allure.attach(screenshot, name='screenshot_on_failure', attachment_type=allure.attachment_type.PNG)