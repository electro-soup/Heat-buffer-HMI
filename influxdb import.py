from influxdb import InfluxDBClient

client = InfluxDBClient(host = '', port = 8086, database = 'nymea')

result = client.get_list_measurements()
start_time = '2024-01-01T00:00:00Z'
end_time = '2024-01-02T00:00:00Z'
query = 'SELECT time, temperature::integer FROM hours."state-{06393f8a-7e38-439c-818d-b9300278b3ce}-temperature" WHERE time > now() - 10d  ORDER BY time ASC'




result = client.query(query)

lol = []

for table in result:
    lol = table

print(lol)
for dict in lol:
    print(dict)



client.close()