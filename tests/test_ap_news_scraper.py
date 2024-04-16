import unittest
from ap_news_scraper.ap_news_scraper import ApnewsScraper

class TestApnewsScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = ApnewsScraper(
            url="https://apnews.com/",
            search_phrase="technology",
            news_category="Science",
            num_months=2
        )

    def test_open_website(self):
        self.scraper.open_website()
        self.assertTrue(self.scraper.browser.is_browser_open())

    def test_enter_search_phrase(self):
        self.scraper.open_website()
        self.scraper.enter_search_phrase()
        search_field_value = self.scraper.browser.get_value("//input[@id='search-input']")
        self.assertEqual(search_field_value, "technology")

    def test_select_news_category(self):
        self.scraper.open_website()
        self.scraper.select_news_category()
        # Assert category selection

    def test_choose_latest_news(self):
        self.scraper.open_website()
        self.scraper.choose_latest_news()
        # Assert latest news selection

    def test_extract_data_and_save_to_excel(self):
        self.scraper.open_website()
        self.scraper.enter_search_phrase()
        self.scraper.select_news_category()
        self.scraper.choose_latest_news()
        self.scraper.extract_data_and_save_to_excel()
        # Assert data extraction and Excel file creation

    def tearDown(self):
        self.scraper.browser.close_browser()

if __name__ == '__main__':
    unittest.main()
