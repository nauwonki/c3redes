import socket
import sys
import time

from router import create_packet

if len(sys.argv) not in (4, 5):
    print("Uso: python3 prueba_router.py 'IP;puerto;TTL' IP_router_inicial puerto_router_inicial [archivo]")
    sys.exit(1)

fields = sys.argv[1].split(";")
if len(fields) not in (2, 3):
    print("Error: los headers deben tener la forma 'IP;puerto;TTL' (el TTL es opcional)")
    sys.exit(1)
try:
    dest_ip = fields[0]
    dest_port = int(fields[1])
    ttl = int(fields[2]) if len(fields) == 3 else 255
    first_router = (sys.argv[2], int(sys.argv[3]))
except ValueError:
    print("Error: el puerto y el TTL deben ser enteros")
    sys.exit(1)

if len(sys.argv) == 5:
    try:
        source = open(sys.argv[4], encoding="utf-8")
    except OSError as e:
        print(f"Error: no se pudo abrir el archivo: {e}")
        sys.exit(1)
else:
    source = sys.stdin

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
enviados = 0
for line in source:
    line = line.rstrip("\r\n")
    if not line:  
        continue
    packet = create_packet({"ip": dest_ip, "port": dest_port, "ttl": ttl, "message": line})
    sock.sendto(packet, first_router)
    enviados += 1
    print(f"Enviado a {first_router}: {packet}")
    #time.sleep(0.05) 

sock.close()
if source is not sys.stdin:
    source.close()
print(f"{enviados} paquetes enviados con destino final ({dest_ip}, {dest_port}) y TTL {ttl}")