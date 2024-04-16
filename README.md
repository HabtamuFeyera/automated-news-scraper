# Automated News Scraper

This project is an automated web scraper designed to extract news articles from a news website. It gathers relevant information such as titles, dates, descriptions, and checks for the presence of specific phrases or keywords. Additionally, it downloads associated images and saves all data into an Excel file for further analysis.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Contributing](#contributing)
- [License](#license)

## Features

- Scrapes news articles from a specified website.
- Allows filtering by search phrase and news category.
- Checks for the presence of specific keywords or phrases in titles and descriptions.
- Downloads associated images.
- Saves data into an Excel file.

## Installation

1. Clone the repository:
git clone https://github.com/HabtamuFeyera/automated-news-scraper.git
cd automated-news-scraper


2. Install dependencies:
pip install -r requirements.txt


## Usage

1. Navigate to the project directory:
cd automated-news-scraper


2. Run the scraper script:
python ap_news_scraper/ap_news_scraper.py

3. Follow the prompts to enter the URL of the news website, search phrase, news category, and number of months to search.

## Dependencies

- [RPA Framework](https://github.com/robocorp/rpaframework)
- [Pandas](https://github.com/pandas-dev/pandas)

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
