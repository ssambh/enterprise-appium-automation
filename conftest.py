import pytest
import json
import os
import subprocess
import time
from urllib import request as url_request
from urllib.error import URLError

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
def appium_service():
    """Starts and stops the Appium server."""
    # Start the Appium server
    appium_process = subprocess.Popen(
        ['appium'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Wait for the server to be ready
    print(".....Waiting for Appium server to start.....")
    url = "http://localhost:4723/status"
    timeout = 60
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with url_request.urlopen(url) as response:
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
    print(".....Stopping Appium server.....")
    appium_process.terminate()
    appium_process.wait()


@pytest.fixture
def driver(env, appium_service):  # Add appium_service dependency
    # Get the absolute path to the project's root directory
    project_root = os.path.dirname(__file__)
    # Construct the absolute path to the capabilities.json file
    capabilities_path = os.path.join(project_root, 'config', 'capabilities.json')

    with open(capabilities_path) as f:
        capabilities = json.load(f)[env]
    options = AppiumOptions()
    options.load_capabilities(capabilities)
    appium_server = 'http://localhost:4723'
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

    # We only look at the report from the 