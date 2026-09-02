import pandas as pd

def buscar_producto(busqueda, ruta_csv='productos.csv'):
    """
    Busca un producto en productos.csv por su CÓDIGO exacto o por su NOMBRE.
    Retorna un diccionario con los datos del producto o None si no lo encuentra.
    """
    try:
        df = pd.read_csv(ruta_csv)
    except Exception as e:
        print(f"❌ Error al abrir {ruta_csv}: {e}")
        return None

    query = str(busqueda).strip().upper()

    # 1. Búsqueda exacta por la nueva columna CÓDIGO
    if 'codigo' in df.columns:
        coincidencia_codigo = df[df['codigo'].astype(str).str.upper() == query]
        if not coincidencia_codigo.empty:
            return coincidencia_codigo.iloc[0].to_dict()

    # 2. Búsqueda por NOMBRE (coincidencia parcial)
    coincidencia_nombre = df[df['producto'].astype(str).str.upper().str.contains(query, na=False)]
    if not coincidencia_nombre.empty:
        return coincidencia_nombre.iloc[0].to_dict()

    return None