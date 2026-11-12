import math
from router_fragmen import create_packet, fragment_IP_packet, HEADER_SIZE


def paquete(largo_mensaje):
    return create_packet({"ip": "127.0.0.1", "port": 8885, "ttl": 10, "id": 7,
                          "offset": 0, "flag": 0, "message": bytes(largo_mensaje)})


def esperado(largo_mensaje, mtu):
    """Tamaño esperado de la lista: 1 si cabe; si no, ceil(largo del mensaje / (MTU - header))."""
    if HEADER_SIZE + largo_mensaje <= mtu:
        return 1
    return math.ceil(largo_mensaje / (mtu - HEADER_SIZE))


# --- Ejemplos concretos (tamaño total = 20 + mensaje)
print("tamaño del paquete | MTU | largo de la lista | esperado")
ejemplos = [
    (30, 50),    # paquete de 50  <= 50 -> 1
    (31, 50),    # paquete de 51  >  50 -> 2   (30 + 1)
    (100, 50),   # paquete de 120 >  50 -> 4   (30+30+30+10)
    (100, 55),   # 35 por fragmento     -> 3   (35+35+30)
    (100, 80),   # 60 por fragmento     -> 2   (60+40)
    (100, 100),  # paquete de 120 > 100 -> 2   (80+20)
    (100, 140),  # paquete de 120 <= 140 -> 1
    (500, 50),   # 30 por fragmento     -> 17
]
for largo, mtu in ejemplos:
    n = len(fragment_IP_packet(paquete(largo), mtu))
    print(f"{HEADER_SIZE + largo:18d} | {mtu:3d} | {n:17d} | {esperado(largo, mtu)}  {'OK' if n == esperado(largo, mtu) else 'FALLA'}")

# --- Barrido: todos los largos de mensaje de 0 a 400 con los MTU de la red (50, 55, 80, 100, 140)
fallas = 0
total = 0
for mtu in (50, 55, 80, 100, 140):
    for largo in range(0, 401):
        paq = paquete(largo)
        lista = fragment_IP_packet(paq, mtu)
        total += 1
        ok = len(lista) == esperado(largo, mtu) and len(lista) >= 1
        if len(paq) <= mtu:
            ok = ok and lista == [paq]          # cabe: lista de 1 elemento, el mismo paquete
        ok = ok and all(len(f) <= mtu for f in lista)
        if not ok:
            fallas += 1
            print("FALLA:", largo, mtu, len(lista))
print(f"\nBarrido: {total} combinaciones (largo de mensaje 0-400 x MTU 50/55/80/100/140), fallas: {fallas}")
print("Todos los tests pasaron" if fallas == 0 else "HAY TESTS FALLIDOS")