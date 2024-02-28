# Activity Tracker
#
# Keeps track of the amount of time spent on targeted processes. Updates every 1 minute.
#
# Created by Dax McPartland

import subprocess
import time
import json
import mysql.connector
import datetime

# shamlessly stolen from stack overflow
def process_exists(process_name):
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    output = subprocess.check_output(call).decode()
    last_line = output.strip().split('\r\n')[-1]
    return last_line.lower().startswith(process_name.lower())

# open json config file
json_stuff = json.load(open('config' +'.json'))
process_list = json_stuff['processes']
db_config = json_stuff['db_config']

# this is waiting a minute for mysql to startup first
time.sleep(60)

# connect to mysql server
cnx = mysql.connector.connect(**db_config)
cursor = cnx.cursor()

while(True):
    time.sleep(60)
    
    for process in process_list:
        if process_exists(process + ".exe"):

            # read the amount of time already logged
            cursor.execute("SELECT time_logged, id FROM processes WHERE name= %s ORDER BY id DESC LIMIT 1;", (process,))
            row = cursor.fetchall()
 
            if row:
                # update the db with new time 
                time_log, id = row[0]
                hours = (time_log.seconds / 3600) + (time_log.days * 24) 
                
                if hours >= 838:
                    cursor.execute("INSERT INTO processes (name, time_logged) values (%s, %s);", (process, datetime.timedelta(minutes=0)))
                else:
                    new_time = time_log + datetime.timedelta(minutes=1)
                    cursor.execute("UPDATE processes SET time_logged= %s WHERE id= %s;", (new_time, id))
            else:
                # insert process into db
                cursor.execute("INSERT INTO processes (name, time_logged) values (%s, %s);", (process, datetime.timedelta(minutes=0)))
        
    cnx.commit()
cnx.close()
cursor.close()

