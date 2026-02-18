import multiprocessing
import time

def calcular(numero):
    print(f"Calculando cuadrado de {numero}")
    time.sleep(2)
    print(f"Resultado: {numero * numero}")

if __name__ == "__main__":
    procesos = []

    for i in range(1, 4):
        p = multiprocessing.Process(target=calcular, args=(i,))
        procesos.append(p)
        p.start()

    for p in procesos:
        p.join()

    print("Todos los cálculos terminaron.")
