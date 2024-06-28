import paramiko
import getpass
import time

def configure_router(hostname, username, password, commands):
    # Crear el cliente SSH
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Conectar al router
        ssh_client.connect(
            hostname,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            port=22  # Puerto SSH estándar
        )

        # Obtener el objeto Transport
        transport = ssh_client.get_transport()

        # Configurar cifrados
        ciphers = ['aes128-cbc', '3des-cbc', 'aes192-cbc', 'aes256-cbc']
        transport.get_security_options().ciphers = ciphers

        # Iniciar una sesión interactiva de shell
        remote_connection = ssh_client.invoke_shell()

        # Ejecutar comandos de configuración
        for command in commands:
            remote_connection.send(command + '\n')
            while not remote_connection.recv_ready():
                time.sleep(1)
            output = remote_connection.recv(65535).decode('utf-8')
            print(output)

        # Cerrar la conexión
        ssh_client.close()
    except Exception as e:
        print(f"Error: {e}")
def configure_interfaz(hostname,username,password):
    commands = [
        f"show ip interface brief",
        f"wr"
    ]
    configure_router(hostname,username,password,commands) 

def execute_single_command(hostname, username, password, command):
    # Función para ejecutar un solo comando en el router
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh_client.connect(
            hostname,
            username=username,
            password=password,
            look_for_keys=False,
            allow_agent=False,
            port=22
        )

        transport = ssh_client.get_transport()
        ciphers = ['aes128-cbc', '3des-cbc', 'aes192-cbc', 'aes256-cbc']
        transport.get_security_options().ciphers = ciphers

        stdin, stdout, stderr = ssh_client.exec_command(command)
        output = stdout.read().decode('utf-8')

        print(output)

        ssh_client.close()

    except Exception as e:
        print(f"Error: {e}")
    return output


def configure_ip_interface(hostname, username, password):
    print("Configuración de IP en una interfaz")

    output = execute_single_command(hostname, username, password, "show ip interface brief")
    interfaces_up, interfaces_unassigned = process_output(output)
    
    print("\nInterfaces disponibles para configurar:")
    for interface in interfaces_unassigned:
        print(interface)

    interface = input("Ingrese la interfaz a configurar (ej. FastEthernet0/0): ")
    ip_address = input("Ingrese la dirección IP (ej. 192.168.1.1): ")
    subnet_mask = input("Ingrese la máscara de subred (ej. 255.255.255.0): ")

    commands = [
        f"interface {interface}",
        f"ip address {ip_address} {subnet_mask}",
        "no shutdown"
    ]

    configure_router(hostname, username, password, commands)


def configure_ospf(hostname, username, password):
    print("Configuración de OSPF")

    # Solicitar datos específicos para OSPF
    router_id = input("Ingrese el Router ID para OSPF (ej. 3.3.3.3): ")
    area = input("Ingrese el número de área OSPF (ej. 0): ")

    # Obtener las interfaces disponibles directamente 
    interfaces_command = "show ip interface brief"
    interfaces_output = execute_single_command(hostname, username, password, interfaces_command)
    # Solicitar interfaces pasivas
    passive_interfaces = []
    while True:
        try:
            choice = input("\n\nIngrese el nombre de la interfaz pasiva para OSPF (o dejar en blanco para terminar): ")
            if choice == '':
                break
            passive_interfaces.append(choice)
        except ValueError:
            print("Ingrese un nombre de interfaz válido.")

    # Obtener la cantidad de redes a configurar para OSPF
    while True:
        try:
            num_networks = int(input("Ingrese la cantidad de redes a configurar para OSPF: "))
            if num_networks <= 0:
                print("Debe ingresar al menos una red.")
            else:
                break
        except ValueError:
            print("Ingrese un número válido.")

    # Solicitar la configuración para cada red
    networks = []
    for i in range(num_networks):
        print(f"\nConfiguración de red {i + 1}:")
        network = input("Ingrese la dirección de red para OSPF (ej. 192.168.3.0): ")
        wildcard_mask = input("Ingrese la máscara wildcard para la red (ej. 0.0.0.255): ")
        networks.append((network, wildcard_mask))

    # Construir los comandos para configurar OSPF en Cisco IOS
    commands = [
        f"configure terminal",
        f"router ospf 1",
        f"router-id {router_id}",
        f"area {area} authentication message-digest"
    ]
    
    for interface in passive_interfaces:
        commands.append(f"passive-interface {interface}")

    for network, wildcard_mask in networks:
        commands.append(f"network {network} {wildcard_mask} area {area}")

    # Llamar a la función para configurar el router
    configure_router(hostname, username, password, commands)

