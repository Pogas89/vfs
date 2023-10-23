import logging

import requests
from time import sleep

from jproperties import Properties
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from retryUtils import run_with_retry

long_timeout = 5
short_timeout = 2

is_registration_properties_set = False


def set_global_properties_for_registration(path):
    global id_number, verification_number, name, surname, sex, passport, exp_date, phone_code, phone, email

    configs = Properties()
    try:
        with open(path, 'rb') as config_file:
            configs.load(config_file)

        id_number = configs.get("id_number").data
        verification_number = configs.get("verification_number").data
        name = configs.get("name").data
        surname = configs.get("surname").data
        sex = configs.get("sex").data
        passport = configs.get("passport").data
        exp_date = configs.get("exp_date").data
        phone_code = configs.get("phone_code").data
        phone = configs.get("phone").data
        email = configs.get("email").data
    except Exception:
        raise Exception("Could not load properties for registration")


def registration_func(drv):
    global is_registration_properties_set
    if not is_registration_properties_set:
        set_global_properties_for_registration('app.properties')
        is_registration_properties_set = True
    run_with_retry(id_number_registration, drv)
    run_with_retry(verification_number_registration, drv)
    run_with_retry(name_registration, drv)
    run_with_retry(surname_registration, drv)
    run_with_retry(sex_registration, drv)
    run_with_retry(passport_registration, drv)
    run_with_retry(exp_date_registration, drv)
    run_with_retry(phone_code_registration, drv)
    run_with_retry(phone_registration, drv)
    run_with_retry(email_registration, drv)


def id_number_registration(drv):
    id_number_input = drv.find_element(By.XPATH, "//*[@id='mat-input-2']")
    id_number_input.send_keys(id_number)
    logging.info("id_number added")
    sleep(short_timeout)


def verification_number_registration(drv):
    verification_number_input = drv.find_element(By.XPATH, "//*[@id='mat-input-3']")
    verification_number_input.send_keys(verification_number)
    logging.info("verification_number added")
    sleep(short_timeout)


def name_registration(drv):
    name_registration_input = drv.find_element(By.XPATH, "//*[@id='mat-input-4']")
    name_registration_input.send_keys(name)
    logging.info("name added")
    sleep(short_timeout)


def surname_registration(drv):
    surname_registration_input = drv.find_element(By.XPATH, "//*[@id='mat-input-5']")
    surname_registration_input.send_keys(surname)
    logging.info("surname added")
    sleep(short_timeout)


def sex_registration(drv):
    sex_el = drv.find_element(By.XPATH, "//*[@id='mat-select-value-9']")
    drv.execute_script("arguments[0].click();", sex_el)
    sleep(short_timeout)
    try:
        _sex = drv.find_element(
            "xpath",
            "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                sex
            ),
        )
    except NoSuchElementException:
        raise Exception("Visa type not found: {}".format(sex))
    sleep(short_timeout)
    drv.execute_script("arguments[0].click();", _sex)
    logging.info("Visa type added")
    sleep(long_timeout)


def passport_registration(drv):
    passport_input = drv.find_element(By.XPATH, "//*[@id='mat-input-6']")
    passport_input.send_keys(passport)
    logging.info("passport added")
    sleep(short_timeout)


def exp_date_registration(drv):
    exp_date_input = drv.find_element(By.XPATH, "//*[@id='passportExpirtyDate']")
    exp_date_input.send_keys(exp_date)
    logging.info("exp_date added")
    sleep(short_timeout)


def phone_code_registration(drv):
    phone_code_input = drv.find_element(By.XPATH, "//*[@id='mat-input-7']")
    phone_code_input.send_keys(phone_code)
    logging.info("phone_code added")
    sleep(short_timeout)


def phone_registration(drv):
    phone_input = drv.find_element(By.XPATH, "//*[@id='mat-input-8']")
    phone_input.send_keys(phone)
    logging.info("phone added")
    sleep(short_timeout)


def email_registration(drv):
    email_input = drv.find_element(By.XPATH, "//*[@id='mat-input-9']")
    email_input.send_keys(email)
    logging.info("email added")
    sleep(short_timeout)