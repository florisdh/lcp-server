from src.game.gamePlayer import GamePlayer
from src.game.playerSetup import PlayerSetup

class GameRoom(object):
	"""Managing game players and containing room meta."""

	def __init__(self, name, maxPlayers, mapID, creatorID):
		self.roomID = -1
		self.name = name
		self.maxPlayers = maxPlayers
		self.mapID = mapID
		self.creatorID = creatorID
		self.players = []
		self.totalPlayers = 0
		self.started = False
		self.loading = False
		self.finished = False
		self.spawnCounter = 0
		self.availableSpawnPoints = []

	def addClient(self, client):
		if self.totalPlayers < self.maxPlayers and not client.inRoom:
			playerInfo = GamePlayer(client, self.getNextSpawnPoint(), PlayerSetup(0, 0, False))
			self.totalPlayers += 1
			self.players.append(playerInfo)
			client.inRoom = True
			client.room = self
			client.roomClient = playerInfo
			return playerInfo
		return None

	def removeClient(self, client):
		for player in self.players:
			if player.playerID == client.playerID:
				self.players.remove(player)
				self.totalPlayers -= 1
				self.availableSpawnPoints.append(player.spawnPointID)
				client.inRoom = False
				client.room = None
				client.roomClient = None
				return True
		return False

	def getNextSpawnPoint(self):
		if len(self.availableSpawnPoints) > 0:
			return self.availableSpawnPoints.pop()
		self.spawnCounter += 1
		return self.spawnCounter - 1

	def checkReady(self):
		if self.totalPlayers != self.maxPlayers:
			return False
		for player in self.players:
			if not player.setup.ready or not player.client.udpRegistered:
				return False
		return True

	def checkLoaded(self):
		if not self.loading:
			return False
		for player in self.players:
			if not player.loaded:
				return False
		return True

	def checkFinished(self):
		if not self.started:
			return False
		totAlive = 0
		for player in self.players:
			if player.alive:
				totAlive += 1
			if totAlive > 1:
				return False
		return True
