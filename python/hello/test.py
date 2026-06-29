from selenium import webdriver
from  selenium.webdriver.chrome.service import  Service as ChromeService
from  selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
#2.输⼊百度⽹址:https://www.baidu.com
driver.get("https://www.baidu.com")
#3、找到输⼊框并输⼊“迪丽热巴”
#driver.find_element(By.CSS_SELECTOR,"#kw").send_keys("迪丽热巴")
#
#4、找到“百度⼀下”按钮并点击
#driver.find_element(By.CSS_SELECTOR,"#su").click()
#5、关闭浏览器
filename = "./images"+'.png'
driver.save_screenshot(filename)
print('testend')
driver.quit()
