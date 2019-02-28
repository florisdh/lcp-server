from src.data.dataBaseConnection import DataBaseConnection
import src.data.byteConverter as ByteConverter
from src.net.udpClient import UDPClient
from src.net.clientState import ClientState
from src.game.gameRoomManager import GameRoomManager
from src.game.gameRoom import GameRoom
import src.packages.packages as Packages
from src.packages.packageTypes import PackageTypes
from src.packages.packageFactory import PackageFactory
from Crypto.Cipher import PKCS1_OAEP, AES, AES
from Crypto.PublicKey import RSA
from Crypto.Util import asn1
from Crypto import Random
import threading
import socket
import codecs
import struct

class GameServer(object):
	
	def __init__(self, hostIp, hostPort):
		self.hostIp = hostIp
		self.hostPort = hostPort
		self.isStarted = False
		self.db = DataBaseConnection()
		self.dbLoaded = False
		self.rooms = GameRoomManager(10)
		
		# Add test Room
		testRoom = GameRoom("TestRoom", 1, 1, 200)
		self.rooms.addRoom(testRoom)

	def loadDataBase(self, fileName):
		self.db.connect(fileName)
		self.dbLoaded = True

	def saveDataBase(self):
		self.db.commit()

	def start(self, maxConnections):
		if self.isStarted:
			return
		self.isStarted = True

		self.hostConnection = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
		self.hostConnection.bind((self.hostIp, self.hostPort))
		self.hostConnection.listen(maxConnections)

		self.clients = []

		self.acceptThread = threading.Thread(target=self.accept)
		self.acceptThread.daemon = True
		self.acceptThread.start()

		self.udpClient = UDPClient(self.hostIp, self.hostPort + 1)
		self.udpClient.start()

		self.udpThread = threading.Thread(target=self.udpReceive)
		self.udpThread.daemon = True
		self.udpThread.start()

	def stop(self, force = False):
		if not self.isStarted:
			return
		self.isStarted = False

		# Save dataBase
		if not force:
			self.saveDataBase()
		self.db.close()

		# Disconnect clients
		for client in self.clients:
			client.close()

		# Stop hosting
		#self.hostConnection.shutdown(socket.SHUT_RDWR)
		self.hostConnection.close()

	def accept(self):
		while self.isStarted:
			try:
				(conn, addr) = self.hostConnection.accept()
			except:
				continue

			self.onClientConnected(conn, addr)

	def receive(self, client):
		while self.isStarted:
			try:
				bytesReceived = client.connection.recv_into(client.recvBuffer)
			except:
				print("Closed connection to client " + str(client.address))
				break

			# Client Disconnect
			if bytesReceived == 0:
				self.onClientDisconnect(client)
				break
			
			# Decrypt
			plain = bytes(client.recvBuffer[0:bytesReceived])
			if client.safeConnection:
				try:
					plain = client.cipher.decrypt(plain)
				except Exception as e:
					print("Failed to decrypt data from " + str(client.address))
					break

			# Handle Client Message On Same thread
			self.handleClientMessage(plain, client)
			
	def udpReceive(self):
		while self.isStarted:
			(addr, data) = self.udpClient.receive()
			
			print("UDP Received {0} bytes from {1}".format(len(data), str(addr)))

			try:
				typedPackage = PackageFactory.UnPack(data)
				if typedPackage.type == PackageTypes.RegisterUDP:
					packageData = Packages.UDPRegisterData.fromBytes(typedPackage.data)
				
					# Search for client
					for client in self.clients:
						if client.playerID == packageData.clientID:
							if client.udpRegistered:
								print("Received udp request but Already registered by addr: " + str(addr))
								break

							# Validate key
							if client.udpKey != packageData.clientKey:
								print("Received invalid udp request with id {0} with key of length {1} from {2}.".format(str(packageData.clientID), str(len(packageData.clientKey)), str(addr)))
								break

							self.onUdpRegistered(client, addr)
							break

			except Exception as e:
				print("Failed to parse {0}b of data from {1}. err: {2}".format(str(len(data)), str(addr), str(e)))

	def handleClientMessage(self, data, client):
		# Parse package
		package = PackageFactory.UnPack(data)
		
		## Security request ##
		if package.type == PackageTypes.RequestSecureConnection:
			if client.safeConnection == False:
				loaded = False

				# Parse data
				try:
					package = Packages.SecurityRequestData.fromBytes(package.data)

					# Load RSA from client
					rsa = RSA.construct((package.modulus, package.exponent))
					client.cipher = PKCS1_OAEP.new(rsa)
					
					loaded = True
				except Exception as e:
					print("!> Failed to load rsa: " + str(e))
					
				if loaded:
					# Create random security key for future comm with AES
					key = Random.get_random_bytes(32)
					
					# Send Key to client using RSA
					returnPackage = Packages.SecuritySetupData(key)
					self.sendMessage(client, PackageTypes.SetupSecureConnection, returnPackage)
					
					# Apply AES
					client.cipher = AES.new(key, AES.MODE_ECB)
					client.safeConnection = True
			else:
				print("!> Client requests for secure connection multiple times. ip:" + str(client.address))

		elif not client.safeConnection:
			print("!> Client requests is not secured:" + str(client.address))

		## Login ##
		elif package.type == PackageTypes.LoginAttempt:
			# Parse data
			credentials = None
			try:
				credentials = Packages.ClientLoginData.fromBytes(package.data)
			except Exception as e:
				print("!> Failed to parse login: " + str(e))
				return

			# Validate credentials in db
			result = self.db.validateUserCredentials(credentials.username, credentials.password)

			if result != None:
				self.onClientLogin(client, result[0], credentials.username)
			else:
				self.sendMessage(client, PackageTypes.LoginFailed, None)

		## Logout ##
		elif package.type == PackageTypes.Logout:
			self.onClientLogout(client)

		## Create Room ##
		elif package.type == PackageTypes.CreateRoom:
			if not client.logedIn or not client.udpRegistered:
				print("!> Client unauthorized")
				return

			# Try parse data
			room = None
			try:
				roomInfo = Packages.CreateRoomData.fromBytes(package.data)
				room = GameRoom(roomInfo.name, roomInfo.maxPlayers, roomInfo.mapID, client.playerID)
				res = self.rooms.addRoom(room)
			except Exception as e:
				print("!> Failed to parse room create msg:" + str(e.message))
				return

			self.onCreateRoom(client, room)

		## Room list ##
		elif package.type == PackageTypes.RequestRooms:
			if not client.logedIn:
				print("!> Client unauthorized")
				return

			package = Packages.RoomListData(self.rooms)
			self.sendMessage(client, PackageTypes.RoomList, package)

		## Join Room ##
		elif package.type == PackageTypes.RequestJoin:
			if not client.logedIn or not client.udpRegistered:
				print("!> Client unauthorized")
				return

			# Parse data
			roomID = -1
			try:
				package = Packages.JoinRequestData.fromBytes(package.data)
				roomID = package.roomID
			except Exception as e:
				print("!> Failed to parse Join Request: " + e.message)
				return

			# Check if room exists
			room = self.rooms.fromID(roomID)
			if room != None:
				self.onJoinRoom(client, room)	
			else:
				print("!> Request room index out of range")

		## Leave Room ##
		elif package.type == PackageTypes.LeaveRoom:
			if not client.logedIn:
				print("Client unauthorized")
				return
			self.onLeaveRoom(client)
		
		elif package.type == PackageTypes.ChangeSetup:
			if not client.logedIn:
				print("!> Client unauthorized")
				return
			if not client.inRoom:
				print("!> Client not in room.")
				return

			setup = None
			try:
				setup = Packages.RoomPlayerSetupData.fromBytes(package.data).setup
			except Exception as e:
				print("!> Failed to parse setup info. err: " + e.message + " args: " + str(e.args))

			if setup:
				# TODO: validate new setup
				client.roomClient.setup = setup
				self.onSetupChange(client)

		elif package.type == PackageTypes.GameLoaded:
			if not client.inRoom:
				print("Load msg but not in room")
				return
			if client.roomClient.loaded:
				print("Load msg but already loaded")
				return

			client.roomClient.loaded = True

			# Check if game ready
			if client.room.checkLoaded():
				self.onStartRoom(client.room)

		elif package.type == PackageTypes.PlayerDied:
			if not client.inRoom:
				print("Player died but not in room")
				return
			if not client.roomClient.loaded:
				print("Player died but not even loaded")
				return
			self.onPlayerDied(client)

		## Unknow Package ##
		else:
			print("!> Unknown msg with type {0} and length {1}.".format(str(package.type), str(len(package.data))))

	def sendData(self, client, data):
		if client.safeConnection == True:
			data = ByteConverter.encode_pkcs7(data, 16)
		encrypted = client.cipher.encrypt(data)
		client.connection.send(encrypted)

	def sendMessage(self, client, type, data):
		self.sendData(client, PackageFactory.Pack(type, data))

	def onClientConnected(self, conn, addr):
			# Add client to connected
			client = ClientState(conn, addr)
			self.clients.append(client)

			# Create receive thread for client
			client.thread = threading.Thread(target=self.receive, args=(client,))
			client.thread.daemon = True
			client.thread.start()

			print(":> Client Connected: " + str(client.address))

	def onClientDisconnect(self, client):
		self.onClientLogout(client)
		self.clients.remove(client)
		client.connection.close()
		print(":> Client Disconnected: " + str(client.address))

	def onClientLogin(self, client, id, usr):
		client.playerID = id
		client.userName = usr
		client.logedIn = True

		# Create UDP-Key for client
		client.udpKey = Random.get_random_bytes(8)

		self.sendMessage(client, PackageTypes.LoginSucceed, Packages.LoginSucceedData(client.playerID, client.udpKey))

		print(":> {0} loged in.".format(client.userName))

	def onClientLogout(self, client):
		if client.logedIn:
			self.onLeaveRoom(client)
			client.logedIn = False
			print(":> {0} loged out.".format(client.userName))
			client.userName = ""

	def onCreateRoom(self, client, room):
		self.sendMessage(client, PackageTypes.RoomCreated, None)
		self.onJoinRoom(client, room)

	def onJoinRoom(self, client, room):
		playerInfo = room.addClient(client)
		if playerInfo != None:

			# Send requestor that he joined
			self.sendMessage(client, PackageTypes.JoinedRoom, Packages.JoinedRoomInfoData(room))

			print(":> {0} joined room {1}".format(client.userName, client.room.name))

			# Send to other players that he joined
			msg = Packages.RoomPlayerData(playerInfo)
			for other in room.players:
				if other.playerID != client.playerID:
					self.sendMessage(other.client, PackageTypes.OtherJoinedRoom, msg)
		else:
			# TODO: Let client know room is full
			print(":> Request is full")

	def onLeaveRoom(self, client):
		if client.inRoom:
			roomName = client.room.name
			room = client.room
			res = room.removeClient(client)
			if res:
				print(":> {0} left room {1}".format(client.userName, roomName))

				# Was last player
				if room.totalPlayers == 0:
					self.rooms.removeRoom(room)
					print(":> Remove room {0} because players left.".format(room.name))

				# Send other players that he left
				else:
					msg = Packages.PlayerIDData(client.playerID)
					for other in room.players:
						self.sendMessage(other.client, PackageTypes.OtherLeftRoom, msg)
			else:
				print("!> Failed to remove client from room.")

	def onSetupChange(self, client):
		if client.inRoom:
			room = client.room
			msg = Packages.OtherPlayerSetupData(client.playerID, client.roomClient.setup)

			# Send to other players
			for other in room.players:
				self.sendMessage(other.client, PackageTypes.OtherChangedSetup, msg)

			# Check if game ready
			if not room.loading and room.checkReady():
				self.onLoadRoom(room)

	def onUdpRegistered(self, client, addr):
		client.udpRegistered = True
		client.udpEP = addr
		self.sendMessage(client, PackageTypes.UDPRegistered, None)
		print("UDP client registered id {0} from {1}".format(client.playerID, str(addr)))

	def onLoadRoom(self, room):
		if room.loading:
			return
		room.loading = True

		print("Load room " + room.name)

		# Construct udpEP info package from all players
		msg = Packages.RoomUdpSetupData()
		for other in room.players:
			msg.addPlayer(other.playerID, other.client.udpEP)

		# Send to all players
		for other in room.players:
			self.sendMessage(other.client, PackageTypes.RoomLoad, msg)

	def onStartRoom(self, room):
		if not room.loading:
			return
		room.loading = False
		room.started = True

		print("Started room " + room.name)

		# Send to players
		for p in room.players:
			p.alive = True
			self.sendMessage(p.client, PackageTypes.RoomStart, None)

	def onPlayerDied(self, client):
		if not client.roomClient.alive:
			print("Player died but was already dead..?")
			return

		print("Player has died " + str(client.playerID))
		client.roomClient.alive = False
		
		# Send to other clients
		for other in client.room.players:
			if other.playerID != client.playerID:
				self.sendMessage(other.client, PackageTypes.OtherDied, None)

		# Check if all players died
		if client.room.checkFinished():
			print("Game Finished!")
			for other in client.room.players:
				self.sendMessage(other.client, PackageTypes.RoomFinished, None)
