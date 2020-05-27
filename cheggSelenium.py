#House Chegg
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import time
import pickle
import json

import os


def loginAndSaveSess(driver):
	##BEWARE OF CAPTCHA
	loginURL = 'https://www.chegg.com/auth?action=login'

	driver.get("http://www.google.com")
	#driver.find_element_by_id("emailForSignIn").send_keys("TEST1")
	#driver.find_element_by_id("passwordForSignIn").send_keys("TEST2")
	time.sleep(3)
	#driver.find_element_by_name("login").click()

	pickle.dump(driver.get_cookies(), open('session.pkl', 'wb'))

def loadSession(driver):
	driver.get("http://www.google.com")
	time.sleep(1)
	cookies = pickle.load(open('session.pkl', "rb"))
	for cookie in cookies:
		driver.add_cookie(cookie)
	return driver

def toPDF(driver, name):
	driver.execute_script('window.print();')
	time.sleep(3)
	files = os.listdir()
	print(files)
	for file in files:
		if file.endswith('.pdf'):
			os.rename(f'./{file}', f'./output/{name}.pdf')
			break



def setup():
	chrome_options = webdriver.ChromeOptions()
	settings = {
		   "recentDestinations": [{
				"id": "Save as PDF",
				"origin": "local",
				"account": "",
			}],
			"selectedDestinationId": "Save as PDF",
			"version": 2
		}
	downloadPath = '/home/justin/Progams/Chegg'
	prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings),'savefile.default_directory':downloadPath}

	chrome_options.add_experimental_option('prefs', prefs)
	chrome_options.add_argument('--kiosk-printing')
	chrome_options.add_argument("user-data-dir=selenium")
	driver = webdriver.Chrome(executable_path = './chromedriver', chrome_options=chrome_options)
	return driver

	