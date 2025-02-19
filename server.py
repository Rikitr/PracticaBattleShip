import socket
import threading
import json

class ServidorBatallaNaval:
    def __init__(self, host="127.0.0.1", puerto=65432):
        self.servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servidor.bind((host, puerto))
        self.servidor.listen(2)
        self.clientes = []
        self.tableros = {}
        self.nombres = {}
        self.tamano_barcos = [5, 4, 3, 3, 2]
        self.turno_actual = 0

    def manejar_cliente(self, socket_cliente):
        if len(self.clientes) >= 2:
            socket_cliente.send(json.dumps({"status": "error", "message": "Servidor lleno."}).encode())
            socket_cliente.close()
            return
        
        self.clientes.append(socket_cliente)
        socket_cliente.send(json.dumps({"status": "connected", "message": "Esperando otro jugador..."}).encode())
        
        if len(self.clientes) == 2:
            self.iniciar_juego()

    def iniciar_juego(self):
        for cliente in self.clientes:
            cliente.send(json.dumps({"status": "start", "message": "El juego ha comenzado."}).encode())
            cliente.send(json.dumps({"action": "place_ships"}).encode())
        
        for i, cliente in enumerate(self.clientes):
            self.recibir_barcos(cliente, i)
        
        self.gestionar_turnos()

    def recibir_barcos(self, cliente, indice_jugador):
        while True:
            try:
                raw_data = cliente.recv(1024).decode()
                data = json.loads(raw_data)
                
                if "player" in data and "ships" in data:
                    self.nombres[indice_jugador] = data["player"]
                    if self.validar_barcos(data["ships"]):
                        self.tableros[indice_jugador] = data["ships"]
                        break
                    else:
                        cliente.send(json.dumps({"status": "error", "message": "Posicionamiento de barcos inválido."}).encode())
            except Exception as e:
                print(f"Error al recibir barcos: {e}")
                continue

    def validar_barcos(self, barcos):
        ocupados = set()
        for posiciones in barcos.values():
            if len(posiciones) not in self.tamano_barcos:
                return False
            for pos in posiciones:
                if pos in ocupados:
                    return False
                ocupados.add(pos)
            filas = {p[0] for p in posiciones}
            cols = {p[1:] for p in posiciones}
            if not (len(filas) == 1 or len(cols) == 1):
                return False
        return True

    def gestionar_turnos(self):
        while True:
            cliente = self.clientes[self.turno_actual]
            otro_cliente = self.clientes[1 - self.turno_actual]
            
            cliente.send(json.dumps({"status": "turn", "message": "Es tu turno."}).encode())
            try:
                raw_data = cliente.recv(1024).decode()
                data = json.loads(raw_data)
                
                if data.get("action") == "shoot":
                    posicion = data["shoot"]
                    acierto, barco_hundido = self.procesar_disparo(posicion, 1 - self.turno_actual)
                    
                    cliente.send(json.dumps({"status": "turn_result", "hit": acierto, "message": "¡Acertaste!" if acierto else "Fallaste.", "sunk_ship": barco_hundido}).encode())
                    otro_cliente.send(json.dumps({"status": "receive_hit", "hit": acierto, "shoot": posicion, "message": "¡Tocado!" if acierto else "Fallaste.", "sunk_ship": barco_hundido}).encode())
                    
                    if self.verificar_fin_juego(1 - self.turno_actual):
                        for c in self.clientes:
                            c.send(json.dumps({"status": "end", "win": c == cliente}).encode())
                        break
            except Exception as e:
                print(f"Error en el turno: {e}")
                break
            
            self.turno_actual = 1 - self.turno_actual

    def procesar_disparo(self, posicion, indice_oponente):
        barcos_oponente = self.tableros[indice_oponente]
        for barco, coordenadas in barcos_oponente.items():
            if posicion in coordenadas:
                coordenadas.remove(posicion)
                return True, barco if not coordenadas else None
        return False, None

    def verificar_fin_juego(self, indice_jugador):
        return all(len(coords) == 0 for coords in self.tableros[indice_jugador].values())

    def iniciar(self):
        print("Servidor esperando conexiones...")
        while len(self.clientes) < 2:
            socket_cliente, _ = self.servidor.accept()
            threading.Thread(target=self.manejar_cliente, args=(socket_cliente,)).start()

if __name__ == "__main__":
    ServidorBatallaNaval().iniciar()