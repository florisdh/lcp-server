import socket

class UDPClient(object):
	"""Simple UDP socket wrapper for client udp origin registration."""

	def __init__(self, hostIp, hostPort):
		self.hostIp = hostIp
		self.hostPort = hostPort
		self.isStarted = False
		self.receiveBuffer = bytearray(128)

	def start(self):
		self.hostConnection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.hostConnection.bind((self.hostIp, self.hostPort))

	def receive(self):
		(byteAmount, addr) = self.hostConnection.recvfrom_into(self.receiveBuffer)
		return (addr, self.receiveBuffer[0:byteAmount])
