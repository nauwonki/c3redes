from router import parse_packet, create_packet

IP_packet_v1 = b"\x7f\x00\x00\x01" + b"\x22\xb1" + b"\x05" + b"hola"
parsed_IP_packet = parse_packet(IP_packet_v1)
IP_packet_v2 = create_packet(parsed_IP_packet)  # create_packet ya retorna bytes
print("parsed:", parsed_IP_packet)
print("IP_packet_v1 == IP_packet_v2 ? {}".format(IP_packet_v1 == IP_packet_v2))