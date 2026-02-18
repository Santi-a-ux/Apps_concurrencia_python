"""
🏃 CARRERA DE CORREDORES — Ejemplo de Programación Concurrente
==============================================================

Conceptos demostrados:
  • threading.Thread  → cada corredor corre en su propio hilo
  • threading.Lock    → protege el marcador de posiciones (sección crítica)
  • thread.join()     → esperar a que todos crucen la meta
"""

import threading
import time
import random

# ──────────────────────────────────────────
# DATOS DE LA CARRERA
# ──────────────────────────────────────────
CORREDORES = ["🧍 Ana", "🧍 Luis", "🧍 Marta", "🧍 Carlos", "🧍 Sofía"]
DISTANCIA  = 10   # pasos hasta la meta

# Lista de llegadas — RECURSO COMPARTIDO entre hilos
# Sin lock, dos hilos podrían escribir al mismo tiempo → datos corruptos
llegadas = []

# 🔒 Lock: solo UN hilo a la vez puede modificar `llegadas`
lock = threading.Lock()

# ──────────────────────────────────────────
# FUNCIÓN QUE EJECUTA CADA HILO (corredor)
# ──────────────────────────────────────────
def correr(nombre: str):
    """Cada hilo llama a esta función con su propio corredor."""

    for paso in range(1, DISTANCIA + 1):
        time.sleep(random.uniform(0.1, 0.4))   # velocidad aleatoria
        print(f"  {nombre}  paso {paso}/{DISTANCIA}")

    # ── SECCIÓN CRÍTICA ──────────────────────────────────────────────
    # Aquí usamos el lock porque `llegadas` es compartida entre hilos.
    # Sin esto, dos corredores podrían llegar "al mismo tiempo" y
    # registrarse con la misma posición → resultado incorrecto.
    with lock:
        posicion = len(llegadas) + 1
        llegadas.append(nombre)
        print(f"\n  ✅ {nombre} llegó en LUGAR #{posicion}\n")
    # ── FIN SECCIÓN CRÍTICA ──────────────────────────────────────────


# ──────────────────────────────────────────
# PROGRAMA PRINCIPAL
# ──────────────────────────────────────────
def main():
    print("=" * 50)
    print("   🏁 CARRERA — Programación Concurrente")
    print("=" * 50)
    print(f"\n  Corredores : {len(CORREDORES)}")
    print(f"  Distancia  : {DISTANCIA} pasos")
    print(f"  Cada uno corre en su propio HILO (en paralelo)\n")
    input("  Presiona ENTER para dar la salida... 🚦\n")

    # ── CREAR UN HILO POR CORREDOR ───────────────────────────────────
    hilos = []
    for nombre in CORREDORES:
        hilo = threading.Thread(target=correr, args=(nombre,))
        hilos.append(hilo)

    # ── LANZAR TODOS A LA VEZ (¡aquí empieza la concurrencia!) ───────
    inicio = time.time()
    print("  ¡FUERA! 🏃‍♂️🏃‍♀️\n")
    for hilo in hilos:
        hilo.start()

    # ── ESPERAR A QUE TODOS TERMINEN ─────────────────────────────────
    # join() bloquea el hilo principal hasta que cada hilo finalice.
    for hilo in hilos:
        hilo.join()

    # ── RESULTADOS ───────────────────────────────────────────────────
    duracion = time.time() - inicio
    print("=" * 50)
    print("   🏆 RESULTADOS FINALES")
    print("=" * 50)
    for i, nombre in enumerate(llegadas, 1):
        medalla = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, f"  {i}.")
        print(f"  {medalla}  {nombre}")

    print(f"\n  Tiempo total de carrera: {duracion:.2f}s")
    print("\n  (Sin concurrencia habría tardado ~"
          f"{DISTANCIA * 0.25 * len(CORREDORES):.1f}s)")
    print("=" * 50)


if __name__ == "__main__":
    main()
