import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException

class FandomEditor:
    def __init__(self):
        self.driver = self.initialize_browser()
        self.logged_in = False

    def initialize_browser(self):
        service = webdriver.chrome.service.Service(executable_path="chromedriver.exe")
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.set_capability('pageLoadStrategy', "eager")
        return webdriver.Chrome(service=service, options=options)

    def login_to_fandom(self, username, password):
        self.driver.get('https://auth.fandom.com/signin?flow=7b6a4faa-9098-4b27-b6b7-01ad0d605e26')
        login_field = self.driver.find_element(by=By.ID, value="identifier")
        password_field = self.driver.find_element(by=By.ID, value="password")
        login_field.send_keys(username)
        password_field.send_keys(password)
        login_button = self.driver.find_element(by=By.XPATH, value="//button[@class='wds-button Submit_button__2u2G7']")
        login_button.click()
        self.logged_in = True

    def navigate_to_page(self, url):
        self.driver.get(url)
        time.sleep(5)
        try:
            enter_button = self.driver.find_element(by=By.XPATH, value="//span[@class='oo-ui-widget oo-ui-widget-enabled oo-ui-buttonElement oo-ui-buttonElement-framed oo-ui-labelElement oo-ui-flaggedElement-primary oo-ui-flaggedElement-progressive oo-ui-buttonWidget oo-ui-actionWidget']")
            enter_button.click()
        except NoSuchElementException:
            print('Кнопка "Сохранить" не была найдена')

    def edit_text(self, filename):
        editable_element = self.driver.find_element(by=By.XPATH,
                                                    value="//div[@class='ve-ce-branchNode ve-ce-documentNode ve-ce-attachedRootNode ve-ce-rootNode mw-content-ltr mw-parser-output mw-show-empty-elt ve-ce-documentNode-codeEditor-webkit-hide']")
        paragraph_element = editable_element.find_element(by=By.XPATH,
                                                          value=".//p[@class='ve-ce-branchNode ve-ce-contentBranchNode ve-ce-paragraphNode']")
        with open(filename, 'r', encoding='utf-8') as f:
            new_text = f.read()
        time.sleep(1)
        paragraph_element.send_keys(Keys.CONTROL + "a")
        time.sleep(1)
        paragraph_element.send_keys(Keys.DELETE)
        for line in new_text.splitlines():
            paragraph_element.send_keys(line)
            paragraph_element.send_keys(Keys.ENTER)
            time.sleep(0.1)

    def save_changes(self):
        save_button = self.driver.find_element(by=By.XPATH, value="//button[.//span[text()='Сохранить']]")
        self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Сохранить']]")))
        try:
            save_button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].scrollIntoView();", save_button)
            save_button.click()
        time.sleep(2)

    def edit_and_save_text(self, url, filename, username, password):
        if not self.logged_in:
            self.login_to_fandom(username, password)
        self.navigate_to_page(url)
        self.edit_text(filename)
        self.save_changes()

    def __del__(self):
        self.driver.quit()
