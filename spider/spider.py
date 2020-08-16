import re
import xlwt
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium import webdriver
netid = ""  # NetID
password = ""  # 密码


driver = webdriver.Chrome()

driver.get('http://ehall.xjtu.edu.cn')

WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, "//span[text()='登录']"))).click()

driver.implicitly_wait(0.5)
driver.find_element_by_class_name("username").send_keys(netid)
driver.implicitly_wait(0.5)
driver.find_element_by_class_name("pwd").send_keys(password)
driver.implicitly_wait(0.5)
driver.find_element_by_id("account_login").click()

WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, "//div[text()='成绩查询']"))).click()
WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, "//div[text()='进入服务']"))).click()

time.sleep(0.5)
wins = driver.window_handles
driver.switch_to.window(wins[-1])

WebDriverWait(driver, 10).until(EC.presence_of_element_located(
    (By.XPATH, "//a[text()='移动应用学生']"))).click()

WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[text()='详情']")))
driver.find_elements_by_xpath(
    "//div[text()='全部' and @class='jqx-tabs-titleContentWrapper jqx-disableselect']")[0].click()

time.sleep(0.5)
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//a[text()='详情']")))

count_text = driver.find_element_by_xpath(
    "//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//span[@class='bh-pager-num']").get_attribute("textContent")
count = result1 = re.findall(r'\d+', count_text)[2]

driver.find_element_by_xpath(
    "//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//div[contains(@id, 'dropdownlistWrapper')]").click()
# driver.find_element_by_xpath("//div[contains(@id, 'listBoxContentinnerListBox')]/div").scrollTop=100000
# driver.find_element_by_xpath("//span[text()='20']").click()

workbook = xlwt.Workbook(encoding='utf-8')
worksheet = workbook.add_sheet('Grade')

for page in range(int(int(count)/10)+1):

    size = int(count) - page * 10 if (page + 1) * 10 >= int(count) else 10
    time.sleep(1)
    for i in range(size):
        cell = driver.find_elements_by_xpath(
            "//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[i].find_elements_by_xpath("./td/span")
        grade = driver.find_elements_by_xpath("//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[
            i].find_element_by_xpath("./td[@class='jqx-cell jqx-grid-cell jqx-item jqx-center-align']")
        last_col = -1
        last_title = 0

        if page == 0 and i == 0:
          dis_title = ['学年学期', '课程名', '课程类别', '课程性质',
                      '学分', '学时', '成绩', 'GPA', '及格', '超过百分比', '平时成绩', '期末成绩', '平均分', '最低分', '最高分']
          for j in range(len(dis_title)):
              worksheet.write(0, j, label=dis_title[j])
              last_title = j

        dis_col_1 = [0, 1, 4, 5, 6, 7]
        for j in dis_col_1:
            last_col += 1
            worksheet.write(i + page * 10 + 1, last_col,
                            label=cell[j].get_attribute("textContent"))

        last_col += 1
        worksheet.write(i + page * 10 + 1, last_col,
                        label=grade.get_attribute("textContent"))

        dis_col_2 = [11, 52]
        for j in dis_col_2:
            last_col += 1
            worksheet.write(i + page * 10 + 1, last_col,
                            label=cell[j].get_attribute("textContent"))

        link = driver.find_elements_by_xpath(
            "//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//tr")[i].find_element_by_xpath("./td/a").click()
        time.sleep(0.2)

        rank_data = driver.find_elements_by_xpath(
            "//div[@class='bh-mt-16 h3  jw-fontWeight-normal']")
        rank_text = rank_data[0].find_element_by_xpath(
            "./span[@class='pm-bfb']").get_attribute("textContent")
        last_col += 1
        worksheet.write(i + page * 10 + 1, last_col, label=rank_text)

        class_grade_list = rank_data[2].find_elements_by_xpath("./span")
        for j in range(2):
            if j < len(class_grade_list): 
              class_grade_title = class_grade_list[j].find_elements_by_xpath(
                "./span")[0].get_attribute("textContent")
              class_grade_text = class_grade_list[j].find_elements_by_xpath(
                "./span")[2].get_attribute("textContent")
            else:
              class_grade_text = ''
            last_col += 1
            worksheet.write(i + page * 10 + 1, last_col,
                            label=class_grade_text)
            # if page == 0 and i == 0:
            #   last_title += 1
            #   worksheet.write(0, last_title, label=class_grade_title)

        rank_group = driver.find_elements_by_xpath(
            "//div[@class='bh-col-md-4 ']")
        rank_pjf_text = rank_group[0].find_element_by_xpath(
            ".//span[@id='cjfb-pjf']").get_attribute("textContent")
        rank_zdf_text = rank_group[1].find_element_by_xpath(
            ".//span[@id='cjfb-zdf']").get_attribute("textContent")
        rank_zgf_text = rank_group[2].find_element_by_xpath(
            ".//span[@id='cjfb-zgf']").get_attribute("textContent")

        last_col += 1
        worksheet.write(i + page * 10 + 1, last_col, label=rank_pjf_text)
        last_col += 1
        worksheet.write(i + page * 10 + 1, last_col, label=rank_zdf_text)
        last_col += 1
        worksheet.write(i + page * 10 + 1, last_col, label=rank_zgf_text)

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

        driver.find_element_by_xpath(
            "//div[@class='bh-property-dialog-container bh-animated bh-card bh-card-lv2 bh-intoRight']/i").click()
        time.sleep(0.2)
    driver.find_elements_by_xpath(
        "//div[@class='cjcx-tab-content-1 bh-mt-8 jqx-tabs-content-element jqx-rc-b']//i[@class='iconfont icon-keyboardarrowright']/..")[1].click()
# 保存
workbook.save('Grade.xls')

time.sleep(10)
driver.quit()
