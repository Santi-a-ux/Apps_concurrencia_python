"""
╔══════════════════════════════════════════════════════════════╗
║         SIMULADOR DE DESCARGAS CONCURRENTES                  ║
║         Demostración de programación concurrente en Python   ║
╚══════════════════════════════════════════════════════════════╝

Conceptos demostrados:
  - threading.Thread        → hilos paralelos
  - threading.Lock          → exclusión mutua (evitar condiciones de carrera)
  - concurrent.futures      → ThreadPoolExecutor para gestión de hilos
  - threading.Event         → señales entre hilos
  - time comparativo        → secuencial vs concurrente
"""

import threading
import time
import random
import concurrent.futures
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
ARCHIVOS = [
    {"nombre": "video_4K.mp4",       "tamaño_mb": 850},
    {"nombre": "dataset_ml.zip",     "tamaño_mb": 420},
    {"nombre": "backup_fotos.tar",   "tamaño_mb": 310},
    {"nombre": "musica_album.zip",   "tamaño_mb": 180},
    {"nombre": "documento_pdf.pdf",  "tamaño_mb":  45},
    {"nombre": "software_v2.exe",    "tamaño_mb": 220},
]

VELOCIDAD_MB_S = 120   # MB/s simulados (compartidos entre hilos)
ANCHO_BARRA   = 30     # caracteres de la barra de progreso

# ─────────────────────────────────────────────
# LOCK COMPARTIDO — evita que los prints se mezclen
# ─────────────────────────────────────────────
print_lock = threading.Lock()

# Estadísticas compartidas (protegidas por lock)
estadisticas = {"total_mb": 0, "archivos_completados": 0}
stats_lock = threading.Lock()


# ─────────────────────────────────────────────
# FUNCIÓN DE DESCARGA SIMULADA
# ─────────────────────────────────────────────
def descargar_archivo(archivo: dict, hilo_id: int, modo: str = "concurrente") -> dict:
    """
    Simula la descarga de un archivo.
    
    Técnicas de concurrencia usadas aquí:
      • threading.Lock → print_lock garantiza salida limpia sin mezcla
      • time.sleep()   → simula I/O (donde la concurrencia aporta más)
      • stats_lock     → actualización segura de estadísticas compartidas
    """
    nombre    = archivo["nombre"]
    tamaño    = archivo["tamaño_mb"]
    hilo_name = threading.current_thread().name  # nombre del hilo actual

    # Velocidad variable por hilo (simula red real)
    velocidad = VELOCIDAD_MB_S / (random.uniform(0.8, 1.5))
    duracion  = tamaño / velocidad

    inicio = time.time()

    with print_lock:
        color = _color_hilo(hilo_id)
        print(f"\n{color}  [{hilo_name}] ▶ Iniciando: {nombre} ({tamaño} MB)\033[0m")

    # Simular descarga en pasos
    pasos = 20
    for paso in range(1, pasos + 1):
        time.sleep(duracion / pasos)
        porcentaje = int((paso / pasos) * 100)
        bloques    = int((paso / pasos) * ANCHO_BARRA)
        barra      = "█" * bloques + "░" * (ANCHO_BARRA - bloques)
        velocidad_actual = tamaño * (paso / pasos) / (time.time() - inicio + 0.001)

        with print_lock:
            color = _color_hilo(hilo_id)
            print(
                f"\r{color}  [{hilo_name}] {nombre[:22]:<22} "
                f"[{barra}] {porcentaje:>3}% "
                f"({velocidad_actual:.1f} MB/s)\033[0m",
                end="", flush=True
            )

    tiempo_total = time.time() - inicio

    # Actualizar estadísticas (sección crítica protegida)
    with stats_lock:
        estadisticas["total_mb"]            += tamaño
        estadisticas["archivos_completados"] += 1

    with print_lock:
        color = _color_hilo(hilo_id)
        print(
            f"\r{color}  [{hilo_name}] {nombre[:22]:<22} "
            f"[{'█' * ANCHO_BARRA}] 100% ✓ "
            f"({tiempo_total:.2f}s)\033[0m"
        )

    return {"nombre": nombre, "tamaño": tamaño, "tiempo": tiempo_total}


# ─────────────────────────────────────────────
# COLORES ANSI para diferenciar hilos visualmente
# ─────────────────────────────────────────────
COLORES = [
    "\033[94m",  # azul
    "\033[92m",  # verde
    "\033[93m",  # amarillo
    "\033[95m",  # magenta
    "\033[96m",  # cian
    "\033[91m",  # rojo
]

def _color_hilo(hilo_id: int) -> str:
    return COLORES[hilo_id % len(COLORES)]


# ─────────────────────────────────────────────
# MODO SECUENCIAL (sin concurrencia)
# ─────────────────────────────────────────────
def modo_secuencial():
    print("\n\033[1m\033[97m" + "═" * 60)
    print("  MODO SECUENCIAL (sin concurrencia)")
    print("  Los archivos se descargan UNO A LA VEZ")
    print("═" * 60 + "\033[0m")

    estadisticas["total_mb"] = 0
    estadisticas["archivos_completados"] = 0
    resultados = []

    inicio = time.time()
    for i, archivo in enumerate(ARCHIVOS):
        res = descargar_archivo(archivo, i, modo="secuencial")
        resultados.append(res)

    tiempo_total = time.time() - inicio
    _mostrar_resumen("SECUENCIAL", resultados, tiempo_total)
    return tiempo_total


