from router_fragmen import parse_packet, create_packet

IP_packet_v1 = (b"\x7f\x00\x00\x01"      # IP 127.0.0.1
                + b"\x22\xb1"            # puerto 8881
                + b"\x0a"                # TTL 10
                + b"\x00\x00\x00\x07"    # ID 7
                + b"\x00\x00\x00\x00"    # offset 0
                + b"\x00\x00\x00\x04"    # tamaño 4
                + b"\x00"                # FLAG 0 (último fragmento)
                + b"hola")
parsed_IP_packet = parse_packet(IP_packet_v1)
IP_packet_v2 = create_packet(parsed_IP_packet)  
print("parsed:", parsed_IP_packet)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

IP_packet_v1 = (b"\x7f\x00\x00\x01" + b"\x22\xb5" + b"\x0a" + b"\x00\x00\x00\x07"
                + b"\x00\x00\x00\x1e" + b"\x00\x00\x00\x04" + b"\x01" + b"hola")
IP_packet_v2 = create_packet(parse_packet(IP_packet_v1))
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

IP_packet_v1 = (bytes([192, 168, 0, 10]) + (8882).to_bytes(2, "big") + bytes([255])
                + (4000000000).to_bytes(4, "big") + (70000).to_bytes(4, "big")
                + (17).to_bytes(4, "big") + b"\x00" + b"mensaje de prueba")
IP_packet_v2 = create_packet(parse_packet(IP_packet_v1))
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

IP_packet_v1 = (b"\x7f\x00\x00\x01" + b"\x22\xb1" + b"\x01" + b"\x00\x00\x00\x01"
                + b"\x00\x00\x00\x00" + b"\x00\x00\x00\x00" + b"\x00")
IP_packet_v2 = create_packet(parse_packet(IP_packet_v1))
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))

base = {"ip": "127.0.0.1", "port": 8881, "ttl": 5, "id": 1, "offset": 0, "flag": 0, "message": "x"}
for campo, valor in (("flag", 2), ("ttl", 256), ("id", 2**32), ("offset", -1), ("port", 70000)):
    try:
        create_packet({**base, campo: valor})
        print("ERROR: no falló con", campo, valor)
    except ValueError as e:
        print("ValueError esperado:", e)
for malo in (b"\x7f\x00\x00\x01" * 3,                   
             IP_packet_v1 + b"extra"):                  
    try:
        parse_packet(malo)
        print("ERROR: no falló")
    except ValueError as e:
        print("ValueError esperado:", e)