from appium import webdriver
from time import sleep

def setUp():
    desired_caps = {
        'platformName': 'Android',
        'deviceName': 'emulator-5554',  # Adjust based on your emulator/device ID
        'appPackage': 'com.google.android.gm',
        'appActivity': 'ConversationListActivityGmail'
    }
    driver = webdriver.Remote('http://localhost:4723/wd/hub', desired_caps)
    return driver

def create_new_account(driver):
    driver.find_element_by_accessibility_id('Gmail').click()
    sleep(2)
    driver.find_element_by_android_uiautomator('new UiSelector().text("Add another account")').click()
    sleep(2)
    driver.find_element_by_android_uiautomator('new UiSelector().text("Google")').click()
    sleep(2)
    driver.find_element_by_android_uiautomator('new UiSelector().text("Create account")').click()
    sleep(2)
    driver.find_element_by_android_uiautomator('new UiSelector().text("For myself")').click()
    # Continue with the account creation steps...

if __name__ == '__main__':
    driver = setUp()
    for _ in range(20):
        create_new_account(driver)
        sleep(5)  # Adjust sleep time as necessary to allow for each account creation process
    driver.quit()
