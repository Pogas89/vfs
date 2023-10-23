# import libraries
import os

import requests
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from jproperties import Properties

from retryUtils import run_with_retry
from selection import selection_func

# telegram credentials (replace 0 by your token & chatid)
telegram_enabled = True

COUNT = 1
LONG_TIMEOUT = 5
SHORT_TIMEOUT = 2
LOAD_PAGE_TIMEOUT = 10


def set_global_properties(path):
    global vfs_url, telegram_token, telegram_chatid, username, password, visa_centres

    configs = Properties()
    try:
        with open(path, 'rb') as config_file:
            configs.load(config_file)

        vfs_url = configs.get("vfs_url").data
        telegram_token = configs.get("telegram_token").data
        telegram_chatid = configs.get("telegram_chatid").data
        username = configs.get("username").data
        password = configs.get("password").data
        visa_centres = configs.get("visa_centres").data.split(",")
    except Exception:
        raise Exception("Could not load properties")


# func for looping through visa center
def choose_visa_center():
    global COUNT
    COUNT = COUNT + 1
    n = COUNT % len(visa_centres)
    return visa_centres[n]


def send_message_to_telegram(m):
    global url, post_data
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    post_data = {"chat_id": telegram_chatid, "parse_mode": "Markdown",
                 "text": m}
    requests.post(url, data=post_data)


def proceed_to_registration(drv):
    proceed_but = drv.find_element("xpath",
                                   "/html/body/app-root/div/div/app-eligibility-criteria/section/form/mat-card[2]/button")
    proceed_but.click()
    logging.info("Proceed to registration")
    sleep(LONG_TIMEOUT)


def choose_new_visit(drv):
    app_but = drv.find_element("xpath", "/html/body/app-root/div/div/app-dashboard/section[1]/div/div[2]/div/button")
    app_but.click()
    logging.info("Chose new visit")


def find_availability_msg(drv):
    try:
        return drv.find_element("xpath", "//*[text()[contains(.,'нет доступных слотов')]]")
    except NoSuchElementException:
        logging.info("There may be some good news...")
    return drv.find_element("xpath", "//*[text()[contains(.,'Самый ранний доступный слот')]]")


# -------------------------------------start of the bot----------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
logging.info("Bot started...")
# Reading the properties
set_global_properties('app.properties')

# check if telegram credentials are provided
if not (telegram_token or telegram_chatid):
    telegram_enabled = False
    logging.info("- Alert! No Telegram credentials were provided. Messages will only be printed in the log.")
if telegram_enabled:
    message = "Bot started..."
    send_message_to_telegram(message)
# access website
driver = webdriver.Chrome()
driver.maximize_window()

driver.get(vfs_url)

logging.info("Website successfully opened!")
sleep(LOAD_PAGE_TIMEOUT)
loginForm = driver.find_element(By.ID, "mat-input-0")
loginForm.send_keys(username)
passForm = driver.find_element(By.ID, "mat-input-1")
passForm.send_keys(password)
logging.info("Login data added!")
logging.info("Time to pass the CAPTCHA!!!!")

# waiting to pass CAPTCHA and login
current_url = driver.current_url
while driver.current_url == current_url:
    sleep(SHORT_TIMEOUT)
sleep(LOAD_PAGE_TIMEOUT)

try:
    run_with_retry(choose_new_visit, driver)
    sleep(LONG_TIMEOUT)
    # first round of inputs
    # example Poland Visa Application Center-Grodno,Poland Visa Application Center-Lida
    vc = choose_visa_center()
    selection_func(driver, vc)
except NoSuchElementException as e:
    logging.error("Timeout - need to be restarted: {}".format(e.msg))

    # send telegram message
    if telegram_enabled:
        send_message_to_telegram("Error - need to be restarted: {}".format(e.msg))
    sleep(LOAD_PAGE_TIMEOUT)
    raise Exception("Error - need to be restarted")

logging.info("Going to the loop after 1 attempt")
while True:
    sleep(SHORT_TIMEOUT)
    # spot error message
    try:
        error_msg = find_availability_msg(driver)
        if "нет доступных слотов" in error_msg.text:
            logging.info("No good news yet...")
            nvc = choose_visa_center()
            sleep(SHORT_TIMEOUT)
            selection_func(driver, nvc)
            continue

        else:
            if "Самый ранний доступный слот" in error_msg.text:
                logging.warning("There may be some good news: {}".format(error_msg.text))

                # send telegram message
                if telegram_enabled:
                    message = "There may be some good news about the visa for {} and {}".format(vc, error_msg.text)
                    send_message_to_telegram(message)
                continue
    except NoSuchElementException as e:
        logging.error("Timeout - need to be restarted: {}".format(e.msg))

        # send telegram message
        if telegram_enabled:
            send_message_to_telegram("Error - need to be restarted: {}".format(e.msg))
        sleep(LOAD_PAGE_TIMEOUT)
        raise Exception("Error - need to be restarted")

if telegram_enabled:
    message = "Going to registration form"
    send_message_to_telegram(message)

sleep(LOAD_PAGE_TIMEOUT)
run_with_retry(proceed_to_registration, driver)
