import logging

from selenium.common.exceptions import NoSuchElementException
from time import sleep


def run_with_retry_two_param(method, param1, param2):
    attempts = 0
    done = False
    while attempts < 3:
        try:
            method(param1, param2)
            done = True
            break
        except NoSuchElementException:
            sleep(5)
            attempts += 1
            logging.warning("Retry with attempt: {}".format(attempts))
    if not done:
        method(param1, param2)


def run_with_retry(method, param):
    attempts = 0
    done = False
    while attempts < 3:
        try:
            method(param)
            done = True
            break
        except NoSuchElementException:
            sleep(5)
            attempts += 1
            logging.warning("Retry with attempt: {}".format(attempts))
    if not done:
        method(param)
