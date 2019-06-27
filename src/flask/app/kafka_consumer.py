from kafka import KafkaConsumer, TopicPartition

# settings
client = "localhost:9092"
topic = 'crashed-devices'

# prepare consumer
lastOffset=-1
# tp = TopicPartition(topic,0)
consumer = KafkaConsumer('sensor-data-1', bootstrap_servers=['ec2-52-203-135-135.compute-1.amazonaws.com:9092',
                        'ec2-52-70-111-222.compute-1.amazonaws.com:9092', 'ec2-34-193-78-218.compute-1.amazonaws.com:9092'],
						enable_auto_commit=True, group_id='my-group',
						auto_offset_reset = 'earliest')
# obtain the last offset value
# lastOffset = consumer.end_offsets([tp])[tp]

for message in consumer:
    # print ("Offset:", message.offset)
    # print ("lastOffset", lastOffset)
    print(message.value)
    # if message.offset == lastOffset-1:
    #     consumer.commit()
    #     break
