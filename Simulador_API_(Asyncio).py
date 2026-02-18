import asyncio
import random

async def consultar_api(nombre):
    print(f"Consultando API: {nombre}")
    tiempo = random.randint(1, 4)
    await asyncio.sleep(tiempo)
    print(f"Respuesta recibida de {nombre} en {tiempo} segundos")

async def main():
    await asyncio.gather(
        consultar_api("Servicio 1"),
        consultar_api("Servicio 2"),
        consultar_api("Servicio 3")
    )

asyncio.run(main())
