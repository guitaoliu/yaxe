netid = "" #NetID
password = "" #密码

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

driver = webdriver.Chrome()

driver.get('http://ehall.xjtu.edu.cn')

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//span[text()='登录']"))).click()

if driver.current_url == "https://org.xjtu.edu.cn/openplatform/login.html":
  driver.implicitly_wait(0.5)
  driver.find_element_by_class_name("username").send_keys(netid)
  driver.implicitly_wait(0.5)
  driver.find_element_by_class_name("pwd").send_keys(password)
  driver.implicitly_wait(0.5)
  driver.find_element_by_id("account_login").click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[text()='成绩查询']"))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[text()='进入服务']"))).click()

time.sleep(1)
wins = driver.window_handles
driver.switch_to.window(wins[-1])

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='移动应用学生']"))).click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='详情']")))
driver.find_elements_by_xpath("//div[text()='全部' and @class='jqx-tabs-titleContentWrapper jqx-disableselect']")[0].click()

time.sleep(10)
driver.quit()