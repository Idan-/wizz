import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time 

def get_driver():
    # Load credentials from environment variables
    username = os.getenv("WIZZ_USERNAME")
    password = os.getenv("WIZZ_PASSWORD")
    # if not username or not password:
    #     raise ValueError("Environment variables WIZZ_USERNAME and WIZZ_PASSWORD must be set")

    # Setup Chromium options
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')

    # Automatically download the correct ChromeDriver version
    service = Service(ChromeDriverManager().install())

    # Initialize WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Step 1: Open subscriptions page
    driver.get("https://multipass.wizzair.com/w6/subscriptions")

    # Step 2: Wait for login button and click it
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "CvoHeader-loginButton"))
    )
    login_button.click()

    # Step 3: Wait for username input to appear and fill credentials
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "username"))).send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)

    # Step 4: Submit login form
    driver.find_element(By.NAME, "password").submit()

    # Step 5: Wait for login to complete and cookies to appear
    WebDriverWait(driver, 15).until(
        lambda d: any(c['name'] == "laravel_session" for c in d.get_cookies())
    )

    cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()} # maybe will be in use in the future

    return driver


def get_flight_data(driver, FROM, TO, DATE):
    script = f"""
    return fetch("https://multipass.wizzair.com/en/w6/subscriptions/json/availability/60739699-ee6d-4039-b264-dda0652d828f", {{
        headers: {{
            "accept": "application/json",
            "content-type": "application/json"
        }},
        method: "POST",
        body: JSON.stringify({{
            flightType: "OW",
            origin: "{FROM}",
            destination: "{TO}",
            departure: "{DATE}",
            arrival: "",
            intervalSubtype: null
        }})
    }}).then(response => response.json());
    """

    result = driver.execute_async_script("""
        const callback = arguments[arguments.length - 1];
        fetch(arguments[0], {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Accept": "application/json"
            },
            body: JSON.stringify(arguments[1])
        })
        .then(response => response.json())
        .then(data => callback(data))
        .catch(err => callback({"error": err.toString()}));
    """, 
        "https://multipass.wizzair.com/en/w6/subscriptions/json/availability/60739699-ee6d-4039-b264-dda0652d828f",
        {
            "flightType": "OW",
            "origin": FROM,
            "destination": TO,
            "departure": DATE,
            "arrival": "",
            "intervalSubtype": None
        }
    )

    return result