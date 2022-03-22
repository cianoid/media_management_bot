# media_management_bot

![workflow](https://github.com/cianoid/media_management_bot/actions/workflows/bot_workflow.yml/badge.svg)


#### .env

Для формирования списка из переменных *ADMIN_IDS* параметры указывать через пробел 

```
TELEGRAM_TOKEN=
ADMIN_IDS=
LOG_LEVEL=INFO
```


#### Запуск в тестовом режиме

```
python3 -m venv venv
source/bin/activate
pip install -r requirements.txt
cd app
python mbot.py
```

#### Запуск в контейнере
```
cd app
docker container rm mbot
docker build --no-cache -t mbot .
docker run --name mbot -d mbot 
```

#### Остановка контейнера
```
docker container stop mbot
```