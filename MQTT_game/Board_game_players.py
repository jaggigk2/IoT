import time

import paho.mqtt.client as mqttClient
from tkinter import filedialog
from tkinter import *
import os

all_clients_l = []

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Player Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")

# read all the player files
root = Tk()
filez_l = root.filename = filedialog.askopenfilenames(parent=root, title="Choose as many files as Players",
                                                      filetypes=(("text files", "*.txt"), ("all files", "*.*")))
filez_l = root.tk.splitlist(filez_l)

# set broker settings
broker_address = "127.0.0.1"  # Broker address
port = 1883  # Broker port
user = "admin"  # Connection username
password = "hivemq"  # Connection password


all_file_contents = {}
all_file_linenum = {}
clients = {}
for filez in filez_l:
    with open(filez) as f:
        client_name = os.path.basename(f.name)[:-4]
        contents = f.read()
        all_file_contents[client_name] = contents.split('\n')
        all_clients_l.append(client_name)
        all_file_linenum[client_name] = -1

        Connected = False

        client = mqttClient.Client(client_name)  # create new instance
        client.on_connect = on_connect
        client.connect(broker_address, port=port)  # connect to broker
        client.loop_start()  # start the loop
        while Connected != True:  # Wait for connection
            time.sleep(0.1)

        clients[client_name] = client


all_clients_l.sort()

while True:
    for x in all_clients_l:
        try:
            clientX = clients[x]
            linenum = all_file_linenum[x] + 1
            all_file_linenum[x] = linenum
            if len(all_file_contents[x]) > linenum:
                line = all_file_contents[x][linenum]
                #print(x+"    "+line)
                clientX.publish(x, line)
                time.sleep(1)

        except KeyboardInterrupt:
            print("exiting")
            clientX.disconnect()
            clientX.loop_stop()
