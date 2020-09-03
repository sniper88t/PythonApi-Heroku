# app.py
from flask import Flask, request, json, jsonify
import requests
import csv
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import time
from sys import platform

app = Flask(__name__)

#Read CSV File
def read_CSV(file, json_file):
    csv_rows = []
    with open(file) as csvfile:
        reader = csv.DictReader(csvfile)
        field = reader.fieldnames
        for row in reader:
            csv_rows.extend([{field[i]:row[field[i]] for i in range(len(field))}])
        convert_write_json(csv_rows, json_file)

#Convert csv data into json
def convert_write_json(data, json_file):
    with open(json_file, "w") as f:
        f.write(json.dumps(data, sort_keys=False, indent=4, separators=(',', ': '))) #for pretty

# function to take care of downloading file
def enable_download_headless(browser,download_dir):
    browser.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
    params = {'cmd':'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': download_dir}}
    browser.execute("send_command", params)

def initChromeDriver():
    # instantiate a chrome options object so you can set the size and headless preference
    # some of these chrome options might be uncessary but I just used a boilerplate
    # change the <path_to_download_default_directory> to whatever your default download folder is located
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--verbose')
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": "<path_to_download_default_directory>",
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing_for_trusted_sources_enabled": False,
        "safebrowsing.enabled": False
    })
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')

    chromedriver = "chromedriver"
    # initialize driver object and change the <path_to_chrome_driver> depending on your directory where your chromedriver should be
    driver = webdriver.Chrome(chrome_options=chrome_options, executable_path="chromedriver")

    # change the <path_to_place_downloaded_file> to your directory where you would like to place the downloaded file
    #file = os.environ['USERPROFILE'] + '\Downloads'
    file = os.environ['HOME'] + "/Downloads"
    download_dir = file

    # function to handle setting up headless download
    enable_download_headless(driver, download_dir)
    return driver

# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"

@app.route('/get_auth', methods=['POST'])
def get_auth():
    brand = request.form.get('brand')
    client_id = request.form.get('client_id')
    email = request.form.get('email')
    password = request.form.get('password')

    url = "https://api-gtm.grubhub.com/auth"
    payload = {
        'brand': brand,
        'client_id': client_id,
        'email': email,
        'password': password
    }

    headers = {
        'authority': 'api-gtm.grubhub.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'accept': 'application/json',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
        'content-type': 'application/json',
        'origin': 'https://restaurant.grubhub.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://restaurant.grubhub.com/login',
        'accept-language': 'en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,de;q=0.6,da;q=0.5,nb;q=0.4,is;q=0.3,af;q=0.2'
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    return json.dumps(response.json())

@app.route('/refresh_token', methods=['POST'])
def resfresh_token():
  client_id = request.form.get('client_id')
  refresh_token = request.form.get('refresh_token')

  print(client_id)
  print(refresh_token)

  url = "https://api-gtm.grubhub.com/auth"
  payload = {
    'client_id': client_id,
    'refresh_token': refresh_token
  }

  headers = {
    'authority': 'api-gtm.grubhub.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'accept': 'application/json',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'content-type': 'application/json',
    'origin': 'https://restaurant.grubhub.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://restaurant.grubhub.com/login',
    'accept-language': 'en-US,en;q=0.9,tr-TR;q=0.8,tr;q=0.7,de;q=0.6,da;q=0.5,nb;q=0.4,is;q=0.3,af;q=0.2'
  }

  response = requests.post(url, headers=headers, data=json.dumps(payload))
  return json.dumps(response.json())

@app.route('/postmates/login', methods=['POST'])
def postmate_login():
    email = request.form.get('email')
    password = request.form.get('password')

    if platform == "linux" or platform == "linux2":
        file = os.environ['HOME'] + "/Downloads/Deliveries.csv"
    if os.path.exists(file):
        os.remove(file)
        print("File Removed!")
    print("path = " + file)

    driver = initChromeDriver()
    url = "https://partner.postmates.com/login"
    try:
        driver.set_page_load_timeout(-1)
        driver.get(url)
        time.sleep(6)
        print("Page Loaded")

        driver.find_element_by_name("email").send_keys(email)
        time.sleep(1)
        driver.find_element_by_name("password").send_keys(password)
        time.sleep(1)
        submit = driver.find_element_by_xpath("//div[@class='content']")
        submit.click()
        time.sleep(6)
        print("============ Login Submitted ============")
        submitlog = driver.find_element_by_xpath(
            "//div[@class='simple-button simple-button--diminished']/button[@class='button button']")
        submitlog.click()
        time.sleep(2)
        print("============ First Step ============")
        submitone = driver.find_element_by_xpath(
            "//div[@class='simple-button simple-button--primary simple-button--big csv-modal__button']/button[@class='button button']")
        submitone.click()
        time.sleep(4)
        print("============ Second Step ============")

        if platform == "linux" or platform == "linux2":
            file = os.environ['HOME'] + "/Downloads/Deliveries.csv"
            #file = "/root/Downloads/Deliveries.csv"
        elif platform == "win64":
            file = os.environ['USERPROFILE'] + '\Downloads\Deliveries.csv'
        print("Open CSV File");
        print(file)
        if os.path.exists(file):
            print("OK FILE DETECTED")

        path = os.path.dirname(os.path.abspath(__file__))
        json_file = path + '/csv.json'
        read_CSV(file, json_file)

    except NoSuchElementException:
        print('No found Element')
        driver.quit()

    #with open(json_file) as f:
        #data = json.load(f)
        #return json.dumps(data)

    with open(json_file, encoding='utf-8', errors='ignore') as json_data:
        data = json.load(json_data, strict=False)
    return json.dumps(data)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)