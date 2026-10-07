"""
Launch visible Chrome browser, navigate to Dhofar University SIS, and autofill Staff ID.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def open_du_portal(username="001097"):
    chrome_options = Options()
    # Keep browser open after script completes
    chrome_options.add_experimental_option("detach", True)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("Navigating to https://web.du.edu.om/ords/f?p=2023 ...")
        driver.get("https://web.du.edu.om/ords/f?p=2023")
        
        # Wait for username input
        u_elem = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "P101_USERNAME"))
        )
        time.sleep(1)
        
        # Fill username and focus password
        driver.execute_script("""
            var u = document.getElementById('P101_USERNAME');
            var p = document.getElementById('P101_PASSWORD');
            if (u) {
                u.value = arguments[0];
                u.dispatchEvent(new Event('input', { bubbles: true }));
                u.dispatchEvent(new Event('change', { bubbles: true }));
            }
            if (p) {
                p.focus();
            }
        """, username)
        
        print("Autofilled Staff ID: 001097 and focused password field!")
        print("Browser is open on your screen.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    open_du_portal()
