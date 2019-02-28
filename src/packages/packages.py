import src.data.byteConverter as ByteConverter
from src.game.playerSetup import PlayerSetup

## General Packages ##

class TypedPackage(object):
	def __init__(self, type, data):
		self.type = type
		self.data = data

class PackageData(object):
	def toBytes(self):
		pass
	@staticmethod
	def fromBytes(data):
		pass

class ErrorData(PackageData):
	def __init__(self, errorId):
		self.errorId = errorId
	def toBytes(self):
		pass
	@staticmethod
	def fromBytes(data):
		errorId = ByteConverter.uint8_from_bytes(data)
		return ErrorPackage(errorId)

## Client Packages ##

class SecurityRequestData(PackageData):
	def __init__(self, exponent, modulus):
		self.exponent = exponent
		self.modulus = modulus
	@staticmethod
	def fromBytes(data):
		exponent = ByteConverter.variableSizedInt_from_bytes(data[:3])
		modulus = ByteConverter.variableSizedInt_from_bytes(data[3:])
		return SecurityRequestData(exponent, modulus)

class ClientLoginData(PackageData):
	def __init__(self, username, password):
		self.username = username
		self.password = password
	@staticmethod
	def fromBytes(data):
		usrLength = ByteConverter.uint8_from_bytes(data[0])
		username = ByteConverter.string_from_bytes(data[1:usrLength+1])
		pwLength = ByteConverter.uint8_from_bytes(data[usrLength+1])
		password = ByteConverter.string_from_bytes(data[usrLength+2:usrLength+2+pwLength])
		return ClientLoginData(username, password)
	
class CreateRoomData(PackageData):
	def __init__(self, name, maxPlayers, mapID):
		self.name = name
		self.maxPlayers = maxPlayers
		self.mapID = mapID
	@staticmethod
	def fromBytes(data):
		nameLength = ByteConverter.uint8_from_bytes(data[0])
		name = ByteConverter.string_from_bytes(data[1:nameLength+1])
		maxPlayers = ByteConverter.uint8_from_bytes(data[nameLength+1])
		mapID = ByteConverter.uint8_from_bytes(data[nameLength+2])
		return CreateRoomData(name, maxPlayers, mapID)

class JoinRequestData(PackageData):
	def __init__(self, roomID):
		self.roomID = roomID
	@staticmethod
	def fromBytes(data):
		roomID = ByteConverter.int32_from_bytes(data)
		return JoinRequestData(roomID)

class UDPRegisterData(PackageData):
	def __init__(self, clientID, clientKey):
		self.clientID = clientID
		self.clientKey = clientKey
	@staticmethod
	def fromBytes(data):
		clientID = ByteConverter.int32_from_bytes(data[0:4])
		clientKey = data[4:12]
		return UDPRegisterData(clientID, clientKey)

## Server Packages ##

class SecuritySetupData(PackageData):
	def __init__(self, encryptionKey):
		self.encryptionKey = encryptionKey
	def toBytes(self):
		return bytes(self.encryptionKey)

class LoginSucceedData(PackageData):
	def __init__(self, playerID, udpKey):
		self.playerID = PlayerIDData(playerID)
		self.udpKey = udpKey
	def toBytes(self):
		data = bytearray()

		# Add playerID
		data.extend(self.playerID.toBytes())
		
		# Add udp key
		data.extend(self.udpKey)
		
		return bytes(data)

class PlayerIDData(PackageData):
	def __init__(self, playerID):
		self.playerID = playerID
	def toBytes(self):
		return ByteConverter.int32_to_bytes(self.playerID)

class JoinedRoomInfoData(PackageData):
	def __init__(self, room):
		self.room = room
	def toBytes(self):
		data = bytearray()

		# Add Room Info
		data.extend(RoomInfoData(self.room).toBytes())
		
		# Add players
		data.extend(ByteConverter.uint8_to_bytes(len(self.room.players)))
		for p in self.room.players:
			data.extend(RoomPlayerData(p).toBytes())

		return bytes(data)
	
