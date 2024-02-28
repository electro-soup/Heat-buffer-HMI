from influxdb import InfluxDBClient
import private
import pickle
client = InfluxDBClient(host = private.db_ip, port = 8086, database = 'nymea')

heat_buffer_temperature_ids = {}

heat_buffer_temperature_ids['temp0'] = 'c6f0aa6a-728a-401e-ab9e-96d4de305179'
heat_buffer_temperature_ids['temp1'] = '698556ca-99dd-455d-8412-546a971a683a'
heat_buffer_temperature_ids['temp2'] = 'aae699cb-e109-48fc-a370-ef681980a1f5'
heat_buffer_temperature_ids['temp3'] = 'aae699cb-e109-48fc-a370-ef681980a1f5'
heat_buffer_temperature_ids['temp4'] = '35daf33b-8004-4eb2-bea9-8406c01ffdc0'
heat_buffer_temperature_ids['temp5'] = 'c19fde1d-fae0-4baf-856f-7d70b369cd64'
heat_buffer_temperature_ids['temp6'] = '817bb84e-e440-4d99-8755-43606ac6cb83'
heat_buffer_temperature_ids['temp7'] = 'fe59a2c0-cc2f-4ea6-aaa5-e7a3cc308814'
heat_buffer_temperature_ids['temp8'] = '3637d208-64dd-453b-8f18-c7338f9ee86d'

result = client.get_list_measurements()
start_time = '2024-01-01T00:00:00Z'
end_time = '2024-01-02T00:00:00Z'


all_data = {}

for temp_sensor, nymea_id in heat_buffer_temperature_ids.items():
    
    query = f'SELECT time, MEAN(temperature) FROM minutes."state-{{{nymea_id}}}-temperature" WHERE time > now() - 200d  GROUP BY time(10m) fill(previous)  ORDER BY time ASC'
    result = client.query(query)
    lol = []

    for table in result:
        lol = table

    print(lol)
    #for dict in lol:
       #print(dict)

    
    new_time_temperature_dict = {d['time']: d['mean'] for d in lol}

    for time, temperature in new_time_temperature_dict.items():
         if temperature is not None:
           if time in all_data:
              all_data[time].append(temperature)
           else:
              all_data[time] = [temperature]    
    

for time, temperature in all_data.items():
        print(time, temperature)

pickle.dump(all_data, open('nymea_minutes.dat', 'wb'))


client.close()