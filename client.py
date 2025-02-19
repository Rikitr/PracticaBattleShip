import socket
import json

def main():
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect(("127.0.0.1", 65432))
    print("Conectado al servidor.")
    nombre = input("Ingresa tu nombre: ")
    
    while True:
        datos = json.loads(cliente.recv(1024).decode())
        
        if datos.get("action") == "place_ships":
            barcos = {
                "ship1": ["A1", "A2", "A3", "A4", "A5"], 
                "ship2": ["B1", "B2", "B3", "B4"], 
                "ship3": ["C1", "C2", "C3"], 
                "ship4": ["D1", "D2", "D3"], 
                "ship5": ["E1", "E2"]
                }
            cliente.send(json.dumps({"player": nombre, "ships": barcos}).encode())
        
        elif datos.get("status") == "turn":
            disparo = input("Ingresa tu disparo (Ej: A1): ").upper()
            cliente.send(json.dumps({"action": "shoot", "shoot": disparo}).encode())
        
        elif datos.get("status") in ["turn_result", "receive_hit"]:
            print(datos["message"], "Hundido:" if "sunk_ship" in datos else "")
        
        elif datos.get("status") == "end":
            print("¡Ganaste!" if datos["win"] else "Perdiste.")
            break
    
    cliente.close()

if __name__ == "__main__":
    main()