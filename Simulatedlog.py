# import redis
# # Connect to Redis Client
# hostname = 'redis-16768.c232.us-east-1-2.ec2.cloud.redislabs.com'
# portnumber = 16768
# password = 'wSAaN3VjrVA9Uw3O8Agn0ktUv8csZccO'


# r = redis.StrictRedis(host=hostname,
#                       port=portnumber,
#                       password=password)
 
# # Simulated Logs
# with open('simulated_logs.txt', 'r') as f:
#     logs_text = f.read()
 
# encoded_logs = logs_text.split('\n')
 
# # Push into Redis database
# r.lpush('Attendance:logs', *encoded_logs)
