
"""Echo server using the threading API."""

import asyncio
from websockets.asyncio.server import serve, broadcast
import json
import uuid
from sqids import Sqids
import random
import requests as req
import emoji_generator.random_emoji as emojigen

r = req.get("http://checkip.amazonaws.com")
ip = r.text


sqids = Sqids(alphabet="1234567890", min_length=4)

rooms = []
active_room_codes = []
sockets = set()

async def echo(websocket):
    async for message in websocket:
        m = json.loads(message)
        print(active_room_codes)
        match m["t"]:
            case "NEWROOM":
                code = generate_room_code()
                pid = str(uuid.uuid4())
                print(pid)
                rooms.append({
                    "code": code,
                    "sockets": {websocket},
                    "players": [pid]
                })
                r = {
                    "t": "NEWROOMX",
                    "code": code,
                    "id": pid
                }
                print("◈ CREATING NEW ROOM: " + code)
                await websocket.send(json.dumps(r))
            case "JOIN":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                if room:
                    pid = str(uuid.uuid4())
                    room["players"].append(pid)
                    room["sockets"].add(websocket)
                    r = {
                        "t": "JOINX",
                        "id": pid,
                        "list": room["players"],
                    }
                    print("◈ PLAYER JOINED ROOM" + m["code"]+ ". ID CREATED: " + pid)
                    
                    rh = {
                        "t": "HJOINX",
                        "id": pid,
                        "list": room["players"]
                    }
                    broadcast(room["sockets"], json.dumps(rh))
                else:
                    r = {
                        "t": "JOINX",
                        "err": "room not found"
                    }
                await websocket.send(json.dumps(r))
                
            case "START":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                r = {
                    "t": "STARTX",
                    "code": room["code"],
                    "first": room["players"][0]
                }
                broadcast(room["sockets"], json.dumps(r))
            case "SWAP":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                print("◈ CARD SWAP. CONTENT:\n" + str(m))
                r = {
                    "t": "SWAPX",
                    "from": m["from"],
                    "to": m["to"],
                    "id": m["id"]
                }
                print("SENDING:\n" + str(r))
                broadcast(room["sockets"], json.dumps(r))
            case "ATK":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                print("◈ ATTACK. CONTENT:\n" + str(m))
                r = {
                    "t": "ATKX",
                    "card": m["card"],
                    "id": m["id"]
                }
                print("SENDING:\n" + str(r))
                broadcast(room["sockets"], json.dumps(r))
            case "COMBO":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                print("◈ COMBO TRIGGERED. CONTENT:\n" + str(m))
                r = {
                    "t": "COMBOX",
                    "id": m["id"]
                }
                print("SENDING:\n" + str(r))
                broadcast(room["sockets"], json.dumps(r))
            case "USE":
                room = next((room for room in rooms if room["code"] == m["code"]), False) # Search for rooms
                print("◈ USE TRIGGERED. CONTENT:\n" + str(m))
                r = {
                    "t": "USEX",
                    "id": m["id"]
                }
                print("SENDING:\n" + str(r))
                broadcast(room["sockets"], json.dumps(r))
            case "END":
                if m["code"] in active_room_codes:
                    print(str(m["code"]))
                    print(active_room_codes)
                    active_room_codes.remove(str(m["code"]))
                    print("◈ CLOSING ROOM: " + str(m["code"]))
            case _:
                print("◈ UNKNOWN TYPE. CONTENT:\n" + str(m))
            
def generate_room_code():
    
    c = sqids.encode([random.randint(0,100)])
    while c in active_room_codes:
        c = sqids.encode([random.randint(0,100)])
    active_room_codes.append(c)
    print(active_room_codes)
    return c
    

async def main():
    async with serve(echo, "localhost", 8765) as server:
        await server.serve_forever()


if __name__ == "__main__":
    print("⁘ STARTING SERVER ON " + ip)
    asyncio.run(main())