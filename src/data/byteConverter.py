import sys
import binascii
import struct
from Crypto.Hash import SHA512

def bool_from_bytes(data):
	return uint8_from_bytes(data) == 1

def bool_to_bytes(data):
	return uint8_to_bytes(1 if data else 0)

def string_from_bytes(data):
	return data.decode("utf-8")

def string_to_bytes(data):
	return data.encode("utf-8")

def uint8_from_bytes(data):
	return int(struct.unpack("B", bytes(data))[0])

def uint8_to_bytes(data):
	return bytes(struct.pack("B", data))

def uint16_from_bytes(data):
	return int(struct.unpack("H", bytes(data))[0])

def uint16_to_bytes(data):
	return bytes(struct.pack("H", data))

def int32_from_bytes(data):
	return int(struct.unpack("<i", bytes(data[0:4]))[0])

def int32_to_bytes(data):
	return bytes(struct.pack("<i", data))

def variableSizedInt_from_bytes(data):
	return int(binascii.hexlify(data), 16)

def encode_sha512(data):
	hashEncoder = SHA512.new(string_to_bytes(data))
	return hashEncoder.hexdigest()

def encode_pkcs7(data, block_size):
	# Calc amount to pad
	padAmount = block_size - (len(data) % block_size)
	if padAmount == 0:
		padAmount = block_size

	# Select padding byte
	padByte = uint8_to_bytes(padAmount)

	# Apply on buffer
	dataBuffer = bytearray(data)
	for x in xrange(0,  padAmount):
		dataBuffer.append(padByte)

	return bytes(dataBuffer)
	