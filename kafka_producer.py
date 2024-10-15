from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_event():
    events = ['click', 'view_product', 'add_to_cart', 'purchase']
    return {
        'user_id': random.randint(1, 1000),
        'event_type': random.choice(events),
        'product_id': random.randint(100, 200),
        'timestamp': int(time.time())
    }

if __name__ == "__main__":
    while True:
        event = generate_event()
        producer.send('customer_activity', event)
        print(f"Produced event: {event}")
        time.sleep(1)
