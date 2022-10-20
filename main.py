import os
import sys
import time
import re
import socket
import json

import requests
from PIL import Image
from pyzbar.pyzbar import decode
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')


# 执行打卡
def send(sessionid):
    headers = {
        'Content-Type': 'application/json',
        'X-Auth-Token': sessionid,
        'User-Agent': 'Mozilla/5.0 (Linux; Android 11; Pixel 4 XL Build/RQ3A.210705.001; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/83.0.4103.106 Mobile Safari/537.36 AliApp(DingTalk/5.1.5) com.alibaba.android.rimet/13534898 Channel/212200 language/zh-CN UT4Aplus/0.2.25 colorScheme/light'
    }
    url = "https://skl.hdu.edu.cn/api/punch"
    data = {
        "currentLocation": "浙江省杭州市钱塘区",
        "city": "杭州市",
        "districtAdcode": "330114",
        "province": "浙江省",
        "district": "钱塘区",
        "healthCode": 0,
        "healthReport": 0,
        "currentLiving": 0,
        "last14days": 0
    }

    for retryCnt in range(3):
        try:
            res = requests.post(url, json=data, headers=headers, timeout=30)
            if res.status_code == 200:
                # message(ur, "成功")
                return "打卡成功"
            elif retryCnt == 3:
                print("提交表单失败")
                #　message(ur, "失败")
                # wechatNotice(os.environ["SCKEY"], "打卡失败")
        except Exception as e:
            if retryCnt < 2:
                print(e.__class__.__name__ + "打卡失败，正在重试")
                time.sleep(3)
            else:
                print("打卡失败")
                # message(ur, "失败")
                # wechatNotice(os.environ["SCKEY"], "打卡失败")

def getCookies():
    rep = requests.get(url="https://raw.githubusercontent.com/handsomeXZ/branch-filestorage-action/actions/filedb/cookie")
    return rep.text

def Entry(browser, path):
    sessionId = ''
    browser.get("https://login.dingtalk.com/oauth2/challenge.htm?client_id=dinghd3ewha7rzdjn3my&response_type=code&scope=openid&prompt=consent&state=NlSNLH8mCoWrlc4ulBj&redirect_uri=https%3A%2F%2Fskl.hdu.edu.cn%2Fapi%2Flogin%2Fdingtalk%2Fauth%3Findex%3Dpasscard.html")
    time.sleep(1)
    cookie_str = getCookies()
    if len(cookie_str)<14:
        return sessionId
    cookies = eval(cookie_str)
    for cookie in cookies:
        browser.add_cookie(cookie)
    print(browser.get_cookies())
    browser.get("https://login.dingtalk.com/oauth2/challenge.htm?client_id=dinghd3ewha7rzdjn3my&response_type=code&scope=openid&prompt=consent&state=NlSNLH8mCoWrlc4ulBj&redirect_uri=https%3A%2F%2Fskl.hdu.edu.cn%2Fapi%2Flogin%2Fdingtalk%2Fauth%3Findex%3Dpasscard.html")
    time.sleep(1)
    bt = browser.find_element(By.CLASS_NAME, 'module-confirm-button.base-comp-button.base-comp-button-type-primary')
    for i in range(12):
        try:
            bt.click()
            time.sleep(5)
            bt = browser.find_element(By.CLASS_NAME,
                                     'module-confirm-button.base-comp-button.base-comp-button-type-primary')
        except Exception as e:

            break
        try:
            sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
        except Exception as e:
            sessionId = ''
        if sessionId is not None and sessionId != '':
            break

    return sessionId

def RunScan(browser, path):
    browser.delete_all_cookies()
    browser.get("https://login.dingtalk.com/oauth2/challenge.htm?client_id=dinghd3ewha7rzdjn3my&response_type=code&scope=openid&prompt=consent&state=NlSNLH8mCoWrlc4ulBj&redirect_uri=https%3A%2F%2Fskl.hdu.edu.cn%2Fapi%2Flogin%2Fdingtalk%2Fauth%3Findex%3Dpasscard.html")
    time.sleep(5)
    browser.find_element(By.CLASS_NAME, 'base-comp-check-box.module-qrcode-op-item').click()
    time.sleep(1)
    browser.save_screenshot(path + "/Scan_Temp.png")
    img = Image.open(path + '/Scan_Temp.png')
    region = img.crop((250, 540, 470, 790))
    region.save(path + '/Scan.png')
    img = Image.open(path + '/Scan.png')
    decocdeQR = decode(img)
    url = decocdeQR[0].data.decode('ascii')
    data = {
        'url': url
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url="https://api.hiflow.tencent.com/engine/webhook/31/1582963297565736962", json=data,
                  headers=headers)
    for i in range(60):
        time.sleep(5)
        try:
            sessionId = browser.execute_script("return window.localStorage.getItem('sessionId')")
        except Exception as e:
            sessionId = ''

        if sessionId is not None and sessionId != '':
            file = open(path + "/cookie", 'w')
            file.write(str(browser.get_cookies()))
            file.close()
            break


if __name__ == '__main__':
    # https://login.dingtalk.com/oauth2/challenge.htm?client_id=dinghd3ewha7rzdjn3my&response_type=code&scope=openid&prompt=consent&state=lUQ2nF4gs5qfkAxILLf&redirect_uri=https%3A%2F%2Fskl.hdu.edu.cn%2Fapi%2Flogin%2Fdingtalk%2Fauth%3Findex%3D
    path = "/home/runner/work/branch-filestorage-action/branch-filestorage-action"
    driver = webdriver.Chrome(service=Service('chromedriver'), options=chrome_options)
    wait = WebDriverWait(driver, 3, 0.5)
    driver.set_window_size(720, 1280)
    # RunScan(driver, path)
    sessionId = Entry(driver, path)
    if sessionId is not None and sessionId != '':
        send(sessionId)
        exit()
    RunScan(driver, path)
    sessionId = Entry(driver, path)
    if sessionId is not None and sessionId != '':
        send(sessionId)
    #Server()
