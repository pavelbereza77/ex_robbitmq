import asyncio

import aiormq
from aiormq.abc import DeliveredMessage


# Callback-функция, вызываемая на каждое сообщение для консьюмера
async def on_message(message: DeliveredMessage):
    print(message.body.decode())

    # Явное подтверждение получения и обработки сообщения
    await message.channel.basic_ack(delivery_tag=message.delivery.delivery_tag)


async def main():
    # Подключение к RabbitMQ
    connection = await aiormq.connect("amqp://pavel:123@localhost/")

    # Создание канала
    channel = await connection.channel()

    # Объявление точки обмена (создается, если не существует)
    await channel.exchange_declare("test_exchange", exchange_type="direct")

    # Объявление очереди (создается, если не существует)
    declare_ok = await channel.queue_declare('test_queue')

    # Привязка очереди к точке обмена
    await channel.queue_bind(
        queue=declare_ok.queue,
        exchange="test_exchange",
        routing_key="test_routing_key"
    )

    # Определение количества сообщений, которые консьюмер может получить за один раз
    await channel.basic_qos(prefetch_count=1)

    # Настройка прослушивания очереди
    await channel.basic_consume(declare_ok.queue, on_message, no_ack=False)

    # Создание бесконечного цикла для ожидания сообщений для консьюмера из очереди
    await asyncio.Future()


asyncio.run(main())