#!/usr/bin/env python3

from tkinter import *
from draw import *
from client_protocol import *
from leaderboard import *
import threading
import time
import sys
from constants import *

splitLock = threading.Lock()
splitted = 0
last_mf = 1

def onMotion(e):
    global curx, cury, canvas
    curx = e.x
    cury = e.y

def sending():
    global curx, cury, player_id, splitLock, splitted
    while True:
        ourx, oury = 0, 0
        if (curList != []):
            for p in curList['players']:
               if p["id"] == player_id:
                   ourx, oury = p["balls"][0]["x"], p["balls"][0]["y"]
                   break
        splitLock.acquire()
        s = splitted
        splitted = 0
        splitLock.release()
        sendMe({"id": player_id, "x": ourx - WINDOW_WIDTH // 2 + curx, "y": oury - WINDOW_HEIGHT // 2 + cury, "s": s})
        # {'x': 1, 'y': 1, 's': 0}
        time.sleep(0.01)
                                                
def asking():
    global curList
    fail = 0
    tm = time.time()
    cnt = 0
    while True:
        # print("abacabadabacaba")
        curList = getField()
     
        if curList == []:
            fail += 1
            if fail > FAIL_COUNT:
                print(fail)
                root.quit()
                exit(0)
        else:
            fail = 0
            now = time.time()
            cnt += 1
            if DEBUG_PROTOCOL_PRINT:
                if (now - tm > 3):
                    print(cnt, cnt  / (now - tm))
                    cnt = 0
                    tm = now
        # print('getField: '+str(curList))
        # print("abacaba")
        time.sleep(0.01)

def splitMe(event):
    global splitLock, splitted
    # print('splitting')
    splitLock.acquire()
    splitted = 1
    splitLock.release()

def drawing():
    global canvas, player_id, curList
    ourx, oury, sum_mass = WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2, 0
    lb = []
    if (curList != []):
        ll = curList['players']
        lb = curList['leaderboard']
        for p in ll:
            if p["id"] == player_id:
                for b in p["balls"]:
                    newx, newy = b['x'], b['y']
                    ourx += newx * b['m']
                    oury += newy * b['m']
                    sum_mass += b['m']
                break  
         # [{'name': 'Vasya', 'color': 'blue', 'id': 1, 'balls': [{'x': 1, 'm': 1, 'y': 1}]}]
    else:
        ourx, oury, sum_mass = 0, 0, INITIAL_MASS
        ll = []
    if sum_mass > 0:
        ourx /= sum_mass
        oury /= sum_mass
    mf = massFactor(sum_mass)
    global last_mf
    if mf > last_mf:
        last_mf += min(DELTA_MF, mf - last_mf)
    else:
        last_mf -= min(DELTA_MF, last_mf - mf)
    mf = last_mf
    canvas.delete("all")
    canvas = draw_bg(canvas, (ourx - WINDOW_WIDTH // 2, oury - WINDOW_HEIGHT // 2), mf)
    canvas = draw_players(canvas, (ourx - WINDOW_WIDTH // 2, oury - WINDOW_HEIGHT // 2), ll, mf)
    canvas = draw_mass(canvas, 'm:' + str(sum_mass) + ' x:' + str(int(round(ourx))) + ' y:' + str(int(round(oury))))
    root.after(10, drawing)
    canvas = draw_leaderboard(canvas, lb, player_id)



root = Tk()
root.wm_resizable(0, 0)
root.geometry(str(WINDOW_WIDTH) + 'x' + str(WINDOW_HEIGHT))
root.title("agar.io_test")

userName, ip, port = None, None, None
if len(sys.argv) > 1:
    userName = sys.argv[1]
if len(sys.argv) > 2:
    ip = sys.argv[2]
if len(sys.argv) > 2:
    port = sys.argv[3]

# PATCHED BY BURUNDUK1 
ip, port = open("config.txt", "r").readline().split()
# END OF PATCH

#ip = '192.168.3.83'
#port = '3030'

if userName is None:
    print('enter your user name: ', end='', flush=True)
    userName = " ".join(sys.stdin.readline().split())
print("OK. Your username is " + userName)

player_id = registerMe(userName)
print(ip)

if ip is None:
    print('enter server ip: ', end='', flush=True)
    ip = sys.stdin.readline().split()[0]
print("OK. ip is " + ip)

if port is None:
    print('enter port: ', end='', flush=True)
    port = sys.stdin.readline().split()[0]
print("OK. port is " + port)

#out = open("config.txt", "w")
#out.write(ip + " " + port)
#out.close()
# At first get name from keyboard
print("connected")

root.tkraise()

curx, cury = 400, 225
# curList = getField()
curList = []
root.bind("<Motion>", onMotion)

canvas = Canvas(root, height=WINDOW_HEIGHT, width=WINDOW_WIDTH)
canvas.pack()

t1 = threading.Thread(target=asking, daemon=True)
t2 = threading.Thread(target=sending, daemon=True)
t1.start()
t2.start()
root.bind('<Button-1>', splitMe)
root.after(0, drawing)

root.mainloop()
