"""
🏥 HOSPITAL — Ejemplo de Programación Concurrente
==================================================

Conceptos demostrados:
  • threading.Event   → el director da la señal de apertura (NUEVO)
  • threading.Thread  → cada médico trabaja en su propio hilo
  • threading.Lock    → protege el registro de pacientes atendidos
  • thread.join()     → esperar a que todos los médicos terminen su turno
"""

import threading
import time
import random

# ──────────────────────────────────────────
# DATOS DEL HOSPITAL
# ──────────────────────────────────────────
MEDICOS = [
    {"nombre": "Dra. García",   "especialidad": "Cardiología",  "emoji": "👩‍⚕️"},
    {"nombre": "Dr. Ramírez",   "especialidad": "Pediatría",    "emoji": "👨‍⚕️"},
    {"nombre": "Dra. Torres",   "especialidad": "Neurología",   "emoji": "👩‍⚕️"},
    {"nombre": "Dr. Mendoza",   "especialidad": "Traumatología","emoji": "👨‍⚕️"},
]

PACIENTES_POR_MEDICO = 3

# ── EVENTO ────────────────────────────────────────────────────────────────────
# Un Event tiene dos estados: "apagado" (por defecto) y "encendido".
# Los hilos pueden llamar a .wait() para PAUSARSE hasta que el evento
# se encienda. El director llama a .set() para encenderlo y liberar a todos.
apertura_hospital = threading.Event()

# ── LOCK ──────────────────────────────────────────────────────────────────────
# Protege `registro` — recurso compartido entre los hilos de los médicos.
lock    = threading.Lock()
registro = []   # lista de atenciones completadas


# ──────────────────────────────────────────
# FUNCIÓN DEL DIRECTOR (hilo independiente)
# ──────────────────────────────────────────
def director():
    """
    El director espera unos segundos (revisión del hospital)
    y luego enciende el evento para que los médicos puedan atender.
    """
    print("  🏢 Director: revisando que todo esté listo...")
    time.sleep(2)   # simula la revisión previa a la apertura

    print("\n  🏢 Director: ¡HOSPITAL ABIERTO! Los médicos pueden atender.\n")

    # .set() enciende el evento → desbloquea todos los .wait() activos
    apertura_hospital.set()


# ──────────────────────────────────────────
# FUNCIÓN DE CADA MÉDICO (un hilo por médico)
# ──────────────────────────────────────────
def atender_pacientes(medico: dict):
    """Cada hilo espera la señal del director y luego atiende sus pacientes."""

    nombre       = medico["nombre"]
    especialidad = medico["especialidad"]
    emoji        = medico["emoji"]

    print(f"  {emoji} {nombre} ({especialidad}): esperando apertura...")

    # ── ESPERAR EL EVENTO ────────────────────────────────────────────
    # .wait() pausa este hilo hasta que apertura_hospital.set() sea llamado.
    # Todos los médicos están bloqueados aquí al mismo tiempo.
    apertura_hospital.wait()
    # ────────────────────────────────────────────────────────────────

    print(f"  {emoji} {nombre}: ¡recibí la señal! Comenzando consultas.")

    for i in range(1, PACIENTES_POR_MEDICO + 1):
        duracion = random.uniform(0.5, 1.5)
        time.sleep(duracion)   # simula la consulta médica

        # ── SECCIÓN CRÍTICA ──────────────────────────────────────────
        # Solo un hilo a la vez puede actualizar el registro.
        with lock:
            registro.append(f"{nombre} → Paciente {i}")
            print(f"  {emoji} {nombre}: atendió paciente {i}/{PACIENTES_POR_MEDICO} "
                  f"({duracion:.1f}s)  | Total atendidos hoy: {len(registro)}")
        # ── FIN SECCIÓN CRÍTICA ──────────────────────────────────────

    print(f"\n  {emoji} {nombre}: turno completado ✓\n")


# ──────────────────────────────────────────
# PROGRAMA PRINCIPAL
# ──────────────────────────────────────────
def main():
    print("=" * 55)
    print("   🏥 SIMULADOR DE HOSPITAL — threading.Event")
    print("=" * 55)
    print(f"\n  Médicos disponibles : {len(MEDICOS)}")
    print(f"  Pacientes por médico: {PACIENTES_POR_MEDICO}")
    print(f"  Total de atenciones : {len(MEDICOS) * PACIENTES_POR_MEDICO}")
    print("\n  ¿Cómo funciona?")
    print("  → Cada médico (hilo) espera con .wait()")
    print("  → El director llama a .set() y los desbloquea a todos\n")
    input("  Presiona ENTER para abrir el hospital... 🚪\n")

    # ── CREAR HILOS ──────────────────────────────────────────────────
    hilo_director = threading.Thread(target=director, name="Director")

    hilos_medicos = [
        threading.Thread(target=atender_pacientes, args=(m,), name=m["nombre"])
        for m in MEDICOS
    ]

    # ── LANZAR HILOS ─────────────────────────────────────────────────
    # Primero los médicos (quedarán bloqueados en .wait())
    for hilo in hilos_medicos:
        hilo.start()

    time.sleep(0.3)  # dar tiempo a que todos lleguen al .wait()

    # Luego el director (quien eventualmente llamará a .set())
    hilo_director.start()

    # ── ESPERAR A TODOS ───────────────────────────────────────────────
    hilo_director.join()
    for hilo in hilos_medicos:
        hilo.join()

    # ── RESUMEN ───────────────────────────────────────────────────────
    print("=" * 55)
    print("   📋 RESUMEN DEL TURNO")
    print("=" * 55)
    print(f"  Pacientes atendidos en total: {len(registro)}")
    print(f"  Estado del evento al cerrar: "
          f"{'🟢 activo' if apertura_hospital.is_set() else '🔴 apagado'}")
    print("\n  Conceptos usados:")
    print("   • threading.Event  → .wait() bloqueó los hilos hasta .set()")
    print("   • threading.Lock   → registro compartido sin conflictos")
    print("   • thread.join()    → esperamos a cada médico antes de imprimir")
    print("=" * 55)


if __name__ == "__main__":
    main()
