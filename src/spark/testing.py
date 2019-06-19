from argparse import ArgumentParser

parser = ArgumentParser(description='Spark Streaming')
parser.add_argument('--broker', type=str, default='localhost:9092', help = 'List all kafka brokers')

broker = parser.parse_args()
broker = broker.broker

print(broker)
