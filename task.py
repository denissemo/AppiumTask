import os
import datetime
from appium import webdriver
import unittest
import json


class MainTest(unittest.TestCase):

    def setUp(self) -> None:
        desired_caps = {
            "platformName": "android",
            "deviceName": "192.168.72.101:5555",
            "app": os.path.join(os.getcwd(), "APK\\TripAdvisor.apk")
        }
        self.driver = webdriver.Remote("http://localhost:4723/wd/hub",
                                       desired_caps)

    def tearDown(self) -> None:
        self.driver.quit()

    def test_find_hotel(self):
        # wait for loading app
        self.driver.implicitly_wait(10)
        close_btn = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/onboarding_close_x")
        close_btn.click()
        login_skip = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/login_skip")
        login_skip.click()
        no_thanks = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/no_thanks")
        no_thanks.click()

        search = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/search_image")
        search.click()
        query_text = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/what_query_text")
        # find required hotel
        query_text.send_keys("The Grosvenor Hotel")
        self.driver.implicitly_wait(20)
        h = self.driver.find_elements_by_id(
            "com.tripadvisor.tripadvisor:id/title")
        h[0].click()

        dates = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/set_dates_button")
        dates.click()

        # current date
        fst_date = datetime.date.today()
        try:
            # add 3 days to current date
            snd_date = datetime.datetime.strptime(
                "{}-{}-{}".format(fst_date.year, fst_date.month,
                                  fst_date.day + 3), "%Y-%m-%d")
        except ValueError:
            # if date is not valid use 5 day of next month
            snd_date = datetime.datetime.strptime(
                "{}-{}-{}".format(fst_date.year, fst_date.month + 1, 5),
                "%Y-%m-%d")
        check_in = self.driver.find_element_by_accessibility_id(str(fst_date))
        check_in.click()

        check_out = self.driver.find_element_by_accessibility_id(
            str(snd_date.date()))
        check_out.click()

        hide_prices = self.driver.find_element_by_id(
            "com.tripadvisor.tripadvisor:id/text_links_open_close_button")

        hide_prices.click()

        # scroll for watching all prices
        size = self.driver.get_window_size()
        startY = int(size["height"] * 0.80)
        endY = int(size["height"] * 0.60)
        startX = int(size["width"] / 2)
        self.driver.swipe(startX, startY, startX, endY, 1000)

        # do screenshot
        file_name = "screenshot.png"
        self.driver.save_screenshot(os.path.join(os.getcwd(), file_name))

        # get prices
        prices = self.driver.find_elements_by_id(
            "com.tripadvisor.tripadvisor:id/hotel_minor_provider_layout")

        # prices dict
        d = {}

        for price in prices:
            d.update({price.find_element_by_id(
                "com.tripadvisor.tripadvisor:id/title").text:
                          price.find_element_by_id(
                              "com.tripadvisor.tripadvisor:id/price").text})

        # write prices to json file
        with open("prices.json", "w") as outfile:
            json.dump(d, outfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(MainTest)
    unittest.TextTestRunner(verbosity=1).run(suite)
