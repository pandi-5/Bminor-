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

    # 🪄 ESTA ES LA MAGIA: Una función que sabe abrir listas dentro de listas
    def procesar_coleccion(rama_padre, nombre, coleccion):
        tipo = type(coleccion).__name__
        rama_coleccion = rama_padre.add(f"[blue]{nombre}[/blue] ({tipo})")
        
        for item in coleccion:
            if isinstance(item, (list, tuple)):
                # ¡Llamada recursiva! Si hay una lista adentro, la vuelve a abrir
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

# --- 2. Función para Graphviz (Imagen PNG) ---
def build_graphviz(node, dot, parent_id=None):
    node_id = str(uuid.uuid4())
    label = type(node).__name__

    # Creamos el nodo visual
    dot.node(node_id, label, shape="box", style="filled", fillcolor="lightblue")

    if parent_id:
        dot.edge(parent_id, node_id)

    for field, value in vars(node).items():
        if field == 'lineno':
            continue
            
        if isinstance(value, list):
            for item in value:
                if hasattr(item, "__dict__"):
                    build_graphviz(item, dot, node_id)
        elif hasattr(value, "__dict__"):
            build_graphviz(value, dot, node_id)
        else:
            # Para valores simples, creamos un nodo "hoja"
            leaf_id = str(uuid.uuid4())
            dot.node(leaf_id, f"{field}: {value}", shape="ellipse")
            dot.edge(node_id, leaf_id)

    return dot