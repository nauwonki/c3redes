import socket
import sys
import ipaddress
import random

HEADER_SIZE = 20

def parse_packet(IP_packet: bytes) -> dict:
    if len(IP_packet) < HEADER_SIZE:
        raise ValueError("Packet is too short to contain a valid header.")
    ip = ".".join(str(b) for b in IP_packet[0:4])
    port = int.from_bytes(IP_packet[4:6], byteorder='big')
    ttl = IP_packet[6]
    packet_id = int.from_bytes(IP_packet[7:11], byteorder='big')
    offset = int.from_bytes(IP_packet[11:15], byteorder='big')
    size = int.from_bytes(IP_packet[15:19], byteorder='big')
    flag = IP_packet[19]
    message = IP_packet[20:]
    if len(message) != size:
        raise ValueError(f"Packet size mismatch: expected {size} bytes, got {len(message)} bytes.")
    return {"ip": ip, "port": port, "ttl": ttl, "id": packet_id, "offset": offset,
            "size": size, "flag": flag, "message": message}

def create_packet(parsed_IP_packet: dict) -> bytes:
    parts = parsed_IP_packet["ip"].split(".")
    if len(parts) != 4:
        raise ValueError("Invalid IP address format.")
    
    ip_bytes = bytes(int(part) for part in parts)
    port = int(parsed_IP_packet["port"])
    ttl = int(parsed_IP_packet["ttl"])
    packet_id = int(parsed_IP_packet["id"])
    offset = int(parsed_IP_packet["offset"])
    flag = int(parsed_IP_packet["flag"])

    if not 0 <= port <= 65535:
        raise ValueError("Port must be between 0 and 65535.")
    if not 0 <= ttl <= 255:
        raise ValueError("TTL must be between 0 and 255.")
    if not 0 <= packet_id <= 4294967295:
        raise ValueError("Packet ID must be between 0 and 4294967295.")
    if not 0 <= offset <= 4294967295:
        raise ValueError("Offset must be between 0 and 4294967295.")
    if flag not in (0, 1):
        raise ValueError("Flag must be either 0 or 1.")
    
    message = parsed_IP_packet["message"]
    if isinstance(message, str):
        message = message.encode()
    return (ip_bytes + port.to_bytes(2, byteorder="big") + ttl.to_bytes(1, byteorder="big") 
            + packet_id.to_bytes(4, byteorder="big") + offset.to_bytes(4, byteorder="big")
            + len(message).to_bytes(4, byteorder="big") + flag.to_bytes(1, byteorder="big")
            + message)

def fragment_IP_packet(IP_packet: bytes, MTU: int):
    if MTU is None or len(IP_packet) <= MTU:
        return [IP_packet]
    
    packet = parse_packet(IP_packet)
    max_data = MTU - HEADER_SIZE

    if max_data <= 0:
        raise ValueError("MTU is too small to accommodate the header.")
    message = packet["message"]
    fragments = []
    for i in range(0, len(message), max_data):
        fragment = dict(packet)
        fragment["message"] = message[i:i + max_data]
        fragment["offset"] = packet["offset"] + i
        is_last_fragment = (i + max_data) >= len(message)
        fragment["flag"] = packet["flag"] if is_last_fragment else 1
        fragments.append(create_packet(fragment))
    
    return fragments

def reassemble_IP_packet(fragment_list: list):
    if not fragment_list:
        return None
    
    parsed = [parse_packet(fragment) for fragment in fragment_list]

    first = parsed[0]
    for p in parsed:
        if p["id"] != first["id"]:
            raise ValueError("Fragments have different IDs.")
        if p["ip"] != first["ip"] or p["port"] != first["port"]:
            raise ValueError("Fragments have different source IP or port.")
        if p["port"] != first["port"]:
            raise ValueError("Fragments have different destination ports.")
    
    unique = {}
    for p in parsed:
        unique.setdefault((p["offset"], p["size"]), p)
    fragments = sorted(unique.values(), key=lambda x: x["offset"])

    if len(fragments) == 1 and fragments[0]["offset"] == 0 and fragments[0]["flag"] == 0:
        return create_packet(fragments[0])
    
    expected_offset = 0
    for p in fragments:
        if p["offset"] != expected_offset:
            return None
        expected_offset += p["size"]
    if fragments[-1]["flag"] != 0:
        return None
    if any(p["flag"] == 0 for p in fragments[:-1]):
        return None
    
    packet = dict(fragments[0])
    packet["message"] = b"".join(p["message"] for p in fragments)
    packet["offset"] = 0
    packet["flag"] = 0
    return create_packet(packet)

