import socket
import threading

def handle_client(client_socket, addr):
    print(f"Cliente conectado desde {addr}")
    client_socket.send(b"Bienvenido al servidor!")
    client_socket.close()

def main():
    host = "127.0.0.1"  # Dirección del servidor (localhost)
    port = 65432        # Puerto del servidor
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(2)
    print("Servidor iniciado, esperando conexiones...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexión aceptada desde {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_handler.start()

if __name__ == "__main__":
    main()
