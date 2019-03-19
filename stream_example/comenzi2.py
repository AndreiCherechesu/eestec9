import cv2, sys
import requests
import json
import time
import socketio

from utils import printTimeDiff, initTimeDiff
from client import startListening, curFrame, frameFragments

def example(frame):
    #TODO: do something with your frame
    
    #render frame to our screen
    cv2.imshow('client', frame)
    cv2.waitKey(1)

# sio = socketio.Client()
# sio.connect("http://10.81.176.105")

def sendCommand(url, body):
    global sio
    try:
        # print(body)
        resp = requests.post(url, json = body)
        print(resp.status_code)
        # resp = sio.emit(url, body)
        print(resp)
    except requests.ConnectionError as e:
        print(e)

url_admin = "http://10.81.176.105/admin"
url_config = "http://10.81.176.105/stream_config"
url_pselect = "http://10.81.176.105/player_select"
url_command = "http://10.81.176.105/command"

menu_down = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "down",
"is_player_2": False
}

menu_up = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "up",
"is_player_2": False
}

menu_left = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "left",
"is_player_2": False
}

menu_right = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "right",
"is_player_2": False
}

menu_enter = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "enter",
"is_player_2": False
}

menu_escape = {
"key": "nuicho9423hlcx80",
"type": "menu_command",
"menu_key": "escape",
"is_player_2": False
}

select_scorpio = {
"key": "2ptwedi1ddp0gow8",
"champion": "scorpio"
}

select_subzero = {
"key": "2ptwedi1ddp0gow8",
"champion": "subzero"
}

game_up = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "up": True
}
}

game_up_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "up": False
}
}

game_down = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "down": True
}
}

game_down_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "down": False
}
}

game_left = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "left": True
}
}

game_left_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "left": False
}
}

game_right = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "right": True
}
}

game_right_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "right": False
}
}

game_front_punch = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "front_punch": True
}
}

game_front_punch_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "front_punch": False
}
}

game_back_punch = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "back_punch": True
}
}
game_back_punch_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "back_punch": False
}
}

game_front_kick = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "front_kick": True
}
}
game_front_kick_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "front_kick": False
}
}

game_back_kick = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "back_kick": True
}
}
game_back_kick_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "back_kick": False
}
}

game_interact = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "interact": True
}
}
game_interact_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "interact": False
}
}

game_throw = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "throw": True
}
}
game_throw_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "throw": False
}
}


game_block = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "block": True
}
}
game_block_disable = {
"key": "2ptwedi1ddp0gow8",
"commands": {
    "block": False
}
}

shortcut_igtmm = {
  "key": "nuicho9423hlcx80",
  "type": "in_game_to_main_menu"
#   "hide_post_game_details": True
}

shortcut_2p = {
  "key": "nuicho9423hlcx80",
  "type": "new_2p_game"
#   "hide_post_game_details": True
}

shortcut_pselect = {
  "key": "nuicho9423hlcx80",
  "type": "start_player_select"
#   "hide_post_game_details": True
}

def escape():
    sendCommand(url_admin, menu_escape)
    time.sleep(0.3)
    sendCommand(url_admin, menu_up)
    time.sleep(0.3)
    sendCommand(url_admin, menu_up)
    time.sleep(0.3)
    sendCommand(url_admin, menu_up)
    time.sleep(0.2)
    sendCommand(url_admin, menu_enter)
    time.sleep(0.2)
    

def low_kick():
    sendCommand(url_command, game_down)
    time.sleep(0.2)
    sendCommand(url_command, game_front_kick)
    time.sleep(0.2)
    sendCommand(url_command, game_front_kick_disable)
    sendCommand(url_command, game_down_disable)
    time.sleep(0.2)
    

def teleport_right():
    sendCommand(url_command, game_down)
    time.sleep(0.1)
    sendCommand(url_command, game_left)    
    time.sleep(0.1)
    sendCommand(url_command, game_front_kick)
    time.sleep(0.1)
    sendCommand(url_command, game_down_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_left_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_front_kick_disable)
    time.sleep(0.2)



def teleport_left():
    sendCommand(url_command, game_down)
    time.sleep(0.1)
    sendCommand(url_command, game_right)    
    time.sleep(0.1)
    sendCommand(url_command, game_front_kick)
    time.sleep(0.1)
    sendCommand(url_command, game_down_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_right_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_front_kick_disable)
    time.sleep(0.2)

