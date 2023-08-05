import time
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC





class Auth0:

    def __init__(self, email_address: str, password: str, proxy: str = None, mfa: str = None):
        self.username = email_address#username
        self.password = password
        self.driver = None
        #self.headless = True
        self.headless = False
        self.pageload_max = 10
        self.puid = None

        #mfa & proxy is ignored for now.


    def init_driver(self):
        if self.driver is None:
            self.driver = uc.Chrome(headless=self.headless)

    
    def get_access_token(self) -> str:
        #launch on demand
        self.init_driver()
        driver = self.driver

        # Navigate to the login page
        driver.get("https://chat.openai.com/auth/login")
        # Click the first button
        init_button = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div[4]/button[1]'))
        )
        init_button.click()



        first_button = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[1]/div[4]/button[1]'))
        )
        first_button.click()

        # Enter the username
        username_field = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
        )
        username_field.send_keys(self.username)

        # Click the second button
        second_button = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/main/section/div/div/div/div[1]/div/form/div[2]/button'))
        )
        second_button.click()

        # Enter the password
        password_field = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="password"]'))
        )
        password_field.send_keys(self.password)

        # Click the third button
        third_button = WebDriverWait(driver, self.pageload_max).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div/main/section/div/div/div/form/div[3]/button'))
        )
        third_button.click()
       

        def detect_puid(driver):
            cookie = driver.get_cookie('_puid')
            if cookie is not None:
                self.puid = cookie["value"]
            return cookie is not None


        try:
           
            ## acquire session.. still a hack
            ajax_code = """
                var xhr = new XMLHttpRequest();
                xhr.open('GET', 'https://chat.openai.com/api/auth/session', true);
                xhr.setRequestHeader('Content-type', 'application/json');

                xhr.onreadystatechange = function() {
                    if (xhr.readyState === XMLHttpRequest.DONE) {
                        if (xhr.status === 200) {
                            window.ajaxResponse = JSON.parse(xhr.responseText);
                        } else {
                            throw new Error('AJAX request failed');
                        }
                    }
                };

                xhr.send();
            """

            driver.execute_script(ajax_code)
            WebDriverWait(driver, self.pageload_max).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div[1]/div[1]/div/div/div/nav/div[3]/div/div/span[1]")),
            )
            
            ajax_response = WebDriverWait(driver, self.pageload_max).until(
                lambda d: d.execute_script("return window.ajaxResponse;")
            )  

            self.access_token = ajax_response.get('accessToken')
        
            WebDriverWait(driver, self.pageload_max*0.1).until(detect_puid)
        except:
            print("timeout, either the site loaded very fast or theres a problem.")

        self.quit()
        return self.access_token

    def quit(self):
        if self.driver and self.driver is not None:
            self.driver.quit()
            self.driver = None

    """
    //*[@id="radix-:rg:"]/div[2]/div[1]/div[2]/button
    //*[@id="radix-:rg:"]/div[2]/div[1]/div[2]/button[2]
    //*[@id="radix-:rg:"]/div[2]/div[1]/div[2]/button[2]
    """


    def get_puid(self) -> str:
        return self.puid
        
    def __del__(self):
        self.quit()

