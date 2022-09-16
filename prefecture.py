import codecs

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep
from win10toast import ToastNotifier
import datetime
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
import os.path
import os
import vlc

import random

# A dictionnary to store all the prefecture desks.
# Modify their name depending on your prefecture desks' names.
# You should inspect the page with chrome and grab the id of each desk (they are radio buttons in the planning element).
# The key are the id of the radio button and the value is as you like
PrefectDesks = {'planning13782': 'planning1', 'planning20779': 'planning2', 'planning21505': 'planning3'}
# Sadok values : planning13782 planning20779 planning21505


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
# Sadok values : https://www.val-doise.gouv.fr/booking/create/11343
# Sentence displayed by the URL if there is no available appointement spots
NoAppointmentAvailable_Sentences = ["existe plus de plage horaire libre pour votre demande",
                                    "de rendez-vous disponibles pour le moment",
                                    "The server returned an invalid or incomplete response"]

toaster = ToastNotifier()

Rdv_filename = 'C:\\Users\\Training\\PrefectureLogs\\rdvs_status.txt'
# Sadok values : C:\Users\medsa\PrefectureLogs\\rdvs_status.txt
Error_filename = 'C:\\Users\\Training\\PrefectureLogs\\log_errors.txt'
# Sadok values : C:\\Users\\medsa\\PrefectureLogs\\log_errors.txt
options.add_argument('--headless')
options.add_argument("--window-size=1280,800")
options.add_argument('--no-sandbox')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')


def check_available_spot(now):
    print("Checking for appointment    " + now)
    # DeskId is chosen randomly
    desk_key = random.choice(list(PrefectDesks.keys()))

    user_agent = user_agent_rotator.get_random_user_agent()

    options.add_argument(f'user-agent={user_agent}')

    # Open Chrome browser and get all the html elements of the webpage
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Set on the deskValue
    wait = WebDriverWait(driver, 5)
    wait.until(ec.element_to_be_clickable((By.ID, desk_key)))
    driver.find_element(By.ID, desk_key).click()

    # Wait until the next_button is clickable and scroll down to click on it
    next_button = wait.until(ec.element_to_be_clickable((By.NAME, 'nextButton')))
    driver.execute_script("return arguments[0].scrollIntoView(true);", next_button)
    sleep(1)
    next_button = driver.find_element(By.NAME, 'nextButton')
    next_button.click()

    # If you want to take screenshot for each attempt
    save_captures_path = "C:\\Users\\Training\\PrefectureLogs\\captures\\"
    file_name = 'capture {}.png'.format(now)
    complete_capture_name = os.path.join(save_captures_path, file_name)
    driver.get_screenshot_as_file(complete_capture_name)

    if any(x in driver.page_source for x in NoAppointmentAvailable_Sentences):
        places_are_already_taken = True
    else:
        places_are_already_taken = False
        save_source(driver, now)
        p = vlc.MediaPlayer("file:///C:/Users/Training/Desktop/prefecture/alarm2.wav")
        p.play()

    return places_are_already_taken, PrefectDesks[desk_key], desk_key


def save_source(driver, now):
    file_name = 'source {}.html'.format(now)
    save_sources_path = "C:\\Users\\Training\\PrefectureLogs\\sources\\"
    complete_source_name = os.path.join(save_sources_path, file_name)
    f = codecs.open(complete_source_name, "w", "utf−8")
    h = driver.page_source
    f.write(h)


def display(desk_value, now):
    toaster.show_toast(title='New spot is available ' + now, msg=str(desk_value), duration=20, threaded=True)


def open_appointment_page(desk_key):
    chrome_options = Options()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.get(url)
    # Set on the deskValue
    WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.ID, desk_key)))
    driver.find_element(By.ID, desk_key).click()
    # Wait until the next_button is clickable and scroll down to click on it
    next_button = WebDriverWait(driver, 5).until(ec.element_to_be_clickable((By.NAME, 'nextButton')))
    driver.execute_script("return arguments[0].scrollIntoView(true);", next_button)
    sleep(1)
    next_button = driver.find_element(By.NAME, 'nextButton')
    next_button.click()
    # try:
    #   sleep(2)
    #   driver.find_element(By.XPATH, '//button[text()="Etape suivante"]')
    # finally:
    #     pass


# driver.implicitly_wait(1000)


def write_results(places_are_already_taken, desk_value, now):
    with open(Rdv_filename, 'a') as f:
        if places_are_already_taken:
            f.write('{} No place is available! Desk Tested {}\n'.format(now, desk_value))
        else:
            f.write('{} At least one place is available! Desk {}\n'.format(now, desk_value))


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
    while True:
        try:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            places_are_already_taken, desk_value, desk_key = check_available_spot(now)
        except Exception as e:
            user_notificator(now)
            log_error(repr(e), str(now))
        else:
            if not places_are_already_taken:
                display(desk_value, now)
                open_appointment_page(desk_key)
            write_results(places_are_already_taken, desk_value, now)
        print('Last Desk checked ' + desk_value + ' ' + now)
        sleep(60)


if __name__ == '__main__':
    main()
