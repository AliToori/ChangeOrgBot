#!/usr/bin/env python3
"""
    *******************************************************************************************
    ChangeOrgBot.
    Author: Ali Toori, Python Developer [Bot Builder]
    Website: https://botflocks.com
    LinkedIn: https://www.linkedin.com/in/alitoori/
    *******************************************************************************************
"""
import time
import os
import ntplib
import random
import pyfiglet
import pandas as pd
from random import randint
import logging.config
from pathlib import Path
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
import undetected_chromedriver as uc
from datetime import datetime, timedelta
from multiprocessing import freeze_support
from selenium.webdriver import ActionChains, DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support import expected_conditions as EC


logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'colored': {
            '()': 'colorlog.ColoredFormatter',  # colored output
            # --> %(log_color)s is very important, that's what colors the line
            'format': '[%(asctime)s] %(log_color)s[%(message)s]',
            'log_colors': {
                'DEBUG': 'green',
                'INFO': 'cyan',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
        'simple': {
                'format': '[%(asctime)s] [%(message)s]',
            },
    },
    "handlers": {
        "console": {
            "class": "colorlog.StreamHandler",
            "level": "INFO",
            "formatter": "colored",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "ChangeOrgBot_logs.log"
        },
    },
    "root": {"level": "INFO",
             "handlers": ["console", "file"]
             }
})

LOGGER = logging.getLogger()


