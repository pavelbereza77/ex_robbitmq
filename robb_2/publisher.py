import asyncio
import aiormq
import random
import json


async def publish():
    # Подключаемся к RabbitMQ
    connection = await aiormq.connect("amqp://pavel:123@localhost/")

    # Создаем канал
    channel = await connection.channel()

    # Объявляем точку обмена (создается, если не существует)
    await channel.exchange_declare("test_exchange", exchange_type="direct")

    # Инициализируем переменную для счетчика сообщений
    counter = 1

    # Запускаем бесконечный цикл публикации сообщений в RabbitMQ
    while True:

        # Добавляем случайную задержку перед отправкой очередного сообщения
        await asyncio.sleep(random.randrange(1, 4))

        # Создаем словарь, из которого будет сформировано тело сообщения
        body = {
            'delay': 1 if not counter % 2 else 5,
            'text': 'Привет из RabbitMQ №',
            'counter': counter
        }

        # Отправляем сообщение в exchange
        await channel.basic_publish(
            body=json.dumps(body).encode('utf-8'),
            exchange="test_exchange",
            routing_key="test_routing_key"
        )

        # Выводим информационное сообщение в консоль
        print(f'Сообщение № {counter} опубликовано!')

        # Увеличиваем счетчик сообщений
        counter += 1


asyncio.run(publish())