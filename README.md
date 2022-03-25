# media_management_bot

![workflow](https://github.com/cianoid/media_management_bot/actions/workflows/bot_workflow.yml/badge.svg)
[![Linux](https://svgshare.com/i/Zhy.svg)](https://svgshare.com/i/Zhy.svg)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)

[//]: # ([![GitHub branches]&#40;https://badgen.net/github/branches/Naereen/Strapdown.js&#41;]&#40;https://github.com/Naereen/Strapdown.js/&#41;)
[![Docker](https://badgen.net/badge/icon/docker?icon=docker&label)](https://https://docker.com/)

# Changelog

## build20220325

Команда /moderator_add позволяет добавить модератора по юзернейму

# Запуск бота

## Запуск в dev-режиме

### Создать файл app/.env

Для формирования списка из переменных *ADMIN_IDS* параметры указывать через пробел 

```
TELEGRAM_TOKEN=
ADMIN_IDS=
LOG_LEVEL=INFO
```

### Запуск в virtual environment

```
python3 -m venv venv
source/bin/activate
pip install -r requirements.txt
cd app
python mbot.py
```

### Или запуск в контейнере

```
cd infra
docker-compose up -d --build
```

### Остановка контейнера

```
docker-compose stop
```


# Автоматический запуск бота на сервере в Docker

## Подготовить Secrets

### Учетные данные Docker

```DOCKER_USERNAME``` - логин на Docker Hub

```DOCKER_PASSWORD``` - пароль на Docker Hub

### Учетные данные сервера, где будет запускаться бот

```SSH_HOST``` - адрес сервера, где будет жить бот

```SSH_USER``` - имя юзера сервера SSH_HOST

```SSH_KEY``` - приватный ключ юзера сервера SSH_HOST


### Данные Telegram-бота для уведомлений о ходе bot_workflow

```TELEGRAM_TO``` - ID юзера в Telegram, кому юот пришлет уведомление (юзер должен написать боту первым)

```TELEGRAM_TOKEN``` - Токен бота, который пришлет уведомлений

### Данные, необходимые для работы бота

```ENV_TELEGRAM_TOKEN``` - Токен рабочаего бота

```ENV_ADMIN_IDS``` - ID админов 

```ENV_LOG_LEVEL``` - уровень логировнаия. По умолчанию INFO

## Docker на сервере

Установите docker и docker-compose на ваш сервер. У пользователя SSH_USER должны быть 
права для запуска docker-compose через sudo

## Deployment

При каждом push в ветку main будет запущен Github Action "bot workflow", который все сделает.

Либо можно запустить вручную

