class GamePlayer(object):
	"""Player game session information."""

	def __init__(self, client, spawnPointID, setup):
		self.client = client
		self.playerID = client.playerID
		self.playerName = client.userName
		self.spawnPointID = spawnPointID
		self.setup = setup
		self.loaded = False
		self.alive = False
