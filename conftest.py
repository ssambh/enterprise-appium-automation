import pytest
import json
import os
import subprocess
import time
import tempfile
import zipfile
import shutil
from urllib import request as url_request
from urllib.error import URLError
from urllib.parse import urlparse

from appium import webdriver
from appium.options.common import AppiumOptions
import allure


def pytest_addoption(parser):
    parser.addini("env", "test environment")


@pytest.fixture(scope="session")
def env(request):
    return request.config.getini("env")


@pytest.fixture(scope="session")
def test_config(env):
    project_root = os.path.dirname(__file__)
    capabilities_path = os.path.join(project_root, 'config', 'capabilities.json')
    with open(capabilities_path) as f:
        all_configs = json.load(f)
    return all_configs[env]


@pytest.fixture(scope="session")
def app_path(test_config):
    """Downloads and unzips an app build, returning the path to the .app or .apk."""
    download_url = test_config.get("build_download_url")
    if not download_url:
        print("No build_download_url found. App will not be downloaded.")
        yield test_config.get("app") or test_config.get("appium:app")
        return

    tmpdir = tempfile.mkdtemp()
    try:
        downloaded_file_path = os.path.join(tmpdir, os.path.basename(download_url))
        print(f"Downloading app from {download_url}...")
        with url_request.urlopen(download_url) as response, open(downloaded_file_path, 'wb') as out_file:
            out_file.write(response.read())
        print(f"App downloaded to {downloaded_file_path}")

        final_app_path = downloaded_file_path

        if downloaded_file_path.endswith('.zip'):
            print(f"Unzipping {downloaded_file_path}...")
            with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            print("Searching for .app bundle...")
            found_path = None
            for root, dirs, files in os.walk(tmpdir):
                for dirname in dirs:
                    if dirname.endswith('.app'):
                        found_path = os.path.join(root, dirname)
                        break
                if found_path:
                    break

            if found_path:
                print(f"Found .app bundle at {found_path}")
                final_app_path = found_path
            else:
                pytest.fail("Could not find a .app file in the unzipped archive.")

        yield final_app_path

    finally:
        if os.path.exists(tmpdir):
            print(f"Cleaning up temporary directory: {tmpdir}")
            shutil.rmtree(tmpdir)


@pytest.fixture(scope="session")
def appium_service(test_config):
    appium_url = test_config.get('appium_server_url')
    parsed_url = urlparse(appium_url)
    if parsed_url.hostname not in ("localhost", "127.0.0.1"):
        print(f"Skipping local Appium server start for remote URL: {appium_url}")
        yield
        return

    print(f"Starting local Appium server...")
    appium_process = subprocess.Popen(['appium'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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

    print("Stopping local Appium server...")
    appium_process.terminate()
    appium_process.wait()


@pytest.fixture
def driver(test_config, appium_service, app_path):
    capabilities = test_config.copy()
    appium_server = capabilities.pop('appium_server_url', 'http://localhost:4723')
    capabilities.pop("build_download_url", None)
    if app_path:
        capabilities['appium:app'] = app_path

    options = AppiumOptions()
    options.load_capabilities(capabilities)
    driver_instance = webdriver.Remote(appium_server, options=options)
    yield driver_instance
    driver_instance.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed:
        if 'driver' in item.fixturenames:
            driver_instance = item.funcargs['driver']
            screenshot = driver_instance.get_screenshot_as_png()
            allure.attach(screenshot, name='screenshot_on_failure', attachment_type=allure.attachment_type.PNG)