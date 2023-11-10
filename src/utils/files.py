def read_urls(file):
    try:
        with open(file, 'r') as f:
            urls = [url.replace('\n', '') for url in f.readlines()]
    except FileNotFoundError:
        return []
    else:
        return [url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/') for url in urls]


def add_urls(urls_txt, file):
    urls = [url for url in urls_txt.split('\n') if url.startswith('https://www.yad2.co.il')]
    try:
        with open(file, 'a') as f:
            urls = [url.replace('\n', '') for url in f.readlines()]
    except FileNotFoundError:
        return []
    else:
        return [url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/') for url in urls]