# ─────────────────────────────────────────────
# MODO CONCURRENTE con threading.Thread
# ─────────────────────────────────────────────
def modo_threads():
    print("\n\033[1m\033[97m" + "═" * 60)
    print("  MODO CONCURRENTE — threading.Thread")
    print("  Cada archivo se descarga en su PROPIO HILO")
    print("═" * 60 + "\033[0m")

    estadisticas["total_mb"] = 0
    estadisticas["archivos_completados"] = 0
    resultados = []
    resultados_lock = threading.Lock()

    def tarea(archivo, idx):
        res = descargar_archivo(archivo, idx)
        with resultados_lock:
            resultados.append(res)

    # ★ Crear y lanzar hilos
    hilos = []
    inicio = time.time()

    for i, archivo in enumerate(ARCHIVOS):
        hilo = threading.Thread(
            target=tarea,
            args=(archivo, i),
            name=f"Hilo-{i+1}",  # nombre descriptivo
            daemon=True
        )
        hilos.append(hilo)
        hilo.start()  # ← lanzar hilo

    # ★ Esperar a que TODOS los hilos terminen
    for hilo in hilos:
        hilo.join()

    tiempo_total = time.time() - inicio
    _mostrar_resumen("CONCURRENTE (threads)", resultados, tiempo_total)
    return tiempo_total


# ─────────────────────────────────────────────
# MODO CONCURRENTE con ThreadPoolExecutor
# ─────────────────────────────────────────────
def modo_pool():
    print("\n\033[1m\033[97m" + "═" * 60)
    print("  MODO POOL — concurrent.futures.ThreadPoolExecutor")
    print("  Pool de 3 hilos que procesan 6 archivos")
    print("═" * 60 + "\033[0m")

    estadisticas["total_mb"] = 0
    estadisticas["archivos_completados"] = 0

    inicio = time.time()

    # ★ ThreadPoolExecutor gestiona automáticamente el pool
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(descargar_archivo, archivo, i): archivo
            for i, archivo in enumerate(ARCHIVOS)
        }

        resultados = []
        for future in concurrent.futures.as_completed(futures):
            try:
                resultado = future.result()
                resultados.append(resultado)
            except Exception as e:
                archivo = futures[future]
                print(f"  Error descargando {archivo['nombre']}: {e}")

    tiempo_total = time.time() - inicio
    _mostrar_resumen("POOL (3 workers)", resultados, tiempo_total)
    return tiempo_total


# ─────────────────────────────────────────────
# RESUMEN FINAL
# ─────────────────────────────────────────────
def _mostrar_resumen(modo: str, resultados: list, tiempo_total: float):
    total_mb = sum(r["tamaño"] for r in resultados)
    throughput = total_mb / tiempo_total if tiempo_total > 0 else 0

    print("\n\033[1m\033[97m" + "─" * 60)
    print(f"  ✅ RESUMEN — {modo}")
    print("─" * 60 + "\033[0m")
    print(f"  Archivos descargados : {len(resultados)}")
    print(f"  Total transferido    : {total_mb} MB")
    print(f"  Tiempo total         : \033[1m{tiempo_total:.2f}s\033[0m")
    print(f"  Throughput promedio  : {throughput:.1f} MB/s")


# ─────────────────────────────────────────────
# COMPARACIÓN FINAL
# ─────────────────────────────────────────────
def mostrar_comparacion(t_seq, t_threads, t_pool):
    print("\n\033[1m\033[97m" + "═" * 60)
    print("  📊 COMPARACIÓN DE RENDIMIENTO")
    print("═" * 60 + "\033[0m")

    datos = [
        ("Secuencial",       t_seq,     "\033[91m"),
        ("Threads paralelos", t_threads, "\033[92m"),
        ("Pool (3 workers)", t_pool,    "\033[93m"),
    ]

    max_t = max(t_seq, t_threads, t_pool)
    for nombre, tiempo, color in datos:
        barra_len = int((tiempo / max_t) * 40)
        barra     = "█" * barra_len
        speedup   = t_seq / tiempo if tiempo > 0 else 0
        print(f"  {color}{nombre:<22} {barra:<40} {tiempo:.2f}s  (×{speedup:.1f})\033[0m")

    print()
    print("\033[1m  💡 Conceptos demostrados:\033[0m")
    print("   • threading.Thread    → hilos independientes por tarea")
    print("   • threading.Lock      → sección crítica (print / estadísticas)")
    print("   • ThreadPoolExecutor  → pool reutilizable con workers limitados")
    print("   • concurrent.futures  → manejo de resultados asincrónicos")
    print("   • thread.join()       → sincronización (esperar a todos)")
    print()


# ─────────────────────────────────────────────
# PUNTO DE ENTRADA
# ─────────────────────────────────────────────
def main():
    print("\033[1m\033[96m")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║      🔀 SIMULADOR DE CONCURRENCIA EN PYTHON              ║")
    print("║         threading · ThreadPoolExecutor · Lock            ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\033[0m  Iniciado: {datetime.now().strftime('%H:%M:%S')}")
    print(f"  Hilos disponibles: Python puede crear múltiples threads")
    print(f"  Archivos a descargar: {len(ARCHIVOS)}")

    print("\n\033[33m  [!] Comparando: secuencial vs threads vs pool...\033[0m")
    input("\n  Presiona ENTER para comenzar la demostración...\n")

    # 1. Secuencial
    t_seq = modo_secuencial()
    time.sleep(0.5)

    # 2. Threads en paralelo
    t_threads = modo_threads()
    time.sleep(0.5)

    # 3. Pool de workers
    t_pool = modo_pool()
    time.sleep(0.5)

    # Comparación final
    mostrar_comparacion(t_seq, t_threads, t_pool)


if __name__ == "__main__":
    main()