def spear_right():
    sendCommand(url_command, game_left)
    time.sleep(0.1)
    sendCommand(url_command, game_right)    
    time.sleep(0.1)
    sendCommand(url_command, game_front_punch)
    time.sleep(0.1)
    sendCommand(url_command, game_left_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_right_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_front_punch_disable)
    time.sleep(0.2)

def spear_left():
    sendCommand(url_command, game_right)
    time.sleep(0.1)
    sendCommand(url_command, game_left)
    time.sleep(0.1)
    sendCommand(url_command, game_front_punch)
    time.sleep(0.1)
    sendCommand(url_command, game_right_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_left_disable)
    time.sleep(0.1)
    sendCommand(url_command, game_front_punch_disable)
    time.sleep(0.2)

def forward2_right():
    sendCommand(url_command, game_right)
    time.sleep(0.2)
    sendCommand(url_command, game_back_punch)
    time.sleep(0.2)
    sendCommand(url_command, game_back_punch_disable)
    sendCommand(url_command, game_right_disable)
    time.sleep(0.2)

def forward2_left():
    sendCommand(url_command, game_left)
    time.sleep(0.2)
    sendCommand(url_command, game_back_punch)
    time.sleep(0.2)
    sendCommand(url_command, game_back_punch_disable)
    sendCommand(url_command, game_left_disable)
    time.sleep(0.2)

def takedown_left():
    sendCommand(url_command, game_right)
    time.sleep(0.2)
    sendCommand(url_command, game_left)
    time.sleep(0.2)
    sendCommand(url_command, game_back_kick)
    time.sleep(0.2)
    sendCommand(url_command, game_left_disable)
    sendCommand(url_command, game_right_disable)
    sendCommand(url_command, game_back_kick_disable)
    time.sleep(0.2)

def takedown_right():
    sendCommand(url_command, game_left)
    time.sleep(0.2)
    sendCommand(url_command, game_right)
    time.sleep(0.2)
    sendCommand(url_command, game_back_kick)
    time.sleep(0.2)
    sendCommand(url_command, game_right_disable)
    sendCommand(url_command, game_left_disable)
    sendCommand(url_command, game_back_kick_disable)
    time.sleep(0.2)

def move_right():
    sendCommand(url_command, game_right)
    time.sleep(0.2)
    sendCommand(url_command, game_right_disable)
    time.sleep(0.2)

def fpunch():
    sendCommand(url_command, game_front_punch)
    time.sleep(0.2)
    sendCommand(url_command, game_front_punch_disable)
    time.sleep(0.2)

def bpunch():
    sendCommand(url_command, game_back_punch)
    time.sleep(0.2)
    sendCommand(url_command, game_back_punch_disable)
    time.sleep(0.2)

def fkick():
    sendCommand(url_command, game_front_kick)
    time.sleep(0.2)
    sendCommand(url_command, game_front_kick_disable)
    time.sleep(0.2)

def bkick():
    sendCommand(url_command, game_back_kick)
    time.sleep(0.2)
    sendCommand(url_command, game_back_kick_disable)
    time.sleep(0.2)

def block():
    sendCommand(url_command, game_block)
    time.sleep(0.2)
    sendCommand(url_command, game_block_disable)

# UDP_IP = "0.0.0.0"
# UDP_PORT = 5005
# if (len(sys.argv) > 1):
#     UDP_PORT = int(sys.argv[1])
# startListening(UDP_IP, UDP_PORT, example)

