import asyncio
import json
import time

import aiormq
from aiormq.abc import DeliveredMessage


# Callback-функция, вызываемая на каждое сообщение для консьюмера
async def on_message(message: DeliveredMessage):
    # Декодируем и десериализуем сообщение
    body: dict = json.loads(message.body.decode('utf-8'))

    print(f"Сообщение {body.get('counter')} получено")
    print(f"{body.get('text')} {body.get('counter')}")

    # Имитируем выполнение тяжелой CPU-bound задачи
    time.sleep(body.get('delay'))

    # Явно подтверждаем получение и обработку сообщения
    await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)
    print(f"Сообщение {body.get('counter')} обработано")


async def main():
    # Подключаемся к RabbitMQ
    connection = await aiormq.connect("amqp://pavel:123@localhost/")

    # Создаем канал
    channel = await connection.channel()

    # Объявляем точку обмена (создается, если не существует)
    await channel.exchange_declare("test_exchange", exchange_type="direct")

    # Объявляем очередь (создается, если не существует)
    declare_ok = await channel.queue_declare('test_queue')

    # Привязываем очередь к точке обмена
    await channel.queue_bind(
        queue=declare_ok.queue,
        exchange="test_exchange",
        routing_key="test_routing_key"
    )

    # Определяем количество сообщений, которое консьюмер может получить за один раз
    await channel.basic_qos(prefetch_count=1)

    # Настраиваем прослушивание очереди
    await channel.basic_consume(declare_ok.queue, on_message, no_ack=False)

    # Создаем бесконечный цикл для ожидания сообщений для консьюмера из очереди
    await asyncio.Future()


asyncio.run(main())