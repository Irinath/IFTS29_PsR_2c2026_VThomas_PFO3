import json
import socket
from concurrent.futures import ThreadPoolExecutor

HOST = "127.0.0.1"
PORT = 5000


def enviar_tarea(tarea):
    """Envía una tarea y devuelve el resultado."""
    try:
        with socket.create_connection((HOST, PORT), timeout=35) as s:
            with s.makefile("rwb") as f:
                f.write((json.dumps(tarea) + "\n").encode())
                f.flush()
                return json.loads(f.readline())
    except OSError as e:
        return {"estado": "error", "mensaje": f"No se pudo conectar: {e}"}


if __name__ == "__main__":
    # Prueba secuencial
    for t in [{"tipo": "mayusculas", "texto": "hola mundo"},
                {"tipo": "factorial", "n": 20}]:
        print(t, "->", enviar_tarea(t))

    # Prueba de concurrencia: 16 tareas de 2 s contra 6 workers
    print("\nEnviando 16 tareas lentas a la vez...")
    with ThreadPoolExecutor(max_workers=8) as ex:
        for r in ex.map(enviar_tarea, [{"tipo": "dormir", "segundos": 2}] * 16):
            print(r)