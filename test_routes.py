from router import check_routes

casos = [
     # (archivo, destino, resultado esperado)
    ("rutas_R1_v2.txt", ("127.0.0.1", 8882), ("127.0.0.1", 8882)),  # R1 -> R2
    ("rutas_R1_v2.txt", ("127.0.0.1", 8883), ("127.0.0.1", 8882)),  # R1 -> R3 vía R2
    ("rutas_R1_v2.txt", ("127.0.0.1", 8881), None),                 # R1 -> R1: no está en su tabla
    ("rutas_R1_v2.txt", ("127.0.0.1", 8884), None),                 # fuera de la red
    ("rutas_R2_v2.txt", ("127.0.0.1", 8881), ("127.0.0.1", 8881)),  # R2 -> R1 (1ª línea)
    ("rutas_R2_v2.txt", ("127.0.0.1", 8883), ("127.0.0.1", 8883)),  # R2 -> R3 (2ª línea)
    ("rutas_R2_v2.txt", ("127.0.0.1", 8884), None),                 # fuera de la red
    ("rutas_R3_v2.txt", ("127.0.0.1", 8881), ("127.0.0.1", 8882)),  # R3 -> R1 vía R2
    ("rutas_R3_v2.txt", ("127.0.0.1", 8882), ("127.0.0.1", 8882)),  # R3 -> R2
    ("rutas_R3_v2.txt", ("127.0.0.1", 8884), None),                 # fuera de la red
    ("rutas_R3_v2.txt", ("10.0.0.1", 8881), None),                  # IP fuera de 127.0.0.0/24
]

good = True
for archivo, destino, esperando in casos:
    obtenido = check_routes(archivo, destino)
    ok = obtenido == esperando
    good = good and ok
    print(f"Archivo: {archivo}, Destino: {destino}, Esperando: {esperando}, Obtenido: {obtenido}, OK: {ok}")
    print("Todos tests pasados!" if good else "Algunos tests fallaron.")