from src.packages.packages import TypedPackage
import src.data.byteConverter as ByteConverter

class PackageFactory:
	"""Packing and unpacking all packages according to right formats."""

	@staticmethod
	def Pack(type, data):
		if not data:
			return ByteConverter.uint8_to_bytes(type)
		else:
			return ByteConverter.uint8_to_bytes(type) + data.toBytes()

	@staticmethod
	def UnPack(data):
		return TypedPackage(ByteConverter.uint8_from_bytes(data[0:1]), data[1:])
		