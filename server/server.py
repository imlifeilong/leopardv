import redis

ROLE='MASTER'
rc = redis.StrictRedis(host='106.12.216.74', port='6379', db=3, password='tongna888')
ps = rc.publish('test', '上线')



