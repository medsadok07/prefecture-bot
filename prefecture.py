import codecs

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from time import sleep
from win10toast import ToastNotifier
import datetime
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import os.path
import os
import vlc

import random

LOGS_ = 'C:\\Users\\Training\\PrefectureLogs\\'
# A dictionary to store all the prefecture desks.
# Modify their name depending on your prefecture desks' names.
# You should inspect the page with chrome and grab the id of each desk (they are radio buttons in the planning element).
# The key are the id of the radio button and the value is as you like
PrefectDesks = {'planning13782': 'planning1', 'planning20779': 'planning2', 'planning21505': 'planning3'}
# Option to run chrome in background while you use webdriver library.
# You should install chromedriver.
# You can follow this tutorial to make it works https://www.youtube.com/watch?v=dz59GsdvUF8
# Chromedriver path "C:\webdrivers\chromedriver.exe"

options = webdriver.ChromeOptions()

software_names = [SoftwareName.CHROME.value]
operating_systems = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value]
user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)

# Put the URL of your prefecture. This one works only with Val d'Oise Prefecture (Cergy)
url = "https://www.val-doise.gouv.fr/booking/create/11343/1"

# Sentence displayed by the URL if there is no available appointment spots
NoAppointmentAvailable_Sentences = ["existe plus de plage horaire libre pour votre demande",
                                    "de rendez-vous disponibles pour le moment",
                                    "The server returned an invalid or incomplete response"]
Error_403 = ["403", "Request forbidden by administrative rules", "Service surchargé", "Aucun accès à Internet"]

toaster = ToastNotifier()

Rdv_filename = '%srdvs_status.txt' % LOGS_
Error_filename = '%slog_errors.txt' % LOGS_
# options.add_argument('--headless') # Uncomment this line if you want it to open browser in background
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')
options.add_argument('--no-sandbox')


# options.add_argument('--disable-gpu')

def check_available_spot(now):
    print("Checking for appointment    " + now)

    # DeskId is chosen randomly
    desk_key = random.choice(list(PrefectDesks.keys()))
    print("random desk key    " + desk_key)

    desk_value = PrefectDesks[desk_key]
    print("corresponds to desk value    " + desk_value)

    user_agent = user_agent_rotator.get_random_user_agent()
    options.add_experimental_option("detach", True)
    options.add_argument(f'user-agent={user_agent}')

    # Open Chrome browser and get all the html elements of the webpage
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    #TODO check if there is a 403 error
    #TODO then open with different browser
    #TODO accept cookies


    # Set on the deskValue
    wait = WebDriverWait(driver, 5)

    # if any(x in driver.page_source for x in Error_403):
    #     driver.quit()
    #     driver = webdriver.Edge(options=options)
    #     driver.get(url)

    wait.until(ec.element_to_be_clickable((By.ID, desk_key)))
    driver.find_element(By.ID, desk_key).click()

    # Wait until the next_button is clickable and scroll down to click on it
    next_button = wait.until(ec.element_to_be_clickable((By.NAME, 'nextButton')))
    driver.execute_script("return arguments[0].scrollIntoView(true);", next_button)
    sleep(1)
    next_button = driver.find_element(By.NAME, 'nextButton')
    next_button.click()

    # If you want to take screenshot for each attempt
    take_screenshot(driver, now)
    save_source(driver, now)

    if any(x in driver.page_source for x in NoAppointmentAvailable_Sentences):
        places_are_already_taken = True
        driver.quit()
    else:
        places_are_already_taken = False
        #todo appuyer sur le bouton etape suivante à tester avec un front local
        # next_button = wait.until(ec.element_to_be_clickable((By.NAME, 'nextButton')))
        # driver.execute_script("return arguments[0].scrollIntoView(true);", next_button)
        # sleep(1)
        # next_button = driver.find_element(By.NAME, 'nextButton')
        # next_button.click()

        play_alarm_sound()
        display(desk_value, now)

    return places_are_already_taken, desk_value, desk_key


def take_screenshot(driver, now):
    save_captures_path = "%scaptures\\" % LOGS_
    file_name = 'capture {}.png'.format(now)
    complete_capture_name = os.path.join(save_captures_path, file_name)
    driver.get_screenshot_as_file(complete_capture_name)


def display(desk_value, now):
    toaster.show_toast(title='New spot is available ' + now, msg=str(desk_value), duration=20, threaded=True)


def write_results(places_are_already_taken, desk_value, now):
    with open(Rdv_filename, 'a') as f:
        if places_are_already_taken:
            f.write('{} No place is available! Desk Tested {}\n'.format(now, desk_value))
        else:
            f.write('{} At least one place is available! Desk {}\n'.format(now, desk_value))


def play_alarm_sound():
    p = vlc.MediaPlayer("alarm.wav")
    p.play()


def save_source(driver, now):
    file_name = 'source {}.html'.format(now)
    save_sources_path = LOGS_ + "sources\\"
    complete_source_name = os.path.join(save_sources_path, file_name)
    f = codecs.open(complete_source_name, "w", "utf−8")
    h = driver.page_source
    f.write(h)


def log_error(e, now):
    with open(Error_filename, 'a') as f:
        f.write('{} Error {}\n'.format(now, e))


def user_notificator(now):
    try:
        toaster.show_toast("error " + str(now))
    except Exception as e:
        log_error("Error toaster :" + str(e) + now)


def main():
    print("""
    ____            ____          __                     ____        __ 
   / __ \________  / __/__  _____/ /___  __________     / __ )____  / /_
  / /_/ / ___/ _ \/ /_/ _ \/ ___/ __/ / / / ___/ _ \   / __  / __ \/ __/
 / ____/ /  /  __/ __/  __/ /__/ /_/ /_/ / /  /  __/  / /_/ / /_/ / /_  
/_/   /_/   \___/_/  \___/\___/\__/\__,_/_/   \___/  /_____/\____/\__/  

    """)
    print('Starting to monitor the reservation system.')
    print('Press CTRL+C to abort...\n')
    attempts = 0
    while True:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H%M%S")
            places_are_already_taken, desk_value, desk_key = check_available_spot(now)
        except Exception as e:
            user_notificator(now)
            log_error(repr(e), str(now))
            print('Last check failed           ' + now)
        else:
            write_results(places_are_already_taken, desk_value, now)
            print('Last Desk checked ' + desk_value + ' ' + now)
        finally:
            attempts += 1;
            print('Attempt number : ' + attempts.__str__())
            sleep(40)


if __name__ == '__main__':
    main()
