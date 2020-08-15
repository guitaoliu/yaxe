netid = "" #NetID
password = "" #密码

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import xlwt
import re

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

time.sleep(0.5)
wins = driver.window_handles
driver.switch_to.window(wins[-1])

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='移动应用学生']"))).click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='详情']")))
driver.find_elements_by_xpath("//div[text()='全部' and @class='jqx-tabs-titleContentWrapper jqx-disableselect']")[0].click()

time.sleep(0.5)
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//a[text()='详情']")))

count_text = driver.find_element_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//span[@class='bh-pager-num']").get_attribute("textContent")
count = result1 = re.findall(r'\d+', count_text)[2]

driver.find_element_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//div[contains(@id, 'dropdownlistWrapper')]").click()
# driver.find_element_by_xpath("//div[contains(@id, 'listBoxContentinnerListBox')]/div").scrollTop=100000
# driver.find_element_by_xpath("//span[text()='20']").click()

workbook = xlwt.Workbook(encoding = 'utf-8')
worksheet = workbook.add_sheet('Grade')

for page in range(int(int(count)/10)+1):

  size = int(count) - page * 10 if (page + 1) * 10 >= int(count) else 10
  time.sleep(1)
  for i in range(size):  
    cell = driver.find_elements_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[i].find_elements_by_xpath("./td/span")
    grade = driver.find_elements_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[i].find_element_by_xpath("./td[@class='jqx-cell jqx-grid-cell jqx-item jqx-center-align']")
    last_line = 0
    for j in range(len(cell)):
      worksheet.write(i + page * 10 + 1, j, label = cell[j].get_attribute("textContent"))
      last_line = j
    last_line += 1  
    worksheet.write(i + page * 10 + 1, last_line , label = grade.get_attribute("textContent"))


    link = driver.find_elements_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[i].find_element_by_xpath("./td/a").click()
    time.sleep(0.2)

    rank_data = driver.find_elements_by_xpath("//div[@class='bh-mt-16 h3  jw-fontWeight-normal']")
    rank_text = rank_data[0].find_element_by_xpath("./span[@class='pm-bfb']").get_attribute("textContent")
    last_line += 1
    worksheet.write(i + page * 10 + 1, last_line , label = rank_text)

    class_grade_list = rank_data[2].find_elements_by_xpath("./span")
    for j in range(len(class_grade_list)):
      class_grade_text = class_grade_list[j].find_elements_by_xpath("./span")[2].get_attribute("textContent")
      last_line += 1
      worksheet.write(i + page * 10 + 1, last_line , label = class_grade_text)

    rank_group = driver.find_elements_by_xpath("//div[@class='bh-col-md-4 ']")
    rank_pjf_text = rank_group[0].find_element_by_xpath(".//span[@id='cjfb-pjf']").get_attribute("textContent")
    rank_zdf_text = rank_group[1].find_element_by_xpath(".//span[@id='cjfb-zdf']").get_attribute("textContent")
    rank_zgf_text = rank_group[2].find_element_by_xpath(".//span[@id='cjfb-zgf']").get_attribute("textContent")
    last_line += 1
    worksheet.write(i + page * 10 + 1, last_line , label = rank_pjf_text)
    last_line += 1
    worksheet.write(i + page * 10 + 1, last_line , label = rank_zdf_text)
    last_line += 1
    worksheet.write(i + page * 10 + 1, last_line , label = rank_zgf_text)

    # 课程排名有bug暂时搁置
    # driver.find_element_by_xpath("//div[@id='dropdownlistContentcjcx-rank-container']").click()
    # driver.find_elements_by_xpath("//span[@class='jqx-listitem-state-normal jqx-item jqx-rc-all']")[1].click()

    # time.sleep(10)
    # rank_group_1 = driver.find_elements_by_xpath("//div[@class='bh-col-md-4 ']")
    # print(len(rank_group_1))
    # rank_pjf_text_1 = rank_group_1[0].find_element_by_xpath(".//span[@id='cjfb-pjf']").get_attribute("textContent")
    # rank_zdf_text_1 = rank_group_1[1].find_element_by_xpath(".//span[@id='cjfb-zdf']").get_attribute("textContent")
    # rank_zgf_text_1 = rank_group_1[2].find_element_by_xpath(".//span[@id='cjfb-zgf']").get_attribute("textContent")
    # print(rank_pjf_text_1, rank_zdf_text_1, rank_zgf_text_1)
    
    driver.find_element_by_xpath("//div[@class='bh-property-dialog-container bh-animated bh-card bh-card-lv2 bh-intoRight']/i").click()
    time.sleep(0.2)
  driver.find_elements_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//i[@class='iconfont icon-keyboardarrowright']/..")[1].click()
# 保存
workbook.save('Grade.xls')

time.sleep(10)
driver.quit()