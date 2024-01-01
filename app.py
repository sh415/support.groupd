import platform
import time
import requests
import pyperclip
from random import *
from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api
from flasgger import Swagger, swag_from
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

class WebDriverManager:
    def __init__(self):
        self.drivers = []

    def count_drivers(self):
        return len(self.drivers)

    def create_driver(self):
        driver = driverInit()
        self.drivers.append(driver)

        return driver

    def close_driver(self, driver):
        driver.quit()
        self.drivers.remove(driver)

manager = WebDriverManager() 

app = Flask(__name__)
api = Api(app)
CORS(app)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "version": "1.0.0",
            "title": "Your API",
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}
swagger = Swagger(app, config=swagger_config)

def driverInit():
    try:
        options = webdriver.ChromeOptions()
        # options.add_argument('headless')
        # options.add_argument("no-sandbox")
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        operaitor = platform.system()
        if (operaitor == 'Windows'):
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif (operaitor == 'Linux'):
            driver = webdriver.Chrome(options=options)

        return driver

    except Exception as e:
        print('driverInit error', e)
        return False

def driverInitHeadless():
    try:
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument("no-sandbox")
        # options.add_argument('window-size=1920x1080')
        # options.add_argument("disable-gpu")
        # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        operaitor = platform.system()
        if (operaitor == 'Windows'):
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        elif (operaitor == 'Linux'):
            driver = webdriver.Chrome(options=options)

        return driver

    except Exception as e:
        print('driverInit error', e)
        return False

def login_searchad(driver, ID, PW, isNaver):
    try:
        driver.get("https://searchad.naver.com/")
        time.sleep(uniform(3.0, 5.0))

        if (isNaver): # 네이버 계정으로 로그인
            login_btn = driver.find_element(By.CSS_SELECTOR, '.naver_login_btn')
            login_btn.click()
            time.sleep(uniform(3.0, 5.0))

            tabs = driver.window_handles
            driver.switch_to.window(tabs[-1])
            time.sleep(uniform(1.0, 2.0))

            input_id = driver.find_element(By.CSS_SELECTOR, '#id')
            input_id.click()
            pyperclip.copy(ID)
            input_id.send_keys(Keys.CONTROL, 'v')
            time.sleep(uniform(1.0, 2.0))

            input_pw = driver.find_element(By.CSS_SELECTOR, '#pw')
            input_pw.click()
            pyperclip.copy(PW)
            input_pw.send_keys(Keys.CONTROL, 'v')
            time.sleep(uniform(1.0, 2.0))

            input_sw = driver.find_element(By.CSS_SELECTOR, '.switch_checkbox')
            driver.execute_script("arguments[0].click();", input_sw)
            time.sleep(uniform(1.0, 2.0))

            button_login = driver.find_element(By.CSS_SELECTOR, '.btn_login')
            button_login.click()
            time.sleep(uniform(3.0, 5.0))
        
        else: # 검색광고 계정으로 로그인
            input_id = driver.find_elements(By.CSS_SELECTOR, '.input_text')[1]
            input_id.click()
            pyperclip.copy(ID)
            input_id.send_keys(Keys.CONTROL, 'v')
            time.sleep(uniform(1.0, 2.0))

            input_pw = driver.find_elements(By.CSS_SELECTOR, '.input_text')[2]
            input_pw.click()
            pyperclip.copy(PW)
            input_pw.send_keys(Keys.CONTROL, 'v')
            time.sleep(uniform(1.0, 2.0))

            button_login = driver.find_element(By.CSS_SELECTOR, '.btn_login').find_element(By.CSS_SELECTOR, 'button')
            button_login.click()
            time.sleep(uniform(3.0, 5.0))

        return True

    except Exception as e:
        print('login_searchad error', e)
        return False

def scrap_searchad(driver):
    try:
        # 팝업 닫기
        tabs = driver.window_handles
        for idx, tab in enumerate(tabs):
            print(tab)
            if (idx >= 1):
                driver.switch_to.window(tabs[1])
                driver.close()
        time.sleep(uniform(3.0, 5.0))
        
        driver.switch_to.window(tabs[0])
        time.sleep(uniform(1.0, 2.0))
        biz_money = driver.find_element(By.CSS_SELECTOR, '.biz_money.v2').find_element(By.CSS_SELECTOR, '.num_list').find_elements(By.CSS_SELECTOR, '.blind')
        digit = ""
        for idx, biz in enumerate(biz_money):
            digit = digit + biz.get_attribute('innerText')
        time.sleep(uniform(1.0, 2.0))

        return digit

    except Exception as e:
        print('login_searchad error', e)
        return False

def driverQuit(driver):
    try:
        driver.quit()
        return True
    
    except Exception as e:
        print('driverQuit error', e)
        return False

@app.route('/')
def index():
    return 'cloud_keywdcheck_server'

# 응답 api
@app.route('/responses', methods=['POST'])
@swag_from({
    'responses': {
        200: {
            'description': 'Successful response',
            'examples': {
                'application/json': {'message': True}
            }
        },
        500: {
            'description': 'Error response',
            'examples': {
                'application/json': {'message': False, 'error': 'Error message'}
            }
        }
    }
})
def server_responses():
    try:
        # res = request.json
        # url = res.get('url')
        # print(url)
        return { 'message': True }, 200
    
    except Exception as e:
        return { 'message': False, 'error': str(e) }, 500

# 네이버 검색광고 비용 체크 api
@app.route("/searchad", methods=["POST"])
@swag_from({
    'tags': ['searchad'],
    'description': '네이버 검색광고 비용을 확인하는 기능입니다.',
    'parameters': [
        {
            'name': 'keywds',
            'description': '아이디와 비밀번호를 입력하세요 (예: { "id": "아이디", "pw": "패스워드" })',
            'in': 'body',
            'type': 'string',
            'required': 'true',
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response',
            'examples': {
                'application/json': [{'href': 'example_url_1'}, {'href': 'example_url_2'}]
            }
        },
        500: {
            'description': 'Error response',
            'examples': {
                'application/json': {'message': False, 'error': 'Error message'}
            }
        }
    }
})
def searchad():
    try:
        driver = driverInit()

        ID = request.json.get('id')
        PW = request.json.get('pw')
        isNaver = request.json.get('isNaver')

        # 응답유형
        # code: 1 로그인 실패
        # code: 2 스크랩 실패
        # code: 3 드라이버 종료 실패
        # code: 4 정상
        # code: 5 오류

        scrap = False

        login = login_searchad(driver, ID, PW, isNaver)
        if (login == False):
           return { 'message': False, 'error': 'login_searchad error', 'code': 1 }, 500
        
        scrap = scrap_searchad(driver)
        if (scrap == False):
            return { 'message': False, 'error': 'scrap_searchad error', 'code': 2 }, 500

        quit = driverQuit(driver)
        if (quit == False):
             return { 'message': False, 'error': 'driverQuit error', 'code': 3 }, 500
    
        return { 'message': True, 'scrap': scrap, 'code': 4 }, 200

    except Exception as e:
        return { 'message': False, 'error': 'Exception error', 'code': 5 }, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True, use_reloader=False)