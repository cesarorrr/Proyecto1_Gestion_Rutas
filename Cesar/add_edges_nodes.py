import networkx as nx

def afegir_edges(grafico : nx.Graph, edges : dict[str, list]):
    """
    Add edges to nodes automatically.

    grafico: The nx.Graph where it will ad the edges

    edges: Dictionary composed by string as keys values and their connections passed as list
        Ex:
            {'Vilassar de Mar' : ['Cabrera','Premia de Mar','Cabrils']}

    """
    try:
        for edge in edges:
            for connexions in edges[edge]:
                grafico.add_edge(edge,connexions)
        return True
    except Exception as e:
        print(e)
        return False
    
    

def afegir_nodes(grafico : nx.Graph, nodes : list):
    """
    Add nodes to a Graph

    grafico: The nx.Graph where it will ad the edges 

    nodes: List of nodes that will be added to the Graph
        Ex: ['Vilassar de Mar', 'Cabrera','Premia de Mar','Cabrils']
    """
    try:
        for node in nodes:
            grafico.add_node(node)
        return True
    except Exception as e:
        print(e)
        return False