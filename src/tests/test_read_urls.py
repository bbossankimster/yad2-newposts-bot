from core.yad2_search_executor import Yad2SearchNewPosts


URLS_FILE = 'tests/urls.txt.test'


def read_urls():
    with open(URLS_FILE, 'r') as f:
        return [line for line in f.read().split('\n') if line]


def read_tagged_urls():
    with open(URLS_FILE, 'r', encoding='utf-8-sig') as f:
        return [line.split(', ') for line in f.read().split('\n') if line]


def test_read_urls():
    urls = read_urls()
    assert len(urls) == 5
    assert urls[0].endswith('\n') is False


def test_tagged_urls():
    urls = read_tagged_urls()
    assert len(urls) == 5
    assert urls[0][0].endswith('\n') is False
    assert urls[0][1] == 'Яд_Элияху_до_2ком'


def test_yad2_urls():
    y2_search = Yad2SearchNewPosts(test_mode=True)
    urls = y2_search.urls
    assert len(urls) == 5
    assert urls[0][0].endswith('\n') is False
    assert urls[0][1] == 'Яд_Элияху_до_2ком'