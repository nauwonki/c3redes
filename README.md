# C3
## Actividad 2
Test 1: Primero compruebe que su código sigue manejando correctamente el TTL de paquetes y fragmentos, y que las rutas siguen alternándose según round-robin
Levantar 5 terminales:

```bash
python3 router_fragmen.py 127.0.0.1 8881 Rutas_R1_v3_mtu.txt
```
hasta 8885 Rutas_R5_v3 

Levantar 6to terminal:

```bash
python3 router_fragmen.py --send 127.0.0.1 8885 'hola!' 127.0.0.1 8881 10
```
Test 2: Pruebe sus routers usando un paquete IP de tamaño total 150 bytes. 
Levantar nuevamente las terminales y en el 6to terminal:

```bash
for i in {1..5}; do
    python3 router_fragmen.py --send 127.0.0.1 8885 "$(python3 -c 'print("A" * 130)')" 127.0.0.1 8881 10
    sleep 1
done
```