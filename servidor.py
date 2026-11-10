import json
import math
import socket
import threading
import time
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PORT = 5000
N_WORKERS = 6

# Los "workers": hilos reutilizables que ejecutan las tareas
pool = ThreadPoolExecutor(max_workers=N_WORKERS, thread_name_prefix="worker")


def ejecutar_tarea(tarea):
    """Se ejecuta dentro de un hilo worker."""
    tipo = tarea.get("tipo")

    if tipo == "mayusculas":
        resultado = str(tarea["texto"]).upper()
    elif tipo == "factorial":
        n = int(tarea["n"])
        if not 0 <= n <= 2000:
            raise ValueError("n debe estar entre 0 y 2000")
        resultado = str(math.factorial(n))
    elif tipo == "dormir":                      # simula una tarea lenta
        time.sleep(float(tarea.get("segundos", 1)))
        resultado = "terminada"
    else:
        raise ValueError(f"Tipo de tarea desconocido: {tipo}")

    return {"resultado": resultado, "worker": threading.current_thread().name}


def atender_cliente(conn, addr):
    """Un hilo por conexión: lee la tarea, la delega al pool y devuelve el resultado."""
    with conn, conn.makefile("rwb") as f:
        try:
            linea = f.readline()
            if not linea:
                return
            tarea = json.loads(linea)
            futuro = pool.submit(ejecutar_tarea, tarea)       # distribuye al worker
            respuesta = {"estado": "ok", **futuro.result(timeout=30)}
        except Exception as e:
            respuesta = {"estado": "error", "mensaje": str(e)}

        f.write((json.dumps(respuesta) + "\n").encode())
        f.flush()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen()
        print(f"Servidor escuchando en {HOST}:{PORT} con {N_WORKERS} workers")
        try:
            while True:
                conn, addr = srv.accept()
                threading.Thread(target=atender_cliente,
                                args=(conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nCerrando servidor...")
        finally:
            pool.shutdown(wait=False, cancel_futures=True)


if __name__ == "__main__":
    main()