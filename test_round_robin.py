from router import check_routes
 
print("R2 (v3), destino R5 (8885) x4 -> debe alternar R3 (8883) y R4 (8884):")
for _ in range(4):
    print("  ", check_routes("Rutas_R2_v3.txt", ("127.0.0.1", 8885)))
 
print("R2 (v3), destino R1 (8881): una sola ruta, siempre la misma:")
for _ in range(2):
    print("  ", check_routes("Rutas_R2_v3.txt", ("127.0.0.1", 8881)))
 
print("R3 (v3): dos áreas con contador propio. Intercalando R1 (8881) y R5 (8885):")
for dest in (8881, 8885, 8881, 8885, 8881, 8885):
    print(f"   dest {dest} ->", check_routes("Rutas_R3_v3.txt", ("127.0.0.1", dest)))
 
print("R2 (v4): intercalando R1 (8881, área R0/R1) y R5 (8885, área R3-R5):")
for dest in (8881, 8885, 8881, 8885, 8885, 8881, 8885):
    print(f"   dest {dest} ->", check_routes("Rutas_R2_v4.txt", ("127.0.0.1", dest)))