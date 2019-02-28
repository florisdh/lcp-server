class PlayerSetup(object):
	"""Player configurables from the setup screen."""

	def __init__(self, boatID, flagColorID, ready):
		self.boatID = boatID
		self.flagColorID = flagColorID
		self.ready = ready
