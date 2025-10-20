import pytest
import json
import os
import subprocess
import time
import tempfile
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
def app_path(test_config):
    """Downloads the app build and returns the path."""
    download_url = test_config.get("build_download_url")
    if not download_url:
        # If no download URL is specified, assume the app is pre-installed or path is in caps
        print("No build_download_url found. App will not be downloaded.")
        # Check for a hardcoded app path in the config as a fallback
        hardcoded_app_path = test_config.get("app") or test_config.get("appium:app")
        if hardcoded_app_path:
            yield hardcoded_app_path
        else:
            # If no app path at all, yield None. Appium will use appPackage/appActivity.
            yield None
        return

    # Download the app to a temporary file
    print(f"Downloading app from {download_url}...")
    with tempfile.NamedTemporaryFile(suffix=".apk", delete=False) as tmp_file:
        with url_request.urlopen(download_url) as response:
            tmp_file.write(response.read())
        downloaded_app_path = tmp_file.name
        print(f"App downloaded to {downloaded_app_path}")

    yield downloaded_app_path

    # Teardown: clean up the downloaded file
    if 'downloaded_app_path' in locals():
        print(f"Cleaning up downloaded app: {downloaded_app_path}")
        os.remove(downloaded_app_path)


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
def driver(test_config, appium_service, app_path):
    """Creates the Appium webdriver instance."""
    capabilities = test_config.copy()
    appium_server = capabilities.pop('appium_server_url', 'http://localhost:4723')
    
    # Remove our custom key and set the app path from our download fixture
    capabilities.pop("build_download_url", None)
    if app_path:
        capabilities['appium:app'] = app_path

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
        if 'driver' in item.fixturenames:
            driver_instance = item.funcargs['driver']
            screenshot = driver_instance.get_screenshot_as_png()
            allure.attach(screenshot, name='screenshot_on_failure', attachment_type=allure.attachment_type.PNG)