if __name__ == "__main__":
    # move_right()
    while(True):
        teleport_right()
        time.sleep(0.2)
        teleport_left()
        time.sleep(0.2)

    while(True):
        line = sys.stdin.readline().strip()
        if (line == "mup"):
            sendCommand(url_admin, menu_up)
        if (line == "mdown"):
            sendCommand(url_admin, menu_down)
        if (line == "mleft"):
            sendCommand(url_admin, menu_left)
        if (line == "mright"):
            sendCommand(url_admin, menu_right)
        if (line == "menter"):
            sendCommand(url_admin, menu_enter)
        if (line == "mescape"):
            sendCommand(url_admin, menu_escape)
        if (line == "scorpio"):
            sendCommand(url_pselect, select_scorpio)
        if (line == "subzero"):
            sendCommand(url_pselect, select_subzero)
        if (line == "reset"):
            sendCommand(url_admin, shortcut_igtmm)
        if (line == "pvp"):
            sendCommand(url_admin, shortcut_2p)
        if (line == "select"):
            sendCommand(url_admin, shortcut_pselect)
        if (line == "gup"):
            sendCommand(url_command, game_up)
            time.sleep(0.1)
            sendCommand(url_command, game_up_disable)
            time.sleep(0.1)
        if (line == "gdown"):
            sendCommand(url_command, game_down)
            time.sleep(0.7)
            sendCommand(url_command, game_down_disable)
            time.sleep(0.1)
        if (line == "gleft"):
            sendCommand(url_command, game_left)
            time.sleep(0.1)
            sendCommand(url_command, game_left_disable)
            time.sleep(0.1)
        if (line == "gright"):
            sendCommand(url_command, game_right)
            time.sleep(0.1)
            sendCommand(url_command, game_right_disable)
            time.sleep(0.1)
        if (line == "fpunch"):
            sendCommand(url_command, game_front_punch)
            time.sleep(0.1)
            sendCommand(url_command, game_front_punch_disable)
            time.sleep(0.1)
        if (line == "bpunch"):
            sendCommand(url_command, game_back_punch)
            time.sleep(0.1)
            sendCommand(url_command, game_back_punch_disable)
            time.sleep(0.1)
        if (line == "fkick"):
            sendCommand(url_command, game_front_kick)
            time.sleep(0.1)
            sendCommand(url_command, game_front_kick_disable)
            time.sleep(0.1)
        if (line == "bkick"):
            sendCommand(url_command, game_back_kick)
            time.sleep(0.1)
            sendCommand(url_command, game_back_kick_disable)
            time.sleep(0.1)
        if (line == "throw"):
            sendCommand(url_command, game_throw)
            time.sleep(0.1)
            sendCommand(url_command, game_throw_disable)
            time.sleep(0.1)
        if (line == "block"):
            sendCommand(url_command, game_block)
            time.sleep(0.1)
            sendCommand(url_command, game_block_disable)
            time.sleep(0.1)
        if (line == "interact"):
            sendCommand(url_command, game_interact)



# sendCommand(url_admin, menu_escape)
# sendCommand(url_command, game_left)
# time.sleep(3)
# sendCommand(url_command, game_left_disable)

# count = 10

# while (count > 0):

    # count -= 1
    # forward2_right()
    # sendCommand(url_command, game_up)
    # time.sleep(0.2)
    # sendCommand(url_command, game_up_disable)
    # time.sleep(0.2)
    # sendCommand(url_command, game_right)
    # time.sleep(0.2)
    # sendCommand(url_command, game_right_disable)
    # time.sleep(0.2)
    # sendCommand(url_command, game_front_punch)
    # time.sleep(0.2)
    # sendCommand(url_command, game_front_punch_disable)
    # time.sleep(0.2)
    # sendCommand(url_command, game_back_kick)
    # time.sleep(0.2)
    # sendCommand(url_command, game_back_kick_disable)
    # time.sleep(0.2)
    # teleport_right()
    # time.sleep(0.2)
    # sendCommand(url_command, game_back_punch)
    # time.sleep(0.2)
    # sendCommand(url_command, game_back_punch_disable)
    # time.sleep(0.2)
    # sendCommand(url_command, game_front_punch)
    # time.sleep(0.2)
    # sendCommand(url_command, game_front_punch_disable)
    # time.sleep(0.2)

    # spear_right()
    # time.sleep(0.2)
    # takedown_right()
    # time.sleep(0.2)
    # teleport_right()
    # time.sleep(0.1)
    # spear_left()
    # time.sleep(0.2)
    # takedown_left()
    # time.sleep(0.2)
    # teleport_left()
    # time.sleep(0.1)
    
# while(True):
#     sendCommand(url_command, game_down)
#     time.sleep(0.2)
#     sendCommand(url_command, game_down_disable)
#     time.sleep(0.1)
# escape()

# sendCommand(url_admin, menu_enter)
# sendCommand(url_pselect, select_scorpio)

