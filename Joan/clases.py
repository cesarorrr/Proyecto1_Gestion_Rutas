############################## CLASES ##############################

class Camion():
    def __init__(self,id_camion:int, id_pedidos:list, destinos:dict, id_productos:list, cantidad:int):
        self.id_camion = id_camion
        self.id_pedidos = id_pedidos
        self.destinos = destinos # {"nombre":coordenadas}
        self.id_productos = id_productos
        self.cantidad = cantidad

    def to_dict(self):
        # Convert the object to a dictionary
        return {
            "id_camion": self.id_camion,
            "id_pedidos": self.id_pedidos,
            "destinos": self.destinos,
            "id_productos": self.id_productos,
            "cantidad": self.cantidad
    }

    def __str__(self):
            return (f"Camion ID: {self.id_camion}\n"
                    f"Pedidos: {', '.join(map(str, self.id_pedidos))}\n"
                    f"Destinos: {' | '.join(self.destinos)}\n"
                    f"Producto ID: {self.id_productos}\n"
                    f"Cantidad: {self.cantidad}")

class Pedido():
    def __init__(self, id_pedido:int, coordenadas:str, destino:str, id_producto:int, nombre_producto:str, cantidad:int):
        self.id_pedido = id_pedido
        self.coordenadas = coordenadas
        self.destino = destino
        self.id_producto = id_producto
        self.nombre_producto = nombre_producto
        self.cantidad = cantidad

    def __str__(self):
        return (
            f"Pedido #{self.id_pedido}:\n"
            f"  Producto: {self.nombre_producto} (ID: {self.id_producto})\n"
            f"  Cantidad: {self.cantidad}\n"
            f"  Coordenadas de recogida: {self.coordenadas}\n"
            f"  Destino: {self.destino}\n"
        )