def configure_rip(hostname, username, password):
    print("Configuración de RIP")

    # Obtener la cantidad de redes a configurar
    while True:
        try:
            num_networks = int(input("Ingrese la cantidad de redes a configurar para RIP: "))
            if num_networks <= 0:
                print("Debe ingresar al menos una red.")
            else:
                break
        except ValueError:
            print("Ingrese un número válido.")

    # Solicitar la configuración para cada red
    networks = []
    for i in range(num_networks):
        print(f"\nConfiguración de red {i + 1}:")
        network = input("Ingrese la dirección de red (ej. 192.168.1.0): ")
        networks.append(network)

    # Construir los comandos para configurar RIP en Cisco IOS
    commands = [
        "configure terminal",
        "router rip"
    ]
    for network in networks:
        commands.extend([
            f"network {network}"
        ])

    # Agregar comando para mostrar interfaces disponibles al principio
    #commands.insert(0, "show ip interface brief")

    # Llamar a la función para configurar el router
    configure_router(hostname, username, password, commands)



def configure_eigrp(hostname, username, password):
    print("Configuración de EIGRP")
    autonomous_system = input("Ingrese el número de sistema autónomo EIGRP (ej. 100): ")
    network = input("Ingrese la dirección de red (ej. 192.168.1.0): ")

    # Comandos para configurar EIGRP en Cisco IOS
    commands = [
        f"router eigrp {autonomous_system}",
        f"network {network}",
        f"exit"
    ]

    configure_router(hostname, username, password, commands)




def show_information_menu(hostname, username, password):
    # Submenú para consultar información en el router
    while True:
        print("\nMenú de Consulta de Información:")
        print("1. Mostrar tabla de enrutamiento (show ip route)")
        print("2. Mostrar información de protocolos IP (show ip protocols)")
        print("3. Mostrar estado de las interfaces (show ip interface brief)")
        print("4. Mostrar configuración en ejecución (show running-config)")
        print("5. Ejecutar un solo comando")
        print("0. Volver al Menú Principal")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            execute_single_command(hostname, username, password, "show ip route")
        elif choice == '2':
            execute_single_command(hostname, username, password, "show ip protocols")
        elif choice == '3':
            execute_single_command(hostname, username, password, "show ip interface brief")
        elif choice == '4':
            execute_single_command(hostname, username, password, "show running-config")
        elif choice == '5':
            custom_command = input("Ingrese el comando que desea ejecutar: ")
            execute_single_command(hostname, username, password, custom_command)
        elif choice == '0':
            break
        else:
            print("Opción no válida. Por favor, seleccione nuevamente.")


def process_output(output):
    # Procesar la salida para mostrar solo las interfaces "up"
    lines = output.splitlines()
    interfaces_up = []
    interfaces_unassigned = []

    for line in lines:
        if line and not line.startswith("Interface"):
            interface_details = line.split()
            interface_name = interface_details[0]
            ip_address = interface_details[1]
            status = interface_details[-2]
            protocol = interface_details[-1]

            if status == "up" and protocol == "up":
                interfaces_up.append((interface_name, ip_address))
            elif ip_address == "unassigned":
                interfaces_unassigned.append(interface_name)

    return interfaces_up, interfaces_unassigned

def main():
    """
    hostname = input("Ingrese la dirección IP del router: ")
    username = input("Ingrese el nombre de usuario SSH: ")
    password = getpass.getpass("Ingrese la contraseña SSH (será oculta): ")
    """
    hostname = "192.168.1.100" 
    username = "maluja" 
    password = "diego"

    # Ejecutar el comando y obtener la salida
    command = "show ip interface brief"
    output = execute_single_command(hostname, username, password, command)
    
    if output:
        interfaces_up, interfaces_unassigned = process_output(output)
        
        print("\nInterfaces que están 'up' con sus direcciones IP:")
        for interface, ip in interfaces_up:
            print(f"{interface}: {ip}")

        print("\nInterfaces 'unassigned' disponibles para configurar:")
        for interface in interfaces_unassigned:
            print(interface)
    else:
        print("No se pudo obtener la salida del comando.")
    while True:
        print("\nMenú de Configuración de Enrutamiento Dinámico:")
        print("1. Configurar IP en una interfaz")
        print("2. Configurar RIP")
        print("3. Configurar OSPF")
        print("4. Configurar EIGRP")
        print("5. consultar informacion")
        print("0. Salir")

        choice = input("Seleccione una opción: ")

        if choice == '1':
            configure_ip_interface(hostname, username, password)
        elif choice == '2':
            configure_rip(hostname, username, password)
        elif choice == '3':
            configure_ospf(hostname, username, password)
        elif choice == '4':
            configure_eigrp(hostname, username, password)
        elif choice == '5':
            show_information_menu(hostname, username, password)
        elif choice == '0':
            break
        else:
            print("Opción no válida. Por favor, seleccione nuevamente.")

if __name__ == "__main__":
    main()