def send_message(ip_final: str, port_final: int, message: str, ip_envio: str, port_envio: int, ttl: int = 255):
    packet = create_packet({"ip": ip_final, "port": port_final, "ttl": ttl, "id": random.getrandbits(32),  
                            "offset": 0, "flag": 0, "message": message})
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet, (ip_envio, port_envio))
    sock.close()
    print(f"Sent message to {ip_final}:{port_final} from {ip_envio}:{port_envio}")

route_counter = {}

def check_routes(routes_file_name: str, destination_address: tuple[str, int]) -> tuple[str, int]:
    dest_ip, dest_port = destination_address
    dest_ip = ipaddress.ip_address(dest_ip)

    routes = []
    with open(routes_file_name) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            fields = line.split()
            if len(fields) not in (5, 6):
                continue
            network, port_start, port_end, hop_id, hop_port = fields[:5]
            mtu = int(fields[5]) if len(fields) == 6 else None
            area = (ipaddress.ip_network(network, strict=False), int(port_start), int(port_end))
            routes.append((area, ((hop_id, int(hop_port)), mtu)))
        
    for area, _ in routes:
            network, port_start, port_end = area
            if dest_ip in network and int(port_start) <= dest_port <= int(port_end):
                next_hops = [hop for a, hop in routes if a == area]
                key = (routes_file_name, area)
                index = (route_counter.get(key, -1) + 1) % len(next_hops)
                route_counter[key] = index
                next_hop_address, mtu = next_hops[index]
                return next_hop_address, mtu
    return None

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--send":
        if len(sys.argv) not in (7, 8):
            print("Usage: python3 router.py --send ip_final port_final message ip_envio port_envio [ttl]")
            sys.exit(1)
        try:
            port_final = int(sys.argv[3])
            port_envio = int(sys.argv[6])
            ttl = int(sys.argv[7]) if len(sys.argv) == 8 else 255
        except ValueError:
            print("Error: port_final and port_envio must be integers.")
            sys.exit(1)
        send_message(sys.argv[2], port_final, sys.argv[4], sys.argv[5], port_envio, ttl)
    else:
        if len(sys.argv) != 4:
            print("Usage: python3 router.py router_ip router_puerto router_rutas.txt")
            sys.exit(1)
        router_ip = sys.argv[1]
        try:
            router_port = int(sys.argv[2])
        except ValueError:
            print("Error: router_puerto must be an integer.")
            sys.exit(1)
        routes_file = sys.argv[3]

        print(f"Router IP: {router_ip}, Port: {router_port}, Routes file: {routes_file}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((router_ip, router_port))
        print(f"Router listening on {router_ip}:{router_port}")

        fragment_by_id = {}

        try:
            while True:
                data, addr = sock.recvfrom(1024)
                try:
                    packet = parse_packet(data)
                except ValueError as e:
                    print(f"Error parsing packet from {addr}: {e}")
                    continue
                if packet["ttl"] <= 0:
                    print(f"Se recibió paquete {data} con TTL 0")
                    continue

                destination_address = (packet["ip"], packet["port"])
                if destination_address == (router_ip, router_port):
                    fragment_by_id.setdefault(packet["id"], []).append(data)
                    print(f"Stored fragment for packet ID {packet['id']} (offset {packet['offset']}, "f"FLAG {packet['flag']}): {len(fragment_by_id[packet['id']])} fragments stored.")
                    try:
                        reassembled = reassemble_IP_packet(fragment_by_id[packet["id"]])
                    except ValueError as e:
                        print(f"Error reassembling packet ID {packet['id']}: {e}")
                        del fragment_by_id[packet["id"]]
                        continue
                    if reassembled is not None:
                        print(parse_packet(reassembled)["message"].decode(errors="replace"))
                        del fragment_by_id[packet["id"]]
                else:
                    route = check_routes(routes_file, destination_address)
                    if route is None:
                        print(f"No route found for destination {destination_address}. Packet dropped.")
                    else:
                        next_hop, mtu = route
                        print(f"Routing packet to next hop {next_hop} for destination {destination_address}.")
                        packet["ttl"] -= 1
                        for fragment in fragment_IP_packet(create_packet(packet), mtu):
                            sock.sendto(fragment, next_hop)
        except KeyboardInterrupt:
            print("Router shutting down.")
        finally:
            sock.close()
