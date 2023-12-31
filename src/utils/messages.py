import emoji
YAD2_POST_URL = 'https://www.yad2.co.il/item/{}'


def make_chunked_msgs(posts):
    msg_portions = {}
    msg_list = []
    split_size = 20
    url_cntr = 0
    for tag, grouped_post in posts:
        msg_list = ['#{}'.format(tag)]
        url_cntr += 1
        cntr = 0
        for indx, post in grouped_post.iterrows():
            cntr += 1
            if post['changed_price_txt']:
                price = '{} {} (было {})'.format(
                    post['price'], emoji.emojize(':green_circle:'), post['changed_price_txt'])
            else:
                price = post['price']
            txt = "{0} {1}\n{2} {3} {4} ({5})".format(
                str(cntr),
                YAD2_POST_URL.format(post['id']),
                post['city'],
                price,
                post['title_1'],
                post['date_added']
                )
            msg_list.append(txt)
        msg_portions[tag] = ["\n\n".join(msg_list[i:i+split_size]) for i in range(0, len(msg_list), split_size)]
    return msg_portions


def iter_msg_chunks_by_tag(tagged_posts, tags):
    txt_portions = make_chunked_msgs(tagged_posts)
    cntr = 0
    for tag in tags:
        cntr += 1
        if tag in txt_portions:
            for txt_portion in txt_portions[tag]:
                txt_portion = f'{cntr}) ' + txt_portion
                yield txt_portion
