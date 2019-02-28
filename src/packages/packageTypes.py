
class PackageTypes:
	"""All types of packages which are sent in this server."""

	# General Packages
	Error = 0

	# Client Packages
	RequestSecureConnection = 8
	LoginAttempt = 9
	Logout = 10
	RegisterUDP = 11
	CreateRoom = 12
	RequestRooms = 13
	RequestJoin = 14
	LeaveRoom = 15
	ChangeSetup = 16
	GameLoaded = 17
	PlayerDied = 18

	# Server Packages
	SetupSecureConnection = 64
	LoginSucceed = 65
	LoginFailed = 66
	UDPRegistered = 67
	RoomCreated = 68
	JoinedRoom = 69
	RoomList = 70
	OtherJoinedRoom = 71
	OtherLeftRoom = 72
	OtherChangedSetup = 73
	RoomLoad = 74
	RoomStart = 75
	OtherDied = 76
	RoomFinished = 77
