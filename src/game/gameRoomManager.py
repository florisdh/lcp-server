class GameRoomManager(object):
	"""Container for gameRooms and managing room identities."""

	def __init__(self, maxRooms):
		self.maxRooms = maxRooms
		self.totalRooms = 0
		self.rooms = []
		self.roomIDCounter = 0
		self.availableRoomIDs = []

	def addRoom(self, room):
		if self.totalRooms >= self.maxRooms:
			return False

		self.totalRooms += 1
		room.roomID = self.getNextID()
		self.rooms.append(room)

		return True

	def removeRoom(self, room):
		if room in self.rooms:
			self.totalRooms -= 1
			self.rooms.remove(room)
			self.availableRoomIDs.append(room.roomID)

	def fromID(self, roomID):
		for room in self.rooms:
			if room.roomID == roomID:
				return room
		return None

	def getNextID(self):
		if len(self.availableRoomIDs) > 0:
			return self.availableRoomIDs.pop()
		else:
			self.roomIDCounter += 1
			return self.roomIDCounter
