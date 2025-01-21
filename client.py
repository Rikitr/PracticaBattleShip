import socket

server_host = "127.0.0.1"
server_port = 65432

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((server_host, server_port))
print("Cliente conectado!")
client.close()