import redis


ROLE='SLAVE'
rc = redis.StrictRedis(host='106.12.216.74', port='6379', db=3, password='tongna888')
ps = rc.pubsub()
ps.subscribe('test')  # 从liao订阅消息

result = ps.listen()

for res in result:
    if res['type'] == 'message':
        data = res['data'].decode()
        print('------------->', data)
