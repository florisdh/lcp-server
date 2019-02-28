from src.data.dataBaseConnection import DataBaseConnection
from src.gameServer import GameServer
import src.data.byteConverter as ByteConverter

_localIp = ""
_localPort = 1337
_server = None

def main():

	# Start server
	_server = GameServer(_localIp, _localPort)
	_server.loadDataBase("./data/data.db")
	_server.start(10)
	
	print(">: Server started at port " + str(_localPort))

	# Handle input
	while True:
		try:
			cmd = raw_input("").split(" ")
		except:
			break

		if cmd[0] == "exit":
			break

		elif cmd[0] == "save":
			_server.saveDataBase()
			print(">: Database saved.")
			
		elif cmd[0] == "list":
			if len(cmd) == 2:
				if cmd[1] == "players":
					print(">: Total players: " + str(len(_server.connectedClients)))
					for p in _server.connectedClients:
						print(">:	{0}: {1}".format(str(p.playerID), str(p.address)))
				elif cmd[1] == "rooms":
					print(">: Total rooms: " + str(_server.rooms.totalRooms))
					for p in _server.rooms.rooms:
						print(">:	{0}: {1}".format(str(p.roomID), str(p.name)))
				else:
					print("!: Invalid cmd format. use: list [players|rooms]")
			else:
				print("!: Invalid cmd format. use: list [players|rooms]")

		elif cmd[0] == "register":
			if len(cmd) != 3:
				print("!: Invalid cmd format. use: register [usr] [pw]")
				continue

			try:
				resID = _server.db.addUser(cmd[1], cmd[2])
				_server.db.commit()
			except Exception as e:
				print("!: Failed to register user:" + str(e))
				continue

			print(">: Registered user with name {0} password {1} id {2}".format(cmd[1], cmd[2], str(resID)))

		else:
			print("!: Unknown command.")

	if _server:
		_server.stop()
		
main()
