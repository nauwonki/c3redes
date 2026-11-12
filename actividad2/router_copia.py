import socket
import sys
import ipaddress

HEADER_SIZE = 7

def parse_packet(IP_packet: bytes) -> dict:
    if len(IP_packet) < HEADER_SIZE:
        raise ValueError("Packet is too short to contain a valid header.")
    ip = ".".join(str(b) for b in IP_packet[0:4])
    port = int.from_bytes(IP_packet[4:6], byteorder='big')
    ttl = IP_packet[6]
    message = IP_packet[7:]
    return {"ip": ip, "port": port, "ttl": ttl, "message": message}

def create_packet(parsed_IP_packet: dict) -> bytes:
    parts = parsed_IP_packet["ip"].split(".")
    if len(parts) != 4:
        raise ValueError("Invalid IP address format.")
    ip_bytes = bytes(int(part) for part in parts)
    port_bytes = parsed_IP_packet["port"].to_bytes(2, byteorder='big')
    ttl = int(parsed_IP_packet["ttl"])
    if not 0 <= ttl <= 255:
        raise ValueError("TTL must be between 0 and 255.")
    ttl_byte = ttl.to_bytes(1, byteorder='big')
    message = parsed_IP_packet["message"]
    if isinstance(message, str):
        message = message.encode()
    return ip_bytes + port_bytes + ttl_byte + message

def send_message(ip_final: str, port_final: int, message: str, ip_envio: str, port_envio: int, ttl: int = 255):
    packet = create_packet({"ip": ip_final, "port": port_final, "ttl": ttl, "message": message})
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
            if len(fields) != 5:
                continue
            network, port_start, port_end, hop_id, hop_port = fields
            area = (ipaddress.ip_network(network, strict=False), int(port_start), int(port_end))
            routes.append((area, (hop_id, int(hop_port))))
        
    for area, _ in routes:
            network, port_start, port_end = area
            if dest_ip in network and int(port_start) <= dest_port <= int(port_end):
                next_hops = [hop for a, hop in routes if a == area]
                key = (routes_file_name, area)
                index = (route_counter.get(key, -1) + 1) % len(next_hops)
                route_counter[key] = index
                return next_hops[index]
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
                    print(f"Packet intended for this router: {packet}")
                else:
                    next_hop = check_routes(routes_file, destination_address)
                    if next_hop is None:
                        print(f"No route found for destination {destination_address}. Packet dropped.")
                    else:
                        print(f"Routing packet to next hop {next_hop} for destination {destination_address}.")
                        packet["ttl"] -= 1
                        sock.sendto(create_packet(packet), next_hop)
        except KeyboardInterrupt:
            print("Router shutting down.")
        finally:
            sock.close()
