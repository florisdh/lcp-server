# LC Pirates Multiplayer Server
Multiplayer server made in python for a simple pvp online pirate game. The game itself can be found on another repository [here](https://github.com/florisdh/LCPiratesOnline).

## Prerequisites
- Setup python 2.7.x on your machine from [here](https://www.python.org/downloads)
- Install the [pycryptodome](https://pypi.org/project/pycryptodome/) package

## Installing
- Clone the repository
- Start server using `py .` in the project folder
- Run the game client from this repository [here](https://github.com/florisdh/LCPiratesOnline)

## About
I made this project as a prove of concept to make a solid realtime multiplayer server in python. This project was made around 2016 and updated it recently to make it work with all recent updates.

### Accounts
Player accounts are managed with a simple SQLite database, which can be found in the [data folder](./data). This database can easilly be edited with any SQLite browser, accounts can also be made using the cli commands.

### Game connection
The game will connect to the server directly using a TCP connection and will need to do a custom handshake to make the connection secure.
#### Handshake
The game will setup and generate RSA credentials and share the public key with the server. This pipeline is secure but it's one-way and it slow. That's why the server will now generate a random key for AES encryption. The server will share this key using the RSA pipeline with the game client and now both parties can communicate securely.
#### Peer to Peer
For higher performance the game will also use a peer-to-peer setup between players. The server will share a random key with the game client, which the client has to send back to the server's UDP endpoint. This way the server will get the know UDP endpoint of the client, which is later shared with other players. When the game starts, the players will get eachothers UDP endpoints and are able to send communicate to eachother directly.

## Commands
After running the server, you can still communicate with the server in the same cli. There are some pre-defined commands which might be usefull during testing.
### Register a new user
```
register [username] [password]
```
### Checking online players
```
list players
```
### Getting a list of active rooms
```
list rooms
```
### Force save database
```
list rooms
```
### Stopping
```
exit
```

## Future ideas
- Setup tests
- Move to external login provider
- Destroy all data properly
