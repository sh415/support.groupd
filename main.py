import uvicorn
import platform
import os
import time
import pyperclip
import requests
from random import *
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

app = FastAPI()

def driverInit():
    try:
        # options = webdriver.ChromeOptions()
        # # options.add_argument('headless')
        # # options.add_argument("no-sandbox")
        # # options.add_argument('window-size=1920x1080')
        # # options.add_argument("disable-gpu")
        # # options.add_experimental_option('excludeSwitches', ['enable-logging'])
        # operaitor = platform.system()
        # if (operaitor == 'Windows'):
        #     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        # elif (operaitor == 'Linux'):
        #     driver = webdriver.Chrome(options=options)

        options = webdriver.ChromeOptions()
        driver_path = ChromeDriverManager().install()
        correct_driver_path = os.path.join(os.path.dirname(driver_path), "chromedriver.exe")
        driver = webdriver.Chrome(service=Service(executable_path=correct_driver_path), options=options)
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

def driverQuit(driver):
    try:
        driver.quit()
        return True
    except Exception as e:
        print('driverQuit error', e)
        return False


    try:
        req = { 'email': email } 
        response = requests.post("https://groupd-support.net/dentphoto/email", data = req)
        return response.json()

    except Exception as e:
        print(e)

def login_searchad(driver, ID, PW, isNaver):
    try:
        driver.get("https://searchad.naver.com/")
        time.sleep(uniform(3.0, 5.0))

        if (isNaver): # 네이버 계정으로 로그인
            login_btn = driver.find_element(By.CSS_SELECTOR, '.naver_login_btn')
            # login_btn.click()
            driver.execute_script("arguments[0].click();", login_btn)
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

def new_device(driver):
    try:
        button_new_device = driver.find_element(By.ID, 'new.save')
        button_new_device.click()
        time.sleep(uniform(3.0, 5.0))

        return True
    
    except Exception as e:
        print('new_device error', e)
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

        time.sleep(uniform(3.0, 5.0))

        return digit

    except Exception as e:
        print('scrap_searchad error', e)
        return False

@app.get("/")
def read_root():
    return {"server": "support.groupd alive..."}
    
@app.post("/responses")
async def send_response():
    try:
        return JSONResponse(status_code=200, content={ 'message': True })

    except Exception as e:
        return JSONResponse(status_code=500, content={ 'message': False, 'error': str(e) })

class SearchAdRequest(BaseModel):
    id: str
    pw: str
    isNaver: bool

@app.post("/searchad", description="네이버 검색광고비 확인")
def searchad(request_body: SearchAdRequest):
    try:
        driver = driverInit()

        # 응답유형
        # code: 1 로그인 실패
        # code: 2 스크랩 실패
        # code: 3 드라이버 종료 실패
        # code: 4 정상
        # code: 5 오류

        ID = request_body.id
        PW = request_body.pw
        isNaver = request_body.isNaver
        
        login = False
        login = login_searchad(driver, ID, PW, isNaver)
        if (login == False):
            return JSONResponse(status_code=500, content={ 'message': False, 'error': 'login_searchad false', 'code': 1 })
        
        isNew = False
        isNew = new_device(driver)
        if (isNew):
            print('새로운 기기(브라우저)에서 로그인 처리')

        scrap = False
        scrap = scrap_searchad(driver)
        if (scrap == False):
            return JSONResponse(status_code=500, content={ 'message': False, 'error': 'scrap_searchad false', 'code': 2 })

        quit = True
        quit = driverQuit(driver)
        if (quit == False):
            return JSONResponse(status_code=500, content={ 'message': False, 'error': 'driverQuit false', 'code': 3 })
    
        return JSONResponse(status_code=200, content={ 'message': True, 'scrap': scrap, 'code': 4 })

    except Exception as e:
        return JSONResponse(status_code=500, content={ 'message': False, 'error': str(e), 'code': 5 })

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port = 7001)