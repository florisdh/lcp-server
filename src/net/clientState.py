
class ClientState(object):
	"""Client state object containing all client meta."""

	def __init__(self, conn, addr, bufferSize = 1024):
		self.connection = conn
		self.address = addr
		self.bufferSize = bufferSize
		self.recvBuffer = bytearray(self.bufferSize)
		self.thread = None
		
		self.safeConnection = False
		self.cipher = None
		
		self.playerID = -1
		self.userName = ""
		self.logedIn = False

		self.inRoom = False
		self.room = None
		self.roomClient = None

		self.udpRegistered = False
		self.udpKey = None
		self.udpEP = None

	def close(self):
		self.connection.shutdown(socket.SHUT_RDWR)
		self.connection.close()
