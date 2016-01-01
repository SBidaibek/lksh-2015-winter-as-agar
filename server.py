#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
    TODO
    Что мы имплементим:
    какой-то init, который дёргает init у socket'ов
    callback, который дёргают socket'ы:
    - на чувак подключился
    - на чувак что-то послал
"""

import random
import math
import physics
from time import *
from threading import *

time_step = 0.03

class AgarioPlayer:
    def __init__(self, name, id, mass = 10):
        self.name = name
        self.id = id
        self.circles = [(random.randint(0, 8000), random.randint(0, 4000), mass)]
        self.cursor = self.circles[0][:2]

    def addCircle(self, mass = 1):
        self.circles.append((random.randint(0, 8000), random.randint(0, 4000), mass))


def distLinePoint(p, u, v):
    a = v[1] - u[1]
    b = u[0] - v[0]
    c = -(a * u[0] + b * u[1])
    return abs(a * u[0] + b * u[1] + c) / math.hypot(a, b)


def dp(a, b, c, d):
    ux = b[0] - a[0]
    uy = b[1] - a[1]
    vx = d[0] - c[0]
    vy = d[1] - c[1]
    return ux * vx + uy * vy


def distRayPoint(p, a, b):
    if (dp(a, b, a, p) <= 0):
        return math.hypot(p[0] - a[0], p[1] - a[1])
    else:
        return distLinePoint(p, a, b)


def distSegmentPoint(p, a, b):
    return max(distRayPoint(p, a, b), distRayPoint(p, b, a))


def doCircleAndRectIntersect(p, r, a, b, c, d):
    if a[0] <= p[0] <= c[0] and a[1] <= p[1] <= c[1]:
        return True
    return min(distSegmentPoint(p, a, b), distSegmentPoint(p, b, c), distSegmentPoint(p, c, d), distSegmentPoint(p, d, a)) <= r


class AgarioServer:
    def __init__(self):
        """
            call init у сокетов
        """
        self.playerLock = Lock()
        self.cursorLock = Lock()
        food = AgarioPlayer('Food', 1)
        food.id = 0
        self.players = {0 : food}

    def addPlayer(self, name, id):
        self.playerLock.acquire()
        player = AgarioPlayer(name, id)
        self.player[player.id] = player
        self.realPlayers.add(player.id)
        self.playerLock.release()
        return player.id

    def addFood(self, cnt):
        food = self.players[0]
        for i in range(cnt):
            food.addCircle(1)

    def updateCursor(self, cursor):
        """
            cursor['x'] = x курсора
            cursor['y'] = y курсора
            cursor['id'] = id игрока
        """
        self.cursorLock.acquire()
        self.player[cursor['id']].cursor = (cursor['x'], cursor['y'])
        self.cursorLock.release()

    def updateCirlces(self, circles):
        for pl in self.players:
            pl.circles = []
        for circle in circles:
            self.players[circle['id']].circles.append((circle['x'], circle['y'], circle['mass']))

    def makeFieldMessage(self, id):
        center = self.players[id].circles[0][:2]
        ans = []
        for player in self.players:
            for circle in player.circles:
                player_balls = []
                if doCircleAndRectIntersect((circle[0], circle[1]), math.sqrt(circle[2]), \
                                            (center[0] - 400, center[1] - 200), (center[0] - 400, center[1] + 200), \
                                            (center[0] + 400, center[1] + 200), (center[0] + 400, center[1] - 200)):
                    player_balls.append({'x' : circle[0], 'y': circle[1], 'm': circle[2]})
                ans.append({'name': player.name, 'color' : 'blue', 'id': player.id, 'balls': player_balls})
        return ans


server = AgarioServer()

addPlayerCallback = lambda name, id: server.addPlayer(name, id)
updateCursorCallback = lambda cursor: server.updateCursor(cursor)

lastTime = time()

while True:
    now = time()
    if (lastTime + time_step < now):
        """
            часть где всё обновляется
        """
        server.cursorLock.acquire()
        server.playerLock.acquire()

        server.addFood(1)
        cursors = []
        circles = []
        for pl in server.players:
            id = pl.id
            cursors.append({'x' : pl.cursor[0], 'y' : pl.cursor[1], 'id' : id})
            for circle in pl.circles:
                circles.append({'x' : circles[0], 'y' : circle[1], 'm' : circle[2], 'id' : id})
        server.updateCirlces(circles)
        newcirlces = physics.updateMap0(cursors, circles, time_step)

        server.cursorLock.release()
        server.playerLock.release()
        """
            рассказать всем о новых полях
        """
        pass
    else:
        sleep(0.01)
