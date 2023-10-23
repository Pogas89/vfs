import logging

import requests
from time import sleep

from jproperties import Properties
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from retryUtils import run_with_retry, run_with_retry_two_param

long_timeout = 5
short_timeout = 2

is_selection_properties_set = False


# function for selection
def selection_func(drv, visa_centre):
    global is_selection_properties_set
    if not is_selection_properties_set:
        set_global_properties_for_selection('app.properties')
        is_selection_properties_set = True

    run_with_retry_two_param(visa_center_selection, drv, visa_centre)
    # choosing visa type
    run_with_retry(visa_type_selection, drv)
    # choosing visa visa_additional_type
    run_with_retry(visa_sub_type_selection, drv)
    # adding birthdate
    run_with_retry(birthday_selection, drv)
    # choosing visa country
    run_with_retry(visa_country_selection, drv)


def visa_center_selection(drv, visa_centre):
    # choosing visa centre
    _visa_centre_el = drv.find_element(By.ID, "mat-select-value-1")  # fill in field #1 (Выберите свой визовый центр)
    drv.execute_script("arguments[0].click();", _visa_centre_el)
    sleep(short_timeout)
    try:
        _visa_centre = drv.find_element(
            "xpath",
            "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                visa_centre
            ),
        )
    except NoSuchElementException:
        raise NoSuchElementException("Visa centre not found: {}".format(visa_centre))
    sleep(short_timeout)
    drv.execute_script("arguments[0].click();", _visa_centre)
    logging.info("Visa center added")
    sleep(long_timeout)


def visa_country_selection(drv):
    _country_name_el = drv.find_element(By.XPATH, "//*[@id='mat-select-value-7']")
    drv.execute_script("arguments[0].click();", _country_name_el)
    sleep(short_timeout)
    try:
        _country_name = drv.find_element(
            "xpath",
            "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                country_name
            ),
        )
    except NoSuchElementException:
        raise Exception("Country not found: {}".format(country_name))
    sleep(short_timeout)
    drv.execute_script("arguments[0].click();", _country_name)
    logging.info("Country added")
    sleep(long_timeout)


def birthday_selection(drv):
    birth_input = drv.find_element(By.XPATH,
                                   "/html/body/app-root/div/div/app-eligibility-criteria/section/form/mat-card[1]/form/div[4]/div[2]/input")
    birth_input.send_keys(date_of_birth)
    logging.info("Birth date added")
    sleep(long_timeout)


def visa_sub_type_selection(drv):
    _visa_add_type_el = drv.find_element(By.ID, "mat-select-4")
    drv.execute_script("arguments[0].click();", _visa_add_type_el)
    sleep(short_timeout)
    try:
        _visa_add_type = drv.find_element(
            "xpath",
            "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                visa_additional_type1
            ),
        )
    except NoSuchElementException:
        try:
            _visa_add_type = drv.find_element(
                "xpath",
                "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                    visa_additional_type2
                ),
            )
        except NoSuchElementException:
            raise Exception("Visa additional type not found: {}".format(visa_additional_type1))
    sleep(short_timeout)
    drv.execute_script("arguments[0].click();", _visa_add_type)
    logging.info("Visa additional type added")
    sleep(long_timeout)


def visa_type_selection(drv):
    _visa_type_el = drv.find_element(By.ID, "mat-select-2")  # fill in field #2 (Выберите категорию записи)
    drv.execute_script("arguments[0].click();", _visa_type_el)
    sleep(short_timeout)
    try:
        _visa_type = drv.find_element(
            "xpath",
            "//mat-option[starts-with(@id,'mat-option-')]/span[contains(text(), '{}')]".format(
                visa_type
            ),
        )
    except NoSuchElementException:
        raise Exception("Visa type not found: {}".format(visa_type))
    sleep(short_timeout)
    drv.execute_script("arguments[0].click();", _visa_type)
    logging.info("Visa type added")
    sleep(long_timeout)


def set_global_properties_for_selection(path):
    global visa_type, visa_additional_type1, visa_additional_type2, date_of_birth, country_name, visa_centres

    configs = Properties()
    try:
        with open(path, 'rb') as config_file:
            configs.load(config_file)

        visa_type = configs.get("visa_type").data
        visa_additional_type1 = configs.get("visa_additional_type1").data
        visa_additional_type2 = configs.get("visa_additional_type2").data
        date_of_birth = configs.get("date_of_birth").data
        country_name = configs.get("country_name").data
        visa_centres = configs.get("visa_centres").data.split(",")
    except Exception:
        raise Exception("Could not load properties for selection")
