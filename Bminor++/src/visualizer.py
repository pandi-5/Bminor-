from rich.tree import Tree
import uuid

# --- 1. Función para Rich (Consola) ---
def build_rich_tree(node, field_name=None):
    class_name = type(node).__name__
    
    if field_name:
        label = f"[blue]{field_name}[/blue]: [bold green]{class_name}[/bold green]"
    else:
        label = f"[bold green]{class_name}[/bold green]"
        
    tree = Tree(label)

    def procesar_coleccion(rama_padre, nombre, coleccion):
        tipo = type(coleccion).__name__
        rama_coleccion = rama_padre.add(f"[blue]{nombre}[/blue] ({tipo})")
        
        for item in coleccion:
            if isinstance(item, (list, tuple)):
                procesar_coleccion(rama_coleccion, "group", item)
            elif hasattr(item, "__dict__"):
                rama_coleccion.add(build_rich_tree(item))
            else:
                rama_coleccion.add(str(item))

    # Recorremos los atributos del nodo
    for field, value in vars(node).items():
        if field == 'lineno':
            continue
            
        if isinstance(value, (list, tuple)):
            # Usamos la nueva herramienta para cualquier lista o tupla
            procesar_coleccion(tree, field, value)
            
        elif hasattr(value, "__dict__"):
            tree.add(build_rich_tree(value, field_name=field))
            
        else:
            tree.add(f"[yellow]{field}[/yellow]: {value}")

    return tree

# --- 2. Función para Graphviz (Gráfico) ---
def build_graphviz(node, dot, parent_id=None, edge_label=None):
    node_id = str(uuid.uuid4())
    label = type(node).__name__

    # 1. Creamos el nodo visual (La caja azul)
    dot.node(node_id, label, shape="box", style="filled", fillcolor="lightblue")

    # 2. Conectamos con el padre (¡AQUÍ PONEMOS EL NOMBRE EN LA FLECHA!)
    if parent_id:
        if edge_label:
            # Si hay una etiqueta (ej. 'value', 'left'), la dibujamos en la línea
            dot.edge(parent_id, node_id, label=edge_label)
        else:
            dot.edge(parent_id, node_id)

    # 3. Recorremos los atributos del nodo
    for field, value in vars(node).items():
        if field == 'lineno':
            continue
            
        if isinstance(value, list):
            for i, item in enumerate(value):
                if hasattr(item, "__dict__"):
                    # TRUCO PRO: Si es una lista, le ponemos el índice a la flecha
                    # Ejemplo: 'statements[0]', 'statements[1]'
                    build_graphviz(item, dot, node_id, edge_label=f"{field}[{i}]")
                    
        elif hasattr(value, "__dict__"):
            # Si el valor es otro nodo, le pasamos el nombre del atributo a la recursividad
            build_graphviz(value, dot, node_id, edge_label=field)
            
        else:
            # 4. Para valores simples (hojas)
            # La flecha lleva el nombre del atributo, y el óvalo lleva SOLO el valor
            leaf_id = str(uuid.uuid4())
            dot.node(leaf_id, str(value), shape="ellipse")
            dot.edge(node_id, leaf_id, label=field)

    return dot