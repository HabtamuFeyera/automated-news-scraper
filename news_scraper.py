import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import openpyxl
import re
import os
import logging
from time import sleep

class NewsScraper:
    def __init__(self, search_phrase, category, num_months):
        self.search_phrase = search_phrase
        self.category = category
        self.num_months = num_months
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.append(["Title", "Date", "Description", "Picture Filename", "Search Phrase Count", "Contains Money"])

    def get_month_range(self):
        today = datetime.today()
        start_date = today.replace(day=1)
        months = []
        for i in range(self.num_months):
            months.append((start_date - timedelta(days=1)).strftime('%Y/%m'))
            start_date = start_date.replace(day=1) - timedelta(days=1)
        return months

    def scrape_news(self):
        months = self.get_month_range()
        for month in months:
            url = f"https://apnews.com/{month}"
            response = self.get_response(url)
            if response:
                soup = BeautifulSoup(response.text, 'html.parser')
                headlines = soup.find_all(class_='Component-headline-0-2-57')
                self.logger.info(f"Scraping news for {month}:")
                for headline in headlines:
                    if self.search_phrase.lower() in headline.text.lower() and self.category.lower() in url.lower():
                        news_url = f"https://apnews.com{headline.find('a')['href']}"
                        news_response = self.get_response(news_url)
                        if news_response:
                            news_soup = BeautifulSoup(news_response.text, 'html.parser')
                            title = news_soup.find('h1').text.strip()
                            date = news_soup.find(class_='Timestamp__date--3VCBF').text.strip()
                            description = news_soup.find(class_='Article__content--prolog').text.strip()
                            search_phrase_count = len(re.findall(self.search_phrase.lower(), title.lower() + description.lower()))
                            contains_money = any(re.findall(r'\$\d+(?:\.\d+)?|\d+\s*(?:dollars|usd)', title.lower() + description.lower()))

                            img_url = news_soup.find(class_='Image__image--2mkws')['src']
                            img_response = self.get_response(img_url)
                            if img_response:
                                img_filename = os.path.basename(img_url)
                                with open(img_filename, 'wb') as img_file:
                                    img_file.write(img_response.content)
                            else:
                                img_filename = None

                            self.ws.append([title, date, description, img_filename, search_phrase_count, contains_money])
                            self.logger.info(f"Title: {title}")
                            self.logger.info(f"Date: {date}")
                            self.logger.info(f"Description: {description}")
                            self.logger.info(f"Search Phrase Count: {search_phrase_count}")
                            self.logger.info(f"Contains Money: {contains_money}")
                            self.logger.info(f"Image Filename: {img_filename}")
            else:
                self.logger.error(f"Failed to retrieve news for {month}")

        self.wb.save("news_data.xlsx")

    def get_response(self, url):
        retries = 3
        for _ in range(retries):
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    return response
                else:
                    self.logger.warning(f"Failed to get response from {url}")
            except requests.RequestException as e:
                self.logger.warning(f"Request to {url} failed: {e}")
            sleep(2)  # Wait for 2 seconds before retrying
        return None

def main():
    # Fetch parameters from Robocloud Work Items
    search_phrase = os.getenv("SEARCH_PHRASE")
    category = os.getenv("NEWS_CATEGORY")
    num_months = int(os.getenv("NUM_MONTHS"))
    
    scraper = NewsScraper(search_phrase, category, num_months)
    scraper.scrape_news()

if __name__ == "__main__":
    main()
