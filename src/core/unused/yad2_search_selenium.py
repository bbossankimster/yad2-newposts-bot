from seleniumwire import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from settings import PROXY_OPT
import utils.url_mods as urlmod
import time
import json
import pandas as pd
from datetime import datetime, timedelta


SELENIUM_OPT = {
    'proxy': {
        'http': PROXY_OPT,
        'https': PROXY_OPT,
        'verify_ssl': False,
    },
    'binary_location': 'chromedriver.exe',
}

ID_COLUMN = 'id'

POST_COLUMNS = [
    ID_COLUMN, "title_1", "price", "Rooms",
    "city", "date_added", "date", "contact_name"
    ]
POST_DF_COLUMNS = POST_COLUMNS + ['url', 'tag']

STORED_POSTS_CSV = 'data/stored_posts.csv'
NEW_POSTS_CSV = 'data/new_posts.csv'
URLS_FILE = 'data/urls.txt'


class SearchEngine:
    def __init__(self) -> None:
        self._start_webdriver()

    def _start_webdriver(self):
        self.driver = webdriver.Chrome(seleniumwire_options=SELENIUM_OPT)
        test_url = 'https://www.yad2.co.il/api/pre-load/getFeedIndex/realestate/rent?topArea=2&area=1&city=5000&neighborhood=206&propertyGroup=apartments,houses&rooms=-1-2&price=1500--1&Order=3'
        self.driver.get('https://ip-api.com/')
        self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.COMMAND + 't')
        time.sleep(5)


class Yad2Search(SearchEngine):
    def __init__(self, urls, ignore_merchant=False) -> None:
        super().__init__()
        self.urls = urls
        self.ignore_merchant = ignore_merchant

    def _iter_posts(self):
        cntr = 0
        for url, tag in self.urls:
            print("\n***** TAG/URL...", tag, url)
            cntr += 1
            try:
                self.driver.get(url)
                time.sleep(3)
                content = self.driver.find_element(By.TAG_NAME, "pre").text
            except Exception as e:
                print("Exception...", e)
            else:
                posts_items = json.loads(content)
                for post in posts_items["feed"]["feed_items"]:
                    yield url, tag, post
            self.driver.get('https://ip-api.com/')
            self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.COMMAND + 't')

    def _iter_filtered_posts(self):
        cntr = 0
        for url, tag, post in self._iter_posts():
            cntr += 1
            try:
                post_data = [post[key] for key in POST_COLUMNS]
            except KeyError:
                pass
            else:
                if not post["merchant"] and self.ignore_merchant:
                    yield post_data + [url, tag]
                elif not post["merchant"]:
                    yield post_data + [url, tag]
                print(tag, post['id'])


class Yad2SearchNewPosts(Yad2Search):
    def __init__(self, ignore_merchant=False, days=7, save_result=True, test_mode=False) -> None:
        self._read_tagged_urls()
        if not test_mode:
            super().__init__(self.urls, ignore_merchant)
        try:
            self.stored_posts = pd.read_csv(STORED_POSTS_CSV, index_col=False)
        except FileNotFoundError:
            self.stored_posts = pd.DataFrame(columns=POST_DF_COLUMNS)
        if list(self.stored_posts.columns) != POST_DF_COLUMNS:
            self.stored_posts = pd.DataFrame(columns=POST_DF_COLUMNS)
        self.days = days
        self.save_result = save_result

    def start(self):
        self._load_new_posts()
        self._split_newposts_by_tag()

    def _read_urls(self):
        try:
            with open(URLS_FILE, 'r') as f:
                self.urls = [url.replace('\n', '') for url in f.readlines()]
        except FileNotFoundError:
            self.urls = []
        else:
            self.urls = [url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/') for url in self.urls]

    def _read_tagged_urls(self):
        try:
            with open(URLS_FILE, 'r', encoding='utf-8') as f:
                tagged_urls = [line.split(', ') for line in f.read().split('\n') if line]
                self.urls = [(urlmod.url_to_api_link(url), tag) for (url, tag) in tagged_urls]
        except FileNotFoundError:
            self.urls = []

    def _load_new_posts(self):
        posts = pd.DataFrame(list(self._iter_filtered_posts()), columns=POST_DF_COLUMNS)
        if self.days and self.days > 0:
            posts = self.get_last_n_day_posts(posts, self.days, 'date')
        print('\nAFTER filtering:', posts, sep='\n\n')
        if not self.stored_posts.empty:
            self.new_posts = pd.concat([self.stored_posts, posts]).drop_duplicates(subset=ID_COLUMN, keep=False)
            self.stored_posts = pd.concat([self.stored_posts, self.new_posts])
        else:
            self.stored_posts = posts
            self.new_posts = posts
        if self.save_result:
            self.stored_posts.to_csv(STORED_POSTS_CSV, index=False)
            self.new_posts.to_csv(NEW_POSTS_CSV, index=False)
        if not self.new_posts.empty:
            self.new_posts['price_numeric'] = self.new_posts['price'].str.replace('[^\d.]', '', regex=True).replace('', '0').astype(float)
            self.new_posts = self.new_posts.sort_values(by='price_numeric', ascending=False)
            print('\nBEFORE filtering:', posts, sep='\n\n')
            print('\nNEW posts:', self.new_posts, sep='\n\n')
            self.new_posts_count = len(self.new_posts.index)

    def _split_newposts_by_tag(self):
        self.new_tagged_posts = [(tag, grouped_df) for tag, grouped_df in self.new_posts.groupby('tag')]

        

    @staticmethod
    def get_last_n_day_posts(df, days, date_column):
        df[date_column] = pd.to_datetime(df[date_column])
        date_in_past = datetime.now().date() - timedelta(days=days)
        df_last_n_days = df[df[date_column].dt.date >= date_in_past]
        return df_last_n_days


if __name__ == "__main__":
    y2_srch = Yad2SearchNewPosts(ignore_merchant=True, days=17)
    y2_srch._load_new_posts()
