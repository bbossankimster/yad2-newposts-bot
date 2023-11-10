import requests
from settings import PROXY_OPT

URLS_FILE = 'tests/urls.txt.test'
PROXIES = {'http': PROXY_OPT, 'https': PROXY_OPT}


def url_to_api_link(url):
    return url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/')


def read_tagged_urls():
    with open(URLS_FILE, 'r', encoding='utf-8-sig') as f:
        return [line.split(', ') for line in f.read().split('\n') if line]


def test_yad2_json():
    urls = [url_to_api_link(url[0]) for url in read_tagged_urls()]
    for url in urls:
        assert url.startswith('https://')
        print(url)
    resp = requests.get(urls[0], proxies=PROXIES)
    assert 'feed' in [*resp.json()]
    assert 'feed_items' in [*resp.json()['feed']]
    # json_keys = [
    #    'feed', 'filters', 'categoriesData', 'media', 'pagination', 'canonicalUrl',
    #    'seoFooterText', 'address', 'catTitle', 'title', 'left_column', 'yad1Listing', 'yad1Ads']
    # feed_keys =  ['cat_id', 'subcat_id', 'title_text', 'sort_values', 'feed_items', 
    #         'feed_imp', 'current_page', 'page_size', 'total_pages', 'total_items', 
    #         'favorites_userid', 'can_filter_results', 'search_params', 'isCached', 
    #         'server_number', 'cacheKey', 'media', 'footer', 'breadCrumbs', 'associated_links',
    #         'nhood_king_package', 'header_text', 'seo_follow', 'seo_index', 'canonical',
    #         'meta_title', 'seo_text', 'left_column', 'hot_pics']
