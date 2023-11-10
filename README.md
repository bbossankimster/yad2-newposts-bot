#
#### [English](#English) / [Russian](#Russian)

# Yad2 new posts search bot


<a name="English"></a> 

## Introduction
This is a Telegram bot for adverising about new posts on yad2.co.il


## Getting started

Clone repositary, activate env (if you want) and install requirements:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/bbossankimster/yad2-newposts-bot.git
cd yad2-newposts-bot
python -m venv env
env\Scripts\activate.ps1
pip install -r requirements.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


## Basic usage

Run bot.py:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cd src
env\Scripts\activate.ps1
python bot.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



<a name="Russian"></a> 

# Yad2 new posts search bot


## Описание
Телеграм бот для поиска новых обьявлений на сайте yad2.co.il
и отправки уведомлений в чат


## Начальная установка и настройка

1. Склонируйте репозитарий, установите виртуальное окружени и пакеты из requirements.txt

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
git clone https://github.com/bbossankimster/yad2-newposts-bot.git
cd yad2-newposts-bot
python -m venv env
env\Scripts\activate.ps1
pip install -r requirements.txt
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

2. Скопируйте settings_example.py в settings.py
Раскоментируйте все переменные и установите свои значения для:
- API_KEY бота
- ID админа бота
- ID разрешенных пользователей
- ID чата в который будут отправляться уведомления о новых обьявлениях
- строка с логином, паролем, хостом и портом для подключения к прокси

## Запуск приложения

Запустите bot.py:

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
cd src
env\Scripts\activate.ps1
python bot.py
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
