import requests
import utils.url_mods as urlmod
import pandas as pd
from datetime import datetime, timedelta
from settings import PROXY_OPT
import hashlib


PROXIES = {
    'http': PROXY_OPT, 'https': PROXY_OPT
    }
# ID column can be changed
POST_COLUMNS = [
    'id', "title_1", "price", "Rooms",
    "city", "date_added", "date", "contact_name"
    ]
POST_DF_COLUMNS = POST_COLUMNS + ['url', 'tag', 'changed_price_txt']
STORED_POSTS_CSV = 'data/stored_posts.csv'
NEW_POSTS_CSV = 'data/new_posts.csv'
URLS_FILE = 'data/urls.txt'


class Yad2Search:
    def __init__(self, urls, ignore_merchant=False) -> None:
        self.errors = []
        self.urls = urls
        self.ignore_merchant = ignore_merchant

    def _iter_posts(self):
        cntr = 0
        for url, tag in self.urls:
            page = 1
            pages = 1
            while page <= pages:
                print("\n***** TAG {}, URL {} (page #{} from {})".format(tag, url, page, pages))
                cntr += 1
                try:
                    resp = requests.get(url+'&page={}'.format(page), proxies=PROXIES)
                    assert resp.status_code == 200
                except Exception as e:
                    print("Exception...", e)
                    self.errors.append(tag)
                else:
                    page += 1
                    pages = resp.json()["feed"]["total_pages"]
                    for post in resp.json()["feed"]["feed_items"]:
                        yield url, tag, post

    def _iter_filtered_posts(self):
        cntr = 0
        for url, tag, post in self._iter_posts():
            cntr += 1
            try:
                post_data = [post[key] for key in POST_COLUMNS]
            except KeyError:
                pass
            else:
                #
                if not post["merchant"] and self.ignore_merchant:
                    yield post_data + [url, tag, '']
                    # print("no_merchant (ignore_merchant=True)", tag, post['id'])
                elif not post["merchant"]:
                    # print("no_merchant (ignore_merchant=False)", tag, post['id'])
                    yield post_data + [url, tag, '']


class Yad2SearchNewPosts(Yad2Search):
    def __init__(self, ignore_merchant=False, days=7, save_result=True, test_mode=False) -> None:
        self._read_tagged_urls()
        if not test_mode:
            super().__init__(self.urls, ignore_merchant)
        try:
            self.stored_posts = pd.read_csv(STORED_POSTS_CSV, index_col='hash')
        except FileNotFoundError:
            print('Can not open {}'.format(STORED_POSTS_CSV))
            self.stored_posts = pd.DataFrame(columns=POST_DF_COLUMNS)
        print('Stored posts count:', len(self.stored_posts))
        last_row = self.stored_posts.iloc[[-1]]
        date_added = last_row['date_added'].values
        hash_value = last_row.index[0]
        print('Last post date/hash is {}/{}'.format(date_added, hash_value))
        if list(self.stored_posts.columns) != POST_DF_COLUMNS:
            print('from file:', list(self.stored_posts.columns))
            print('from vars:', POST_DF_COLUMNS)
            err = 'Incorrect columns in {} found!'.format(STORED_POSTS_CSV)
            raise ValueError(err)
        self.days = days
        self.save_result = save_result
        self.new_tagged_posts = []
        self.new_posts_count = 0

    def start(self):
        posts_df = self._start_posts_parsing()
        new_posts = self._get_new_posts(posts_df)
        changed_price_posts = self._get_changed_price_only(posts_df)
        #self.stored_posts = pd.concat([self.stored_posts, self.new_posts])
        #self.stored_posts = self.stored_posts.sort_values(by=DATE_COL)
        if self.new_posts_count:
            self.new_tagged_posts = [(tag, grouped_df) for tag, grouped_df in self.new_posts.groupby('tag')]

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
            with open(URLS_FILE, 'r', encoding='utf-8-sig') as f:
                tagged_urls = [line.split(', ') for line in f.read().split('\n') if line]
                self.urls = [(urlmod.url_to_api_link(url), tag) for (url, tag) in tagged_urls]
                self.tags = [tag for (_, tag) in self.urls]
        except FileNotFoundError:
            self.urls = []

    def _start_posts_parsing(self):
        print('Parsing yad2 started!')
        posts_raw = list(self._iter_filtered_posts())
        posts_df = pd.DataFrame(posts_raw, columns=POST_DF_COLUMNS)
        posts_df['hash'] = posts_df.apply(lambda x: hashlib.md5((x['tag'] + x['city'] + x['title_1'] + x['contact_name']).encode()).hexdigest(), axis=1)
        posts_df['price'] = posts_df['price'].str.replace('[^\d.]', '', regex=True).replace('', '0').astype(int)
        posts_df = posts_df.set_index('hash')
        print([*posts_df.columns])
        print('Parsing yad2 finished! Found {} posts!'.format(len(posts_df.index)))
        return posts_df

    def _get_new_posts(self, posts_df):
        new_records = posts_df[~posts_df.index.isin(self.stored_posts.index)]
        if not new_records.empty:
            DATE_COL = 'date_added'
            new_records[DATE_COL] = pd.to_datetime(new_records[DATE_COL])
            date_in_past = datetime.now().date() - timedelta(days=60)
            new_records = new_records[new_records[DATE_COL].dt.date >= date_in_past]
            print('Found {} new posts!'.format(len(new_records)))
            print(new_records[['id', 'date_added','price', 'changed_price_txt']])
        return new_records

    def _get_changed_price_only(self, posts=None):
        print('Trying to find posts with changed price!')
        merged_df = pd.merge(posts, self.stored_posts, on='hash', suffixes=('_df1', '_df2'))
        print('Обьединенная таблица с обьявлениями из yad2 и сохраненными:')
        print(merged_df[['id_df1', 'price_df1', 'id_df2','price_df2']])
        return None

    def _save_posts(self):
        self.stored_posts.to_csv(STORED_POSTS_CSV, index=False)
        self.new_posts = self.new_posts.sort_values(by='price', ascending=False)
        self.new_posts.to_csv(NEW_POSTS_CSV, index=False)

    def _split_newposts_by_tag(self):
        self.new_tagged_posts = [(tag, grouped_df) for tag, grouped_df in self.new_posts.groupby('tag')]
