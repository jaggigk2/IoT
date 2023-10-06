import paho.mqtt.client as mqttClient
import time

all_clients_location = {}


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("server connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
    else:
        print("Connection failed")


def game_on(player, locPow):
    if locPow[0] == -1:
        return

    locX = int(locPow[0])
    locY = int(locPow[1])
    pow1 = int(locPow[2])
    killed_by = ""
    winner = ""
    dead = ""

    for key, value in all_clients_location.items():
        if value[2] == -1:
            return
        if key == player:
            continue
        else:
            valX = int(value[0])
            valY = int(value[1])
            pow2 = int(value[2])

            diffX = abs(valX - locX)
            diffY = abs(valY - locY)

            if pow1 == pow2:
                continue
            elif pow1 == 0 and pow2 == 1:
                if diffX <= 1 and diffY <= 1:
                    killed_by = key
                    dead = player
                    print(dead + " was killed by " + killed_by)
                    break
            elif pow1 == 1 and pow2 == 0:
                if diffX <= 1 and diffY <= 1:
                    killed_by = player
                    dead = key
                    print(dead + " was killed by " + killed_by)
                    break

    if len(killed_by) == 0:
        return
    else:
        del all_clients_location[dead]
        client_main.unsubscribe(dead)
        if len(all_clients_location) == 1:
            winner = list(all_clients_location.keys())[0]
            print("WINNER is " + winner)
        else:
            return


def on_message(client, userdata, message):
    pl_temp = str(message.payload)
    pl = pl_temp[2:-1]
    topic = str(message.topic)
    pl_arr = pl.split()

    if len(pl_arr) == 0:
        return
    # return
    if len(pl_arr) > 1:
        #print(topic + " makes a move to " + pl)
        all_clients_location[topic] = pl_arr
        game_on(topic, pl_arr)
    else:
        for i in range(1, int(pl_arr[0])):
            subb = "player-" + str(i+1)
            client_main.loop_start()
            client_main.subscribe(subb)

        all_clients_location[topic] = [-1, -1, -1]


broker_address = "127.0.0.1"  # Broker address
port = 1883  # Broker port
user = "admin"  # Connection username
password = "hivemq"  # Connection password

Connected = False

client_name = "server"
client_main = mqttClient.Client(client_name)  # create new instance
client_main.on_connect = on_connect  # attach function to callback
client_main.on_message = on_message  # attach function to callback
client_main.connect(broker_address, port=port)  # connect to broker

client_main.loop_start()  # start the loop
client_main.subscribe("player-1")
# client_main.subscribe("player-2")
while not Connected:  # Wait for connection
    time.sleep(0.1)
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("exiting")
    client_main.disconnect()
    client_main.loop_stop()
