def url_to_api_link(url):
    return url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/')


def urls_to_api_path(urls):
    return [url.replace('yad2.co.il/', 'yad2.co.il/api/pre-load/getFeedIndex/') for url in urls]


def api_link_to_url(api_link):
    return api_link.replace('yad2.co.il/api/pre-load/getFeedIndex/', 'yad2.co.il/')
