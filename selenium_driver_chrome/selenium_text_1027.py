
# coding: utf-8

# In[1]:

#背包客棧控制測試
from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup

chrome_path = "D:\Moyege\Work\@PROJECT\selenium_driver_chrome\chromedriver.exe" #chromedriver.exe執行檔所存在的路徑
web = webdriver.Chrome(chrome_path)

web.get('https://www.backpackers.com.tw/forum/')
web.set_window_position(0,0) #瀏覽器位置
# web.set_window_size(700,700) #瀏覽器大小
# time.sleep(5)

web.find_element_by_xpath("//input[@class='placeholder']").send_keys("台北")
web.find_element_by_xpath("//button[@class='button searchbtn']").submit()

# pageSource = web.page_source
# print (pageSource)


# length = len（ web.find_elements_by_tag_name（"a"）

#     for i in range（0,length）：

#     link = links[i]

#     if not （"_blank" in link.get_attribute（"target"） or "http" in link.get_attribute（"href"））：

# link.click

# driver.back




# r1 = web.find_elements_by_class_name("gs-title")
# print (r1)


# web.find_element_by_xpath("//div[@class='gsc-tabHeader gsc-inline-block gsc-tabhActive']").click()
# web.find_element_by_link_text('天氣預報').click() #點擊頁面上"天氣預報"的連結
# time.sleep(5)

# web.close()

