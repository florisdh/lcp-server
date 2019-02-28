import sqlite3
import threading
from src.data import byteConverter as ByteConverter

class DataBaseConnection(object):
	"""SQLite database connection wrapper with application related setup. This database is used for managing user credentials."""

	def __init__(self):
		self.connection = None
		self.cursor = None
		self.lock = threading.Lock()

	def connect(self, relativeFileDir):
		self.connection = sqlite3.connect(relativeFileDir, check_same_thread=False)
		self.cursor = self.connection.cursor()

	def close(self):
		self.connection.close()

	def deleteTable(self):
		self.query("""
			DROP TABLE 'User_Credentials'
		""")

	def createTable(self):
		self.query("""
			CREATE TABLE 'User_Credentials' (
				ID INTEGER PRIMARY KEY AUTOINCREMENT,
				UserName TEXT NOT NULL,
				Password TEXT NOT NULL
			)
		""")

	def addUser(self, username, password):
		passwordHash = ByteConverter.encode_sha512(password)
		self.query("""
			INSERT INTO 'User_Credentials' (
				'UserName',
				'Password'
			) VALUES (
				'{0}',
				'{1}'
			)
		""".format(username, passwordHash))
		return self.cursor.lastrowid

	def checkUsernameTaken(self, username):
		rows = self.query("""
			SELECT * FROM 'User_Credentials'
			WHERE UserName = '{0}'
		""".format(username))
		return rows != None

	def validateUserCredentials(self, username, password):
		passwordHash = ByteConverter.encode_sha512(password)
		ids = self.query("""
			SELECT ID FROM 'User_Credentials'
			WHERE
				UserName = '{0}' AND
				Password = '{1}'
		""".format(username, passwordHash))
		return ids

	def commit(self):
		self.connection.commit()

	def query(self, queryString, fetch = "one"):
		self.waitForLock()
		try:
			self.cursor.execute(queryString)
		finally:
			self.releaseLock()

		if fetch == "all":
			return self.cursor.fetchall()
		elif fetch == "one":
			return self.cursor.fetchone()

	def waitForLock(self):
		self.lock.acquire()

	def releaseLock(self):
		self.lock.release()