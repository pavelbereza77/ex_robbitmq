import asyncio
import json
from datetime import datetime, timedelta, timezone

import aiormq


async def publish_message():
    # Подключаемся к RabbitMQ
    connection = await aiormq.connect('amqp://pavel@:1234@localhost/')

    # Создаем канал
    channel = await connection.channel()

    # Объявляем точку обмена (создается, если не существует)
    await channel.exchange_declare('main_exchange', exchange_type='direct')

    # Определяем время, когда сообщение должно быть обработано
    scheduled_time = (datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat()

    # Создаем словарь, из которого будет сформировано тело сообщения
    body = {
        'text': 'Hello is RabbitMQ!',
    }

    # Отправляем сообщение в `main_exchange`
    await channel.basic_publish(
        body=json.dumps(body).encode('utf-8'),
        exchange='main_exchange',
        routing_key='main_routing_key',
        properties=aiormq.spec.Basic.Properties(
            headers={
                'scheduled_time': scheduled_time
            }
        )
    )

    print(f'Published message with scheduled time: {scheduled_time}')

    # Закрываем соединение
    await connection.close()


asyncio.run(publish_message())