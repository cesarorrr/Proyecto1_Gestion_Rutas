############################## CLASES ##############################

class Camion:
    """
    Representa un camión que transporta pedidos.

    Atributos:
        id_camion (int): Identificador único del camión.
        capacidad_restante (int): Capacidad restante del camión en unidades de carga.
        pedidos (list): Lista de pedidos asignados al camión.
        destinos (dict): Diccionario con destinos únicos como claves y sus coordenadas como valores.
        productos_asignados (set): Conjunto de nombres de productos asignados al camión.
    """
    def __init__(self, id_camion, capacidad):
        """
        Inicializa un camión con un ID único y una capacidad específica.
        
        Args:
            id_camion (int): Identificador del camión.
            capacidad (int): Capacidad total del camión.
        """
        self.id_camion = id_camion
        self.capacidad_restante = capacidad
        self.pedidos = []  # Lista para almacenar los pedidos asignados
        self.destinos = {}  # Diccionario para registrar los destinos y sus coordenadas
        self.productos_asignados = set()  # Conjunto para rastrear los productos transportados

    def agregar_pedido(self, id_pedido, nombre_producto, cantidad, destino, coordenadas, capacidad_camion):
        """
        Agrega un pedido al camión si hay suficiente capacidad disponible.
        
        Args:
            id_pedido (int): Identificador único del pedido.
            nombre_producto (str): Nombre del producto en el pedido.
            cantidad (int): Cantidad del producto en el pedido.
            destino (str): Dirección de entrega del pedido.
            coordenadas (str): Coordenadas del destino en formato "latitud, longitud".
        
        Returns:
            bool: True si el pedido fue agregado exitosamente, False si no hay capacidad suficiente.
        """
        if cantidad <= self.capacidad_restante and cantidad > 0:
            self.pedidos.append((id_pedido, nombre_producto, cantidad, destino))  # Agregar pedido
            self.capacidad_restante -= cantidad  # Actualizar capacidad restante
            self.destinos[destino] = coordenadas  # Registrar destino
            self.productos_asignados.add(nombre_producto)  # Agregar producto al conjunto
            return True, 0  # Pedido asignado correctamente
        
        elif cantidad > capacidad_camion and self.capacidad_restante == capacidad_camion:
            self.pedidos.append((id_pedido, nombre_producto, capacidad_camion, destino))  # Agregar pedido
            self.capacidad_restante = 0  # Actualizar capacidad restante
            self.destinos[destino] = coordenadas  # Registrar destino
            self.productos_asignados.add(nombre_producto)  # Agregar producto al conjunto
            return True, cantidad-capacidad_camion  # Pedido asignado correctamente

        return False, 0  # No se pudo agregar el pedido debido a falta de capacidad

class Pedido:
    """
    Representa un pedido realizado por un cliente.

    Atributos:
        id_pedido (int): Identificador único del pedido.
        coordenadas (str): Coordenadas de destino en formato "latitud, longitud".
        destino (str): Dirección del destino del pedido.
        id_producto (int): Identificador único del producto en el pedido.
        nombre_producto (str): Nombre del producto.
        cantidad (int): Cantidad solicitada del producto.
    """
    def __init__(self, id_pedido: int, coordenadas: str, destino: str, id_producto: int, nombre_producto: str, cantidad: int):
        """
        Inicializa un pedido con los detalles proporcionados.
        
        Args:
            id_pedido (int): Identificador único del pedido.
            coordenadas (str): Coordenadas de destino en formato "latitud, longitud".
            destino (str): Dirección de destino del pedido.
            id_producto (int): Identificador único del producto.
            nombre_producto (str): Nombre del producto en el pedido.
            cantidad (int): Cantidad del producto en el pedido.
        """
        self.id_pedido = id_pedido
        self.coordenadas = coordenadas
        self.destino = destino
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad

    def __str__(self):
        """
        Representación en cadena de un pedido para impresión.

        Returns:
            str: Detalles del pedido en formato legible.
        """
        return (
            f"Pedido #{self.id_pedido}:\n"
            f"  Producto: {self.nombre_producto} (ID: {self.id_producto})\n"
            f"  Cantidad: {self.cantidad}\n"
            f"  Coordenadas de recogida: {self.coordenadas}\n"
            f"  Destino: {self.destino}\n"
        )
