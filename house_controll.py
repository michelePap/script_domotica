# -*- coding: utf-8 -*- 
#!/usr/bin/python
import tgl
import os
import glob
import time
from functools import partial

# sensore temperatura
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
device_file = '/sys/bus/w1/devices/28-00043d1512ff/w1_slave'

# variabili Telegram client
our_id = 0
binlog_done = False;

# legge il file con l'output del sensore di temperatura
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

# calcola la temperatura
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
        
def on_binlog_replay_end():
    binlog_done = True;

def on_get_difference_end():
    pass

def on_our_id(id):
    our_id = id
    return "Set ID: " + str(our_id)

def msg_cb(success, msg):
	pass

HISTORY_QUERY_SIZE = 100

# cronologia ultimi messaggi
def history_cb(msg_list, peer, success, msgs):
  print(len(msgs))
  msg_list.extend(msgs)
  print(len(msg_list))
  if len(msgs) == HISTORY_QUERY_SIZE:
    tgl.get_history(peer, len(msg_list), HISTORY_QUERY_SIZE, partial(history_cb, msg_list, peer));

def cb(success):
    print(success)

# risponde ai messaggi ricevuti
def on_msg_receive(msg):
    if msg.out and not binlog_done:
      return;

    if msg.dest.id == our_id: # direct message
      peer = msg.src
    else: # chatroom
      peer = msg.dest

    if msg.text.startswith("Help"):
        peer.send_text("/home/pi/tg/help_msg.txt")

    elif msg.text.startswith("Ping"):
      peer.send_msg("PONG!")

    elif msg.text.startswith("Foto"):
    	os.system("fswebcam -r 640x480 /home/pi/tg/img.jpg")
    	peer.send_photo('/home/pi/tg/img.jpg')
    	
    elif msg.text.startswith("Meteo"):
    	os.system("/home/pi/tg/meteo.sh")
    	peer.send_text("/home/pi/tg/bari.txt")
    	
    elif msg.text.startswith("Temperatura"):
    	temp = str(read_temp())
    	peer.send_msg("--- " + temp + ' C°')

    elif msg.text.startswith("Avviso temperatura"):
        while True:
            temperatura = float(read_temp())
            if temperatura > 24:
                break;
        peer.send_msg("--- Temperatura elevata: " + str(read_temp()) + " C°")

    elif msg.text.startswith("Avviso movimento"):
        os.system("sudo python /home/pi/tg/pir_alert.py")
        peer.send_msg("--- Movimento rilevato, invio foto...")
        peer.send_photo("/home/pi/tg/alert.jpg")

    else:
        peer.send_msg("--- Comando non riconosciuto")
        
def on_secret_chat_update(peer, types):
    return "on_secret_chat_update"

def on_user_update(peer, what_changed):
    pass

def on_chat_update(peer, what_changed):
    pass

# Set callbacks
tgl.set_on_binlog_replay_end(on_binlog_replay_end)
tgl.set_on_get_difference_end(on_get_difference_end)
tgl.set_on_our_id(on_our_id)
tgl.set_on_msg_receive(on_msg_receive)
tgl.set_on_secret_chat_update(on_secret_chat_update)
tgl.set_on_user_update(on_user_update)
tgl.set_on_chat_update(on_chat_update)

