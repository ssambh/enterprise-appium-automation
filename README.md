# Enterprise Appium Automation

This is a Python-based Appium automation framework for testing mobile applications.

## Project Structure

- `config/capabilities.json`: Defines the capabilities for different test environments (e.g., local emulator, real device, cloud provider).
- `conftest.py`: Pytest configuration file for setting up the Appium driver fixture.
- `pytest.ini`: Pytest configuration file for defining custom markers and setting the test environment.
- `requirements.txt`: Lists the Python dependencies for this project.
- `README.md`: This file.

## Getting Started

### Prerequisites

- Python 3.x
- Node.js and npm
- Appium

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```

2. **Create and activate a virtual environment:**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

1. **Select the test environment:**

   Open the `pytest.ini` file and set the `env` variable to the desired environment from `config/capabilities.json` (e.g., `local_android_emulator`).

2. **Run the tests:**

   ```bash
   pytest
   ```

   You can also run specific tests using markers:

   ```bash
   pytest -m smoke
   pytest -m regression
   ```