class RoomInfoData(PackageData):
	def __init__(self, room):
		self.room = room
	def toBytes(self):
		data = bytearray()
		
		data.extend(ByteConverter.int32_to_bytes(self.room.roomID))
		data.extend(ByteConverter.uint8_to_bytes(len(self.room.name)))
		data.extend(ByteConverter.string_to_bytes(self.room.name))
		data.extend(ByteConverter.uint8_to_bytes(self.room.maxPlayers))
		data.extend(ByteConverter.uint8_to_bytes(self.room.mapID))
		data.extend(ByteConverter.uint8_to_bytes(self.room.creatorID))

		return bytes(data)
			
class RoomPlayerData(PackageData):
	def __init__(self, player):
		self.player = player
	def toBytes(self):
		data = bytearray()

		data.extend(ByteConverter.uint8_to_bytes(self.player.playerID))
		data.extend(ByteConverter.uint8_to_bytes(len(self.player.playerName)))
		data.extend(ByteConverter.string_to_bytes(self.player.playerName))
		data.extend(ByteConverter.uint8_to_bytes(self.player.spawnPointID))
		data.extend(RoomPlayerSetupData(self.player.setup).toBytes())

		return bytes(data)

class IPEPData(PackageData):
	def __init__(self, addr):
		self.ip = addr[0]
		self.port = addr[1]
	def toBytes(self):
		data = bytearray()

		data.extend(ByteConverter.uint8_to_bytes(len(self.ip)))
		data.extend(ByteConverter.string_to_bytes(self.ip))
		data.extend(ByteConverter.uint16_to_bytes(self.port))

		return bytes(data)

class RoomPlayerSetupData(PackageData):
	def __init__(self, setup):
		self.setup = setup
	def toBytes(self):
		data = bytearray()

		data.extend(ByteConverter.uint8_to_bytes(self.setup.boatID))
		data.extend(ByteConverter.uint8_to_bytes(self.setup.flagColorID))
		data.extend(ByteConverter.bool_to_bytes(self.setup.ready))

		return bytes(data)
	@staticmethod
	def fromBytes(data):
		boatID = ByteConverter.uint8_from_bytes(data[0:1])
		colorID = ByteConverter.uint8_from_bytes(data[1:2])
		ready = ByteConverter.uint8_from_bytes(data[2:3]) == 1
		return RoomPlayerSetupData(PlayerSetup(boatID, colorID, ready))

class RoomListData(PackageData):
	def __init__(self, rooms):
		self.rooms = rooms
	def toBytes(self):
		data = bytearray()

		data.extend(ByteConverter.uint8_to_bytes(self.rooms.totalRooms))
		for room in self.rooms.rooms:
			data.extend(RoomInfoData(room).toBytes())

		return bytes(data)

class OtherPlayerSetupData(PackageData):
	def __init__(self, playerID, setup):
		self.playerID = playerID
		self.setup = setup
	def toBytes(self):
		data = bytearray()
		data.extend(PlayerIDData(self.playerID).toBytes())
		data.extend(RoomPlayerSetupData(self.setup).toBytes())
		return bytes(data)

class RoomUdpSetupData(PackageData):
	def __init__(self):
		self.UdpPlayerList = []
	def addPlayer(self, playerID, udpEP):
		self.UdpPlayerList.append(PlayerUdpSetupData(playerID, udpEP))
	def remPlayer(self, playerID):
		for p in self.UdpPlayerList:
			if p.playerID == playerID:
				self.UdpPlayerList.remove(p)
				break
	def toBytes(self):
		data = bytearray()

		data.extend(ByteConverter.uint8_to_bytes(len(self.UdpPlayerList)))
		for p in self.UdpPlayerList:
			data.extend(p.toBytes())

		return bytes(data)

class PlayerUdpSetupData(PackageData):
	def __init__(self, playerID, endpoint):
		self.playerID = playerID
		self.ep = endpoint
	def toBytes(self):
		data = bytearray()
		data.extend(PlayerIDData(self.playerID).toBytes())
		data.extend(IPEPData(self.ep).toBytes())
		return bytes(data)

