import os
import re
import logging
from datetime import datetime, timedelta
from dateutil import parser
from urllib.parse import urlparse
import requests
import pandas as pd

from RPA.Browser.Selenium import Selenium
from RPA.HTTP import HTTP
from RPA.Robocorp.WorkItems import WorkItems

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ApnewsScraper:
    def __init__(self, url, search_phrase, news_category, num_months, excel_file="results/ap_news.xlsx"):
        self.browser = Selenium()
        self.http = HTTP()
        self.url = url
        self.search_phrase = search_phrase
        self.news_category = news_category
        self.num_months = int(num_months)
        self.excel_file = excel_file
        self.picture_folder = "data/news_pictures"
        os.makedirs(self.picture_folder, exist_ok=True)

    def open_website(self):
        try:
            self.browser.open_available_browser(self.url, maximized=True)
            logger.info(f"Opened website: {self.url}")
        except Exception as e:
            logger.error(f"Error opening website: {e}")

    def enter_search_phrase(self):
        search_field_xpath = "//input[@id='search-input']"
        try:
            self.browser.input_text(search_field_xpath, self.search_phrase)
            self.browser.press_keys(search_field_xpath, '\ue007')  # press Enter
            logger.info(f"Entered search phrase: {self.search_phrase}")
        except Exception as e:
            logger.error(f"Error entering search phrase: {e}")

    def select_news_category(self):
        if self.news_category:
            try:
                category_xpath = f"//span[text()='{self.news_category}']"
                self.browser.wait_until_element_is_visible(category_xpath, timeout=30)
                self.browser.click_element(category_xpath)
                logger.info(f"Selected news category: {self.news_category}")
            except Exception as e:
                logger.warning(f"Error selecting news category: {e}")

    def choose_latest_news(self):
        select_xpath = "//select[@id='search-sort-option']"
        try:
            self.browser.wait_until_page_contains_element(select_xpath, timeout=10)
            self.browser.click_element(select_xpath)
            logger.info("Clicked on the select element")
        except Exception as e:
            logger.error(f"Error occurred: {e}")

    def extract_data_and_save_to_excel(self):
        current_date = datetime.now()

        if self.num_months == 0 or self.num_months == 1:
            start_date = current_date.replace(day=1)
        elif self.num_months > 1:
            middle_date = current_date.replace(day=15)
            days_to_subtract = (self.num_months - 1) * 30
            new_date = middle_date - timedelta(days=days_to_subtract)
            start_date = new_date.replace(day=1)

        data = {
            "Title": [],
            "Date": [],
            "Description": [],
            "Title Count": [],
            "Description Count": [],
            "Money Present": [],
            "Picture Filename": []
        }

        i = 1
        while True:
            try:
                link_xpath = f"(//a[@class='u-clickable-card__link'])[{i}]"
                self.browser.wait_until_element_is_enabled(link_xpath, timeout=10)
                self.browser.scroll_element_into_view(link_xpath)
                paragraph = self.browser.get_text(f'(//div[@class="gc__excerpt"]//p)[{i}]')

                splitted = paragraph.split('...')
                date = splitted[0]

                if 'ago' in date:
                    current_time = datetime.now()
                    value, units, _ = date.split()
                    unit_mapping = {'hour': 'hours', 'hours': 'hours', 'minute': 'minutes', 'minutes': 'minutes', 'min\xadutes': 'minutes', 'day': 'days', 'days': 'days'}

                    delta = timedelta(**{unit_mapping[units]: int(value)})
                    date_obj = current_time - delta
                else:
                    date_obj = parser.parse(date)

                if start_date <= date_obj:
                    titles = self.browser.get_text(link_xpath)
                    data["Title"].append(titles)

                    description = splitted[1]
                    data["Description"].append(description)

                    data["Date"].append(date_obj)
                    count_title = titles.lower().count(self.search_phrase.lower())
                    count_description = description.lower().count(self.search_phrase.lower())
                    data["Title Count"].append(count_title)
                    data["Description Count"].append(count_description)

                    money_pattern = r'\$|\d+ dollars|\d+\s*USD'
                    money_in_title = re.search(money_pattern, titles, re.IGNORECASE)
                    money_in_description = re.search(money_pattern, description, re.IGNORECASE)

                    money_present = bool(money_in_title or money_in_description)
                    data["Money Present"].append(money_present)

                    picture_xpath = f"{link_xpath}/ancestor::div[@class='gc__card__media']//img"
                    picture_url = self.browser.find_element_by_xpath(picture_xpath).get_attribute("src")
                    picture_filename = self.download_picture(picture_url)
                    data["Picture Filename"].append(picture_filename)

                    i += 1
                else:
                    break
            except Exception as e:
                logger.error(f"Error occurred: {e}")
                break

        df = pd.DataFrame(data)
        df.to_excel(self.excel_file, index=False)
        logger.info(f"Data saved to {self.excel_file}")

    def download_picture(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                picture_filename = os.path.basename(urlparse(url).path)
                picture_path = os.path.join(self.picture_folder, picture_filename)
                with open(picture_path, "wb") as f:
                    f.write(response.content)
                return picture_filename
            else:
                logger.warning(f"Failed to download picture from {url}")
                return ""
        except Exception as e:
            logger.error(f"Error downloading picture: {e}")
            return ""
