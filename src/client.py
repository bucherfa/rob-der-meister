#!/usr/bin/python3
import json
import select
import socket
import sys

from RBGctrl import RGBctrl
from Engine import Engine

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.setblocking(1)
client.connect(('spikeone.goip.de', 3665))

client.send(('{"currentPosition":{"x":1,"y":1.0,"z":1.1,"o":1.1,"floor":1},"robotName":"Rob","macAddress":"MM:MM:MM:SS:SS:SS"}').encode())
# client.send(('{"currentPosition":{"x":1.1,"y":1.1,"z":1.1,"o":1.1,"floor":1},"robotName":"Rob","macAddress":"MM:MM:MM:SS:SS:SS"}').encode())

print("connected...")

RGBCtrl_1 = RGBctrl()
RGBCtrl_1.setup()
engine = Engine()
engine.setup()


def color_light(command):
    side = command["side"]
    r = command["color"]["R"]
    g = command["color"]["G"]
    b = command["color"]["B"]
    if side == 0:
        RGBCtrl_1.set_left_color(r, g, b)
        RGBCtrl_1.set_right_color(r, g, b)
    elif side == 1:
        RGBCtrl_1.set_left_color(r, g, b)
    elif side == 2:
        RGBCtrl_1.set_right_color(r, g, b)
    else:
        print("invalid side: " + str(side))


def color_off(command):
    side = command["side"]
    if side == 0:
        RGBCtrl_1.set_left_off()
        RGBCtrl_1.set_right_off()
    elif side == 1:
        RGBCtrl_1.set_left_off()
    elif side == 2:
        RGBCtrl_1.set_right_off()
    else:
        print("invalid side: " + str(side))


def engine_command(command):
    direction = command["direction"]
    if direction == 1:
        engine.motorForward(100)
    elif direction == 0:
        engine.motorStop()
    elif direction == 2:
        engine.motorBackward(100)
    # engine.move(100, 'forward', 1, None)
    # {'angle': 0, 'direction': 1, 'type': 5}


commands: dict = {1: color_off, 2: color_light, 5: engine_command}

try:
    while True:

        # maintains a list of possible input streams
        sockets_list = [sys.stdin, client]

        """ There are two possible input situations. Either the
        user wants to give manual input to send to other people,
        or the server is sending a message to be printed on the
        screen. Select returns from sockets_list, the stream that
        is reader for input. So for example, if the server wants
        to send a message, then the if condition will hold true
        below.If the user wants to send a message, the else
        condition will evaluate as true"""
        read_sockets, write_socket, error_socket = select.select(sockets_list, [], [])

        for socks in read_sockets:
            if socks == client:
                message = socks.recv(2048)
                command = message.decode()
                command_dict = json.loads(command)
                print(command_dict)
                dict_key = command_dict["type"]
                if dict_key in commands:
                    commands[dict_key](command_dict)
                else:
                    print("Unknown command: " + str(dict_key))
                    # client.send('{"error":"unknown_type"}'.encode())
            else:
                message = sys.stdin.readline()
                client.send(message.encode())
                sys.stdout.write("<You>")
                sys.stdout.write(message)
                sys.stdout.flush()
except ConnectionResetError or KeyboardInterrupt:
    print('cleaning up...')
    client.close()
    RGBCtrl_1.destroy()
