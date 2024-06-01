from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

current_time = datetime.now()
service = Service(executable_path='./chromedriver')
options = Options()
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=service, options=options)

def read_numbers_from_file(filename):
    data = {}
    crn_count = 1  # Counter for CRNs
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
            
            if len(lines) > 0:
                label, value = lines[0].split(':', 1)
                data['username'] = value.strip()
                
            if len(lines) > 1:
                label, value = lines[1].split(':', 1)
                data['password'] = value.strip()
            
            if len(lines)>2:
                label, value = lines[2].split(':', 1)
                data['registration_time'] = value.strip()
                
            for i, line in enumerate(lines[3:], start=1):
                if ':' in line:
                    label, value = line.split(':', 1)
                    value = value.strip()
                    if value:
                        data[f'crn{crn_count}'] = int(value)
                        crn_count += 1

    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found. \nmake sure it has the same directory as this file")
    except ValueError as e:
        print(f"Error: {e}. \nPlease ensure the file contains valid characters.")
    
    return data


def wait_until(data):

    today = datetime.today()
    target_time = datetime.strptime(data['registration_time'], "%H:%M:%S").replace(year=today.year, month=today.month, day=today.day)
    current_time = datetime.now()
    # Calculate the time difference
    time_difference = (target_time - current_time).total_seconds()
    
    if time_difference > 0:
        print(f"Waiting for {time_difference} seconds.")
        time.sleep(time_difference)
    else:
        print("Target time has already passed. Please launch the program within 24 hours of registration open")
        driver.quit()

def mainrun(data):
    try:

        driver.get("https://registration.gosolar.gsu.edu/StudentRegistrationSsb/ssb/registration/registration")
        WebDriverWait(driver,50).until(EC.presence_of_element_located((By.ID, 'registerLink')))
        
        driver.find_element(By.ID, 'registerLink').click()
        WebDriverWait(driver,50).until(EC.presence_of_element_located((By.ID, 'loginForm:username')))
        
        driver.find_element(By.ID, 'loginForm:username').send_keys(data['username'])
        password = driver.find_element(By.ID,'loginForm:password')
        password.send_keys(data['password'])

        wait_until(data_dictionary)
        
        password.send_keys(Keys.ENTER)
        print("Verify with DUO")
        WebDriverWait(driver,900).until(EC.presence_of_element_located((By.ID, 'trust-browser-button')))
        driver.find_element(By.ID,'trust-browser-button').click()
        WebDriverWait(driver,900).until(EC.presence_of_element_located((By.ID, 's2id_txt_term')))
        driver.find_element(By.ID, 's2id_txt_term').click()
        WebDriverWait(driver,900).until(EC.presence_of_element_located((By.ID, '202408')))
        driver.find_element(By.ID,'202408').click()
        driver.find_element(By.ID,'term-go').click()
        WebDriverWait(driver,900).until(EC.presence_of_element_located((By.ID, 'enterCRNs-tab')))
        driver.find_element(By.ID,'enterCRNs-tab').click()
        time.sleep(1)

        crn_search = driver.find_element(By.ID,'txt_crn1')
        crn_list = list(data.values())[3:]
        counter = 1
        
        for i in range(len(crn_list)-1):
            driver.find_element(By.ID,'addAnotherCRN').click()

        for i in crn_list:
            crn_search= driver.find_element(By.ID,('txt_crn'+str(counter)))
            crn_search.send_keys(i)
            counter+=1
        driver.find_element(By.ID,'addCRNbutton').click()
        time.sleep(30)
        
    finally:
        driver.quit()

file_name = 'registration_information.txt'
data_dictionary = read_numbers_from_file(file_name)
mainrun(data_dictionary)