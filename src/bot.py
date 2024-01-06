
import os
import sys

from numpy import hypot
from settings import API_KEY, YAD2_POSTS_CHAT, REPEAT_MINUTES, ADMIN
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from utils.auth import restricted
from utils.url_mods import urls_to_api_path
from utils.files import read_urls
from utils.messages import iter_msg_chunks_by_tag
from core.yad2_search_executor import Yad2SearchNewPosts
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

START_TEXT = """\
/start - Вывести стартовое сообщение от бота
/start_search - Запустить поиск новых обьявлений

/start_search_loop - Добавить задание на периодический поиск
/delete_search_loop - Удалить задание на периодический поиск

/add_urls - Добавить/заменить список URL
/show_urls - Показать список URL
"""
NOT_FOUND_TEXT = 'Новых обьявлений нет!'

YAD2_POST_URL = 'https://www.yad2.co.il/item/{}'
URLS_FILE = 'data/urls.txt'

logging.basicConfig(
    handlers=[logging.FileHandler(os.path.join(BASE_DIR, "bot.log"), 'a', 'utf-8')],
    format='%(asctime)s %(message)s',
    # datefmt='%m-%d %H:%M',
    level=logging.INFO #CRITICAL ERROR WARNING  INFO    DEBUG    NOTSET 
)


def main():
    mybot = Updater(API_KEY, use_context=True)
    dp = mybot.dispatcher
    dp.bot_data['urls'] = read_urls(URLS_FILE)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("start_search", start_search))
    dp.add_handler(CommandHandler("start_search_loop", start_search_loop))
    dp.add_handler(CommandHandler("delete_search_loop", delete_search_loop))
    dp.add_handler(CommandHandler("add_urls", add_urls))
    dp.add_handler(CommandHandler("show_urls", show_urls))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    mybot.start_polling()
    mybot.idle()


@restricted
def start(update, context):
    print(context.bot_data)
    update.message.reply_text(START_TEXT)


@restricted
def start_search(update, context):
    y2_srch = Yad2SearchNewPosts(ignore_merchant=True, days=7, save_result=True)
    y2_srch.start()
    for msg_chunk in iter_msg_chunks_by_tag(y2_srch):
        update.message.reply_text(msg_chunk, disable_web_page_preview=True)
    if not y2_srch.new_tagged_posts:
        update.message.reply_text(NOT_FOUND_TEXT, disable_web_page_preview=True)


@restricted
def start_search_loop(update, context):
    jobs = context.job_queue.get_jobs_by_name('yad2_search_loop')
    if jobs:
        for job in jobs:
            job.schedule_removal()
    chat_id = update.message.chat_id
    time_delta = datetime.timedelta(minutes=REPEAT_MINUTES)
    context.job_queue.run_repeating(callback_search_loop, time_delta, first=1, context=[chat_id], name="yad2_search_loop")
    update.message.reply_text("Добавил поиск по расписанию (каждые {} минут)".format(REPEAT_MINUTES))

@restricted
def delete_search_loop(update, context):
    jobs = context.job_queue.get_jobs_by_name('yad2_search_loop')
    if jobs:
        for job in jobs:
            job.schedule_removal()
        update.message.reply_text('Удалил {} задачу поиска по расписанию'.format(len(jobs)))
    else:
        update.message.reply_text('Нет задач поиска по расписанию')


def callback_search_loop(context):
    chat_id = context.job.context[0]
    y2_srch = Yad2SearchNewPosts(ignore_merchant=True, days=7, save_result=True)
    y2_srch.start()
    if not y2_srch.new_tagged_posts:
        context.bot.send_message(chat_id=ADMIN, text=NOT_FOUND_TEXT, disable_web_page_preview=True)
    else:
        for msg_chunk in iter_msg_chunks_by_tag(y2_srch):
            context.bot.send_message(chat_id=YAD2_POSTS_CHAT, text=msg_chunk, disable_web_page_preview=True)

@restricted
def add_urls(update, context):
    msg = "\
    Введите URL, чтобы добавить к существующему списку.\n\
    Введите список URL, чтобы перезаписать весь список."
    update.message.reply_text(msg)
    context.user_data['urls_input'] = True


@restricted
def show_urls(update, context):
    with open(URLS_FILE, 'r', encoding='utf-8') as f:
        urls = f.read().split('\n')
        update.message.reply_text("URL адресов для поиска: {}\n\n{}".format(
            len(urls), "\n\n".join(urls)), disable_web_page_preview=True)


def handle_message(update, context):
    if context.user_data.get('urls_input'):
        urls = update.message.text.strip().split('\n')
        urls = [url for url in urls if url and url.startswith('https://www.yad2.co.il')]
        if len(urls) > 1:
            with open(URLS_FILE, 'w', encoding='utf-8') as f:
                f.write('\n'.join(urls))
            update.message.reply_text("Список URL перезаписан!")
            context.bot_data['urls'] = urls_to_api_path(urls)
        elif len(urls) == 1:
            with open(URLS_FILE, 'a', encoding='utf-8') as f:
                f.write('\n' + '\n'.join(urls))
            update.message.reply_text("URL добавлен в список!")
            context.bot_data['urls'] = context.bot_data['urls'] + urls_to_api_path(urls)
        else:
            update.message.reply_text(
                "Введите URL, который начинается с https://www.yad2.co.il", disable_web_page_preview=True)
        del context.user_data['urls_input']
    else:
        update.message.reply_text("Неизвестная команда.")


if __name__ == "__main__":
    main()
