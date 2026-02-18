import threading
import time
import random

def descargar_archivo(nombre):
    print(f"Iniciando descarga: {nombre}")
    tiempo = random.randint(2, 5)
    time.sleep(tiempo)
    print(f"Descarga completada: {nombre} en {tiempo} segundos")

archivos = ["archivo1.zip", "archivo2.mp4", "archivo3.pdf"]

hilos = []

for archivo in archivos:
    hilo = threading.Thread(target=descargar_archivo, args=(archivo,))
    hilos.append(hilo)
    hilo.start()

for hilo in hilos:
    hilo.join()

print("Todas las descargas finalizaron.")
