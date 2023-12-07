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
import webbrowser
import pyautogui
from selenium import webdriver
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
            "filename": "ChangeOrgBot-v0.1_logs.log"
        },
    },
    "root": {"level": "INFO",
             "handlers": ["console", "file"]
             }
})

LOGGER = logging.getLogger()

pyautogui.FAILSAFE = False


class ChangeOrgBot:
    def __init__(self):
        self.comments_today = 0
        self.PROJECT_ROOT = Path(os.path.abspath(os.path.dirname(__file__)))
        self.file_proxies = self.PROJECT_ROOT / 'ChangeRes/proxies.txt'
        self.file_uagents = self.PROJECT_ROOT / 'ChangeRes/user_agents.txt'
        self.file_campaigns = str(self.PROJECT_ROOT / 'ChangeRes/Campaigns.csv')
        self.extension_img = str(self.PROJECT_ROOT / 'ChangeRes/nordvpn.svg')
        self.file_delay = str(self.PROJECT_ROOT / 'ChangeRes/Delay.txt')
        self.file_voters = str(self.PROJECT_ROOT / 'ChangeRes/Voters.csv')
        self.file_vpn_ips = str(self.PROJECT_ROOT / 'ChangeRes/VPN_IPs.csv')
        self.file_vpn_cords = str(self.PROJECT_ROOT / 'ChangeRes/Cords.csv')
        self.file_options = str(self.PROJECT_ROOT / 'ChangeRes/Options.csv')
        self.CHNG_HOME_URL = "https://www.change.org/"
        self.mesh_proxy_api = 'https://proxymesh.com/api/proxies/'
        self.driver = None
        self.proxies = self.get_proxies()
        self.user_agents = self.get_user_agent()
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
        print('Author: Ali Toori, Bot Developer\n'
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
        u_agents_list = [x.strip() for x in content]
        return u_agents_list

    # Clear browser cache
    @staticmethod
    def block_cookies():
        LOGGER.info(f"Blocking third-party cookies")
        # Go to block cookies switch
        pyautogui.press(['tab', 'tab'])
        sleep(1)
        pyautogui.press('enter')
        sleep(1)
        LOGGER.info(f"Third-party cookies have been blocked")

    @staticmethod
    def clear_cache():
        LOGGER.info(f"Clearing cache")
        # Go to clear cache tab in chrome
        # pyautogui.hotkey('ctrl', 'shift', 'delete')
        pyautogui.hotkey('ctrl', 'n')
        sleep(1)
        pyautogui.typewrite('chrome://settings/content/siteDetails?site=https%3A%2F%2Fwww.change.org')
        pyautogui.press('enter')
        sleep(2)
        # Press tab to focus on Clear button
        pyautogui.press('tab')
        sleep(1)
        pyautogui.press('enter')
        sleep(1)
        pyautogui.press(['tab', 'tab'])
        sleep(1)
        # Press enter to trigger the "Skip" button
        pyautogui.press('enter')
        sleep(1)
        # Close the current tab in chrome
        # pyautogui.hotkey('ctrl', 'w')
        LOGGER.info(f"Cache has been cleared")

    def solve_captcha(self, wait_for_captcha):
        LOGGER.info(f"Solving captcha")
        center_x, center_y = self.get_screen_center()
        pyautogui.moveTo(x=center_x, y=center_y)
        sleep(3)
        # Move the mouse to the first name bot and fill the inputs
        pyautogui.click(x=center_x, y=center_y, button='left')
        sleep(1)
        # Press tab to focus on Clear button
        pyautogui.keyDown('enter')
        sleep(wait_for_captcha)
        pyautogui.keyUp('enter')
        LOGGER.info(f"Captcha has been solved")

    # Returns center of the screen
    @staticmethod
    def get_screen_center():
        height = pyautogui.size().width
        width = pyautogui.size().height
        center_x, center_y = int(height/2), int(width/2)
        return center_x, center_y

    # get data from followers of a user
    def cast_vote(self):
        if os.path.isfile(self.file_voters):
            voters_df = pd.read_csv(self.file_voters, index_col=None)
            # Get voters from Accounts.csv
            voter_list = [voter for voter in voters_df.iloc]
            campaigns_df = pd.read_csv(self.file_campaigns, index_col=None)
            # vpn_ips_df = pd.read_csv(self.file_vpn_ips, index_col=None)
            # vpn_ips = [ip["CountryIP"] for ip in vpn_ips_df.iloc]
            options_df = pd.read_csv(self.file_options, index_col=None)
            options = [option for option in options_df.iloc]
            vpn_popup = str(options[0]["VPNPop"])
            ip_switch = str(options[0]["IPSwitch"])
            wait_for_campaign = int(options[0]["WaitForCampaign"])
            delay = str(options[0]["Delay"])
            captcha = str(options[0]["Captcha"])
            first_name_box = int(options[0]["FirstNameBox"])
            wait_for_captcha = int(options[0]["WaitForCaptcha"])
            wait_between_actions = options[0]["WaitBetweenActions"]
            vpn_cords = str(options[0]["VpnCords"])
            close_cords = str(options[0]["CloseCords"])
            vpn_x = int(vpn_cords.split(':')[0])
            vpn_y = int(vpn_cords.split(':')[1])
            close_x = int(close_cords.split(':')[0])
            close_y = int(close_cords.split(':')[1])
            delay_start = int(delay.split(':')[0])
            delay_end = int(delay.split(':')[1])
            # Get voters from Accounts.csv
            webbrowser.open_new('https://www.google.com')
            for campaign in campaigns_df.iloc:
                for voter in voter_list:
                    campaign_url = campaign['CampaignURL']
                    # vpn_ip = random.choice(vpn_ips)
                    first_name = str(voter['FirstName'])
                    last_name = str(voter['LastName'])
                    email = str(voter['Email'])
                    country = str(voter['Country'])
                    city = str(voter['City'])
                    zip_code = str(voter['ZipCode'])
                    LOGGER.info(f"Requesting campaign: {campaign_url}")
                    # Open URL in new window, raising the window if possible.
                    sleep(wait_between_actions)
                    webbrowser.open_new(campaign_url)
                    sleep(wait_between_actions)
                    # Skip VPN pop-up
                    if vpn_popup.lower() == 'yes':
                        pyautogui.press(['tab', 'tab', 'tab'])
                        sleep(wait_between_actions)
                        pyautogui.press('enter')
                        sleep(wait_between_actions)
                    if ip_switch.lower() == 'yes':
                        LOGGER.info(f"Changing IP to: {country}")
                        pyautogui.moveTo(vpn_x, vpn_y)
                        # Click on NordVPN extension
                        pyautogui.click(vpn_x, vpn_y)
                        # Wait for NordVPN to load
                        sleep(3)
                        # Click on change country
                        # pyautogui.moveTo(vpn_country_x, vpn_country_y)
                        # # sleep(3)
                        # pyautogui.click(vpn_country_x, vpn_country_y)
                        # sleep(3)
                        pyautogui.press('enter')
                        sleep(wait_between_actions)
                        pyautogui.press(['tab', 'tab', 'tab'])
                        sleep(wait_between_actions)
                        pyautogui.press('enter')
                        sleep(wait_between_actions)
                        # Enter the country name
                        pyautogui.typewrite(country)
                        sleep(wait_between_actions)
                        # press enter to go to the campaign
                        pyautogui.press('enter')
                        pyautogui.press('esc')
                    # LOGGER.info(f"Closing the tab")
                    # Close the newly-opened tab by pressing CTRL + w
                    # pyautogui.hotkey('ctrl', 'w')
                    # sleep(10)
                    # LOGGER.info(f"Opening a new incognito window")
                    # Open new incognito tab by pressing CTRL + shift + n
                    # pyautogui.hotkey('ctrl', 'n')
                    # sleep(1)
                    # Block third-party cookies in incognito mode
                    # self.block_cookies()
                    # Enter the URL
                    # pyautogui.typewrite(campaign_url)
                    # sleep(3)
                    # press enter to go to the campaign
                    # pyautogui.press('enter')
                    LOGGER.info(f"Waiting for the campaign")
                    sleep(wait_for_campaign)
                    # Move the mouse to the first name bot and fill the inputs
                    # pyautogui.moveTo(x=input_x, y=input_y)
                    # # sleep(3)
                    # pyautogui.click(x=input_x, y=input_y, button='left')
                    # Hit tab n-times to focus on FirstNam input box
                    for i in range(1, first_name_box):
                        pyautogui.press('tab')
                    sleep(wait_between_actions)
                    LOGGER.info(f"FirstName: {first_name}")
                    pyautogui.typewrite(first_name)
                    sleep(wait_between_actions)
                    pyautogui.press('tab')
                    LOGGER.info(f"LastName: {last_name}")
                    pyautogui.typewrite(last_name)
                    sleep(wait_between_actions)
                    pyautogui.press('tab')
                    LOGGER.info(f"Email: {email}")
                    pyautogui.typewrite(email)
                    sleep(wait_between_actions)
                    # pyautogui.press(['tab', 'tab'])
                    # LOGGER.info(f"City: {city}")
                    # pyautogui.typewrite(city)
                    # sleep(1)
                    # pyautogui.press('tab')
                    # LOGGER.info(f"ZipCode: {zip_code}")
                    # pyautogui.typewrite(zip_code)
                    # sleep(1)
                    LOGGER.info(f"The vote is being submitted")
                    # press enter to submit the vote
                    pyautogui.press('enter')
                    # Wait for captcha to load
                    sleep(wait_between_actions)
                    # solve on captcha
                    if captcha.lower() == 'yes':
                        self.solve_captcha(wait_for_captcha=wait_for_captcha)
                    # press space to scroll to the "share" button
                    pyautogui.press('space')
                    # Press tab twice to focus on the "share"
                    pyautogui.press(['tab', 'tab'])
                    # Press enter to trigger the "share" button
                    pyautogui.press('enter')
                    # Wait for the next page
                    sleep(1)
                    # press space to scroll to the "skip" button
                    pyautogui.press('space')
                    # Press tab 4 times to focus on the "skip"
                    pyautogui.press(['tab', 'tab', 'tab', 'tab'])
                    # Press enter to trigger the "Skip" button
                    pyautogui.press('enter')
                    # Wait for the next page
                    sleep(1)
                    # press space to scroll to the "skip" button
                    pyautogui.press('space')
                    sleep(wait_between_actions)
                    # CLear the cache before closing the tab
                    self.clear_cache()
                    sleep(wait_between_actions)
                    # Press CTRL + w to close the opened incognito window
                    # pyautogui.hotkey('ctrl', 'w')
                    # Close the window
                    # width = pyautogui.size().width
                    pyautogui.click(x=close_x - 3, y=close_y, button='left')
                    sleep(wait_between_actions)
                    # Close the vote tab
                    pyautogui.hotkey('ctrl', 'w')
                    LOGGER.info(f"Your vote has been successfully submitted")
                    delay = randint(delay_start, delay_end)
                    LOGGER.info(f"Waiting for {str(delay)} seconds before next vote")
                    sleep(delay)

    def main(self):
        freeze_support()
        self.enable_cmd_colors()
        trial_date = datetime.strptime('2022-01-05 23:59:59', '%Y-%m-%d %H:%M:%S')
        # Print ASCII Art
        self.banner()
        # Trial version logic
        if self.trial(trial_date):
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
