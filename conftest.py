import pytest
import json
import os
import subprocess
import time
from urllib import request as url_request
from urllib.error import URLError
from urllib.parse import urlparse

from appium import webdriver
from appium.options.common import AppiumOptions
# Import allure to handle attachments.
import allure


def pytest_addoption(parser):
    parser.addini("env", "test environment")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getini("env")


@pytest.fixture(scope="session")
def test_config(env):
    """Loads the configuration for the selected environment."""
    project_root = os.path.dirname(__file__)
    capabilities_path = os.path.join(project_root, 'config', 'capabilities.json')
    with open(capabilities_path) as f:
        all_configs = json.load(f)
    return all_configs[env]


@pytest.fixture(scope="session")
def appium_service(test_config):
    """Starts and stops a local Appium server if required by the configuration."""
    appium_url = test_config.get('appium_server_url')

    # Only start a local server if the URL points to localhost
    parsed_url = urlparse(appium_url)
    if parsed_url.hostname not in ("localhost", "127.0.0.1"):
        print(f"Skipping local Appium server start for remote URL: {appium_url}")
        yield
        return

    # Start the Appium server process
    print(f"Starting local Appium server...")
    appium_process = subprocess.Popen(
        ['appium'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for the server to be ready by polling its status endpoint
    status_url = appium_url.rstrip('/') + '/status'
    timeout = 60
    start_time = time.time()
    print(f"Waiting for Appium server to be ready at {status_url}...")
    while time.time() - start_time < timeout:
        try:
            with url_request.urlopen(status_url) as response:
                if response.status == 200:
                    print("Appium server started successfully.")
                    break
        except URLError:
            time.sleep(1)
    else:
        # If the loop completes without breaking, the server did not start
        appium_process.terminate()
        stdout, stderr = appium_process.communicate()
        print(f"Appium stdout:\n{stdout}")
        print(f"Appium stderr:\n{stderr}")
        pytest.fail(f"Appium server did not start within {timeout} seconds.")

    yield

    # Stop the Appium server
    print("Stopping local Appium server...")
    appium_process.terminate()
    appium_process.wait()


@pytest.fixture
def driver(test_config, appium_service):
    """Creates the Appium webdriver instance."""
    # Make a copy so we can modify it without affecting other fixtures
    capabilities = test_config.copy()

    # Pop the custom server URL capability so it's not passed to Appium
    appium_server = capabilities.pop('appium_server_url', 'http://localhost:4723')

    options = AppiumOptions()
    options.load_capabilities(capabilities)

    driver_instance = webdriver.Remote(appium_server, options=options)
    yield driver_instance

    # --- TEARDOWN ---
    driver_instance.quit()


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
