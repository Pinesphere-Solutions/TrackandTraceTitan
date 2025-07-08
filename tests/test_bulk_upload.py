import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

# Configure logging
logging.basicConfig(
    filename='bulk_upload_test.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

class BulkUploadTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.driver.implicitly_wait(10)
        cls.base_url = "http://192.168.1.5:8000/dayplanning/bulk_upload/"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def log_and_print(self, msg):
        print(msg)
        logging.info(msg)

    def test_single_upload_and_submit(self):
        driver = self.driver
        wait = WebDriverWait(driver, 10)
        driver.get(self.base_url)
        self.log_and_print("Opened Bulk Upload page.")

        wait.until(EC.element_to_be_clickable((By.ID, "add-model-btn"))).click()
        self.log_and_print("Clicked Single Upload button.")

        wait.until(EC.visibility_of_element_located((By.ID, "data-table-section")))
        self.log_and_print("Data table is visible.")

        try:
            row_xpath = "//tbody/tr[1]"

            def fill_input(cell_index, value, label):
                for attempt in range(3):
                    try:
                        row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
                        cell = row.find_elements(By.TAG_NAME, "td")[cell_index]
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cell)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", cell)
                        time.sleep(0.4)
                        row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
                        cell = row.find_elements(By.TAG_NAME, "td")[cell_index]
                        input_elem = WebDriverWait(cell, 2).until(
                            lambda c: c.find_element(By.TAG_NAME, "input")
                        )
                        input_elem.clear()
                        input_elem.send_keys(value)
                        self.log_and_print(f"Entered {label}: {value}")
                        time.sleep(0.5)
                        return
                    except Exception as e:
                        if attempt < 2:
                            time.sleep(0.6)
                        else:
                            raise e

            def select_dropdown(cell_index, label, match_text=None):
                for attempt in range(3):
                    try:
                        row = wait.until(EC.presence_of_element_located((By.XPATH, row_xpath)))
                        cell = row.find_elements(By.TAG_NAME, "td")[cell_index]
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", cell)
                        time.sleep(0.2)
                        driver.execute_script("arguments[0].click();", cell)
                        try:
                            select_elem = cell.find_element(By.TAG_NAME, "select")
                        except:
                            select_elem = wait.until(EC.presence_of_element_located((By.TAG_NAME, "select")))
                        found = False
                        for option in select_elem.find_elements(By.TAG_NAME, "option"):
                            if match_text and option.text.strip().lower() == match_text.lower():
                                option.click()
                                self.log_and_print(f"Selected {label}: {option.text}")
                                found = True
                                break
                        if not found:
                            for option in select_elem.find_elements(By.TAG_NAME, "option"):
                                val = option.get_attribute("value")
                                if val and val.strip() and "select" not in option.text.lower():
                                    option.click()
                                    self.log_and_print(f"Selected {label} fallback: {option.text}")
                                    found = True
                                    break
                        if not found:
                            raise Exception(f"No valid option found for {label}")
                        time.sleep(0.5)
                        return
                    except Exception as e:
                        if attempt < 2:
                            time.sleep(0.6)
                        else:
                            raise e

            fill_input(1, "1805SSA02", "Plating Stk No")
            fill_input(2, "1805XSA02", "Polishing Stk No")
            fill_input(3, "IPS", "Plating Colour")
            select_dropdown(4, "Category")
            fill_input(5, "45", "Input Qty")
            select_dropdown(6, "Source", match_text="Testing")

            # 🔽 ADDITION: Repeat for 9 more rows (total 10 rows)
            for i in range(9):
                plus_icon = wait.until(EC.element_to_be_clickable((By.XPATH, "//i[contains(@class,'fa-plus')]")))
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", plus_icon)
                plus_icon.click()
                time.sleep(0.6)
                self.log_and_print(f"Clicked + to add row {i+2}")

                row_xpath = f"//tbody/tr[{i+2}]"
                fill_input(1, "1805SSA02", "Plating Stk No")
                fill_input(2, "1805XSA02", "Polishing Stk No")
                fill_input(3, "IPS", "Plating Colour")
                select_dropdown(4, "Category")
                fill_input(5, "45", "Input Qty")
                select_dropdown(6, "Source", match_text="Testing")

        except Exception as e:
            self.log_and_print(f"❌ Error while entering data: {e}")
            raise

        submit_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Submit')]")))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
        time.sleep(0.4)
        submit_btn.click()
        self.log_and_print("Clicked Submit.")

        time.sleep(1)
        try:
            error_modal = driver.find_element(By.CLASS_NAME, "swal2-html-container")
            error_msg = error_modal.text.strip()
            if error_msg:
                script = f'alert("Submission Failed\\n❌ {error_msg}");'
                driver.execute_script(script)
                self.log_and_print(f"❌ Submission failed: {error_msg}")
                self.fail("Form submission failed.")
        except:
            pass

        wait.until(EC.url_contains("/adminportal/index"))
        current_url = driver.current_url
        if "/adminportal/index" in current_url:
            self.log_and_print("✅ Successfully redirected to /adminportal/index/")
        else:
            self.log_and_print(f"❌ Not redirected properly. Current URL: {current_url}")
            self.fail("Submit did not redirect as expected.")

if __name__ == "__main__":
    unittest.main()
