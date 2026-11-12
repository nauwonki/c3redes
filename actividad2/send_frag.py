import socket
import sys
import time

from router_fragmen import parse_packet

if len(sys.argv) < 4:
    print(__doc__)
    sys.exit(1)

fragmentos = dict(line.split() for line in open("fragmentos.txt") if line.strip())
destino = (sys.argv[1], int(sys.argv[2]))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
for etiqueta in sys.argv[3:]:
    data = bytes.fromhex(fragmentos[etiqueta])
    sock.sendto(data, destino)
    p = parse_packet(data)
    print(f"enviado {etiqueta}: ID {p['id']}, offset {p['offset']}, flag {p['flag']}")
    time.sleep(0.3)