class ChangeOrgBot:
    def __init__(self):
        self.comments_today = 0
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.directory_downloads = str(self.PROJECT_ROOT / 'CMCRes/Downloads/')
        self.file_proxies = self.PROJECT_ROOT / 'ChangeRes/proxies.txt'
        self.file_uagents = self.PROJECT_ROOT / 'ChangeRes/user_agents.txt'
        self.file_campaigns = str(self.PROJECT_ROOT / 'ChangeRes/Campaigns.csv')
        self.file_delay = str(self.PROJECT_ROOT / 'ChangeRes/Delay.txt')
        self.file_voters = str(self.PROJECT_ROOT / 'ChangeRes/Accounts.csv')
        self.CHNG_HOME_URL = "https://www.change.org/"
        self.mesh_proxy_api = 'https://proxymesh.com/api/proxies/'
        self.driver = None
        self.proxies = self.get_proxies()
        self.user_agents = self.get_user_agent()
        self.delay = self.get_delay()
        self.stopped = False

    @staticmethod
    def enable_cmd_colors():
        # Enables Windows New ANSI Support for Colored Printing on CMD
        from sys import platform
        if platform == "win32":
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

    # Print ASCII Art
    @staticmethod
    def banner():
        print('************************************************************************\n')
        pyfiglet.print_figlet('____________                   ChangeOrgBot ____________\n', colors='RED')
        print('Author: Ali Toori\n'
              'Website: https://botflocks.com/\n'
              '************************************************************************')

    # Trial version logic
    @staticmethod
    def trial(trial_date):
        ntp_client = ntplib.NTPClient()
        try:
            response = ntp_client.request('pool.ntp.org')
            local_time = time.localtime(response.ref_time)
            current_date = time.strftime('%Y-%m-%d %H:%M:%S', local_time)
            current_date = datetime.strptime(current_date, '%Y-%m-%d %H:%M:%S')
            return trial_date > current_date
        except:
            pass

    # Get proxies
    def get_proxies(self):
        with open(self.file_proxies) as f:
            content = f.readlines()
        proxies_list = [x.strip() for x in content]
        return proxies_list

    # Get user-agents
    def get_user_agent(self):
        with open(self.file_uagents) as f:
            content = f.readlines()
        user_agents_list = [x.strip() for x in content]
        return user_agents_list

    # Get delay interval
    def get_delay(self):
        with open(self.file_delay) as f:
            content = f.readlines()
        delay = [x.strip().split(':') for x in content][0]
        return delay

    def get_driver(self, proxy=None):
        # For absolute chromedriver path
        DRIVER_BIN = str(self.PROJECT_ROOT / "ChangeRes/bin/chromedriver.exe")
        service = Service(executable_path=DRIVER_BIN)
        # user_dir = str(self.PROJECT_ROOT / 'CMCRes/UserData')
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-notifications")
        options.add_argument("--dns-prefetch-disable")
        options.add_argument('--no-sandbox')
        options.add_argument('--incognito')
        options.add_argument('--disable-extensions')
        options.add_argument('--ignore-ssl-errors')
        options.add_argument('--ignore-certificate-errors')
        # options.add_argument(f"--user-data-dir={user_dir}")
        options.add_experimental_option('prefs', {
            'directory_upgrade': True,
            'credentials_enable_service': False,
            'profile.password_manager_enabled': False,
            'profile.default_content_settings.popups': False,
            # "profile.managed_default_content_settings.images": 2,
            f'download.default_directory': f'{self.directory_downloads}'})
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    # Finish and quit browser
    def finish(self, driver):
        try:
            # if not self.stopped:
            LOGGER.info(f'Closing the browser instance')
            driver.quit()
                # self.stopped = True
        except WebDriverException as exc:
            LOGGER.info(f'Problem occurred while closing the browser instance: {exc.args}')

    @staticmethod
    def wait_until_visible(driver, xpath=None, element_id=None, name=None, class_name=None, tag_name=None, css_selector=None, duration=10000, frequency=0.5):
        if xpath:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.XPATH, xpath)))
        elif element_id:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.ID, element_id)))
        elif name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.NAME, name)))
        elif class_name:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CLASS_NAME, class_name)))
        elif tag_name:
            WebDriverWait(driver, duration, frequency).until(EC.visibility_of_element_located((By.TAG_NAME, tag_name)))
        elif css_selector:
            WebDriverWait(driver, duration, frequency).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    # get data from followers of a user
    def cast_vote(self):
        if os.path.isfile(self.file_voters):
            voters_df = pd.read_csv(self.file_voters, index_col=None)
            # Get voters from Accounts.csv
            voter_list = [voter for voter in voters_df.iloc]
            campaigns_df = pd.read_csv(self.file_campaigns, index_col=None)
            delay_start = int(self.delay[0])
            delay_end = int(self.delay[1])
            # Get voters from Accounts.csv
            for campaign in campaigns_df.iloc:
                for voter in voter_list:
                    driver = self.get_driver()
                    driver.delete_all_cookies()
                    # if len(self.proxies) == 0:
                    #     driver = self.get_driver()
                    # else:
                    #     proxy = random.choice(self.proxies)
                    #     LOGGER.info(f"Using proxy: {proxy}")
                    #     driver = self.get_driver(proxy=proxy)
                    campaign_url = campaign['CampaignURL']
                    first_name = voter['FirstName']
                    last_name = voter['LastName']
                    email = voter['Email']
                    country = voter['Country']
                    city = voter['City']
                    zip_code = str(voter['ZipCode'])
                    LOGGER.info(f"Requesting campaign: {campaign_url}")
                    driver.get(campaign_url)
                    LOGGER.info(f"Waiting for the campaign")
                    self.wait_until_visible(driver=driver, css_selector="input[placeholder='First name']")
                    LOGGER.info(f"Submitting the campaign")
                    sleep(1)
                    LOGGER.info(f"FirstName: {first_name}")
                    driver.find_element(By.CSS_SELECTOR, "input[placeholder='First name']").send_keys(first_name)
                    sleep(1)
                    LOGGER.info(f"LastName: {last_name}")
                    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Last name']").send_keys(last_name)
                    sleep(1)
                    LOGGER.info(f"Email: {email}")
                    driver.find_element(By.CSS_SELECTOR, "input[placeholder='Email']").send_keys(email)
                    sleep(1)
                    try:
                        # Edits country, city and ZipCode
                        self.wait_until_visible(driver=driver, css_selector=".corgi__sc-17wpo9f-0.fcyNaC", duration=3)
                        # driver.find_element(By.CSS_SELECTOR, ".corgi__sc-17wpo9f-0.fcyNaC").click()
                        sleep(1)
                    except:
                        pass
                    try:
                        LOGGER.info(f"Country: {country}")
                        self.wait_until_visible(driver=driver, css_selector="select[name='countryCode']", duration=5)
                        country_select = Select(driver.find_element(By.CSS_SELECTOR, "select[name='countryCode']"))
                        # country_select.select_by_visible_text(country)
                        sleep(1)
                    except:
                        pass
                    try:
                        LOGGER.info(f"City: {city}")
                        self.wait_until_visible(driver=driver, css_selector="input[name='city']", duration=5)
                        city_box = driver.find_element(By.CSS_SELECTOR, "input[name='city']")
                        # city_box.clear()
                        # city_box.send_keys(city)
                        sleep(1)
                    except:
                        pass
                    try:
                        LOGGER.info(f"ZipCode: {zip_code}")
                        self.wait_until_visible(driver=driver, css_selector="input[name='postalCode']", duration=3)
                        zip_code_box = driver.find_element(By.CSS_SELECTOR, "input[name='postalCode']")
                        # zip_code_box.clear()
                        # zip_code_box.send_keys(zip_code)
                        sleep(1)
                    except:
                        pass
                    sleep(1000)
                    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                    try:
                        self.wait_until_visible(driver=driver, css_selector="[role='alert']", duration=3)
                        alert_text = driver.find_element(By.CSS_SELECTOR, "[role='alert']").text
                        if 'There was an error submitting your signature' in alert_text:
                            self.finish(driver=driver)
                            continue
                    except:
                        pass
                    LOGGER.info(f"Campaign is being submitted")
                    # i_frame_elem = driver.find_element('iframe:nth-child(8)')
                    # driver.switch_to.frame(i_frame_elem)
                    LOGGER.info(f"Waiting for captcha")
                    self.wait_until_visible(driver=driver, css_selector="#px-captcha")
                    sleep(1)
                    element = driver.find_element(By.CSS_SELECTOR, '#px-captcha')
                    action = ActionChains(driver)
                    captcha_submitted = False
                    LOGGER.info(f"Solving captcha")
                    while not captcha_submitted:
                        action.click_and_hold(element)
                        action.perform()
                        # sleep(15)
                        # action.release(element)
                        # self.wait_until_visible(driver=driver, css_selector="input[placeholder='First name']")
                        # Wait until Captcha disappears
                        try:
                            WebDriverWait(driver, 14, 0.5).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, '#px-captcha')))
                            captcha_submitted = True
                            LOGGER.info(f"Captcha has been solved")
                        except:
                            pass
                    LOGGER.info(f"Your vote has been successfully submitted")
                    # self.finish(driver)
                    delay = randint(delay_start, delay_end)
                    LOGGER.info(f"Waiting for {str(delay)} seconds before next vote")
                    sleep(delay)
                    sleep(5000)

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        trial_date = datetime.strptime('2021-11-16 23:59:59', '%Y-%m-%d %H:%M:%S')
        # Print ASCII Art
        self.banner()
        # Trial version logic
        # if self.trial(trial_date):
        if True:
            LOGGER.info(f'Launching ChangeOrgBot ...')
            # LOGGER.warning("Your trial will end on: ",
            #       str(trial_date) + ". To get full version, please contact fiverr.com/AliToori !")
            self.cast_vote()
            LOGGER.info(f'Process completed successfully!')
        # else:
        #     pass
            # LOGGER.warning("Your trial has been expired"")
            # LOGGER.warning("Please visit http://botflocks.com !")


if __name__ == '__main__':
    changeorg_bot = ChangeOrgBot()
    changeorg_bot.main()
