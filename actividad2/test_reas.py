from router_fragmen import create_packet, parse_packet, fragment_IP_packet, reassemble_IP_packet
 
def probar(IP_packet_v1: bytes, MTU: int):
    fragment_list = fragment_IP_packet(IP_packet_v1, MTU)
    IP_packet_v2 = reassemble_IP_packet(fragment_list)
    print(f"paquete de {len(IP_packet_v1)} bytes, MTU {MTU} -> {len(fragment_list)} fragmento(s)")
    print("IP_packet_v1 = IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))
 
 
# Paquete IP armado con la estructura del header: IP 127.0.0.1, puerto 8885, TTL 10, ID 7, offset 0, FLAG 0
mensaje = b"Este es un mensaje de prueba bastante largo para poder fragmentarlo en varios trozos al pasar por enlaces con MTU pequeno."
IP_packet_v1 = create_packet({"ip": "127.0.0.1", "port": 8885, "ttl": 10, "id": 7,
                              "offset": 0, "flag": 0, "message": mensaje})
 
# Con los MTU de la red de 5 routers (50, 55, 80, 100, 140): algunos fragmentan y otros no
for MTU in (50, 55, 80, 100, 140, 200):
    probar(IP_packet_v1, MTU)
 
# Un paquete corto, que no necesita fragmentación
probar(create_packet({"ip": "127.0.0.1", "port": 8881, "ttl": 5, "id": 1, "offset": 0, "flag": 0, "message": b"hola"}), 50)
 
# Mismo test mostrando los fragmentos para el MTU 50
print("\nFragmentos con MTU 50:")
for f in fragment_IP_packet(IP_packet_v1, 50):
    p = parse_packet(f)
    print(f"   {len(f):2d} bytes | offset={p['offset']:3d} tamaño={p['size']:2d} flag={p['flag']} | {p['message']}")