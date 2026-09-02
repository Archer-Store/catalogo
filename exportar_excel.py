import csv

# ==========================================
# ARCHER — EXPORTADOR A LISTA DE PRECIOS EXCEL
# ==========================================

archivo_entrada = 'productos.csv'
archivo_salida = 'lista_de_precios_archer.csv'

# Definición de costos base (mismos que en la calculadora)
PRECIO_VELLON_KG = 5000.0
PRECIO_MICROFIBRA_M2 = 2500.0
PRECIO_CORDURA_M2 = 3000.0
PRECIO_HOJA_A3 = 300.0
COSTO_VIATICOS = 1500.0
CANTIDAD_BOLETOS = 2

# Factores de precio
MULTIPLICADOR_SUGERIDO = 2.3
MULTIPLICADOR_ML = 1.27  # Comisión + envío aprox ML

productos_exportados = 0

with open(archivo_entrada, mode='r', encoding='utf-8') as f_in:
    lector = csv.DictReader(f_in)
    
    # Preparamos las columnas para el archivo de Excel
    columnas = [
        'Producto', 
        'Costo de Producción (ARS)', 
        'Precio Sugerido (ARS)', 
        'Precio MercadoLibre (ARS)'
    ]
    
    with open(archivo_salida, mode='w', newline='', encoding='utf-8-sig') as f_out:
        escritor = csv.DictWriter(f_out, fieldnames=columnas, delimiter=';')
        escritor.writeheader()
        
        for fila in lector:
            prod = fila['producto']
            vellon_g = float(fila['cant_vellon_g'])
            insumo_dir = float(fila['costo_insumo_directo'])
            micro_cm2 = float(fila['cm2_microfibra'])
            cordura_cm2 = float(fila['cm2_cordura'])
            hojas = float(fila['cant_hojas'])
            
            # Cálculos de costos
            c_vellon = (vellon_g / 1000.0) * PRECIO_VELLON_KG
            c_micro = (micro_cm2 / 10000.0) * PRECIO_MICROFIBRA_M2
            c_cordura = (cordura_cm2 / 10000.0) * PRECIO_CORDURA_M2
            c_hojas = hojas * PRECIO_HOJA_A3
            
            costo_prod = c_vellon + insumo_dir + c_micro + c_cordura + c_hojas
            p_sugerido = (costo_prod * MULTIPLICADOR_SUGERIDO) + (COSTO_VIATICOS * CANTIDAD_BOLETOS)
            p_ml = p_sugerido * MULTIPLICADOR_ML
            
            # Escribimos la fila en el nuevo archivo
            escritor.writerow({
                'Producto': prod,
                'Costo de Producción (ARS)': f"{costo_prod:.2f}".replace('.', ','),
                'Precio Sugerido (ARS)': f"{p_sugerido:.2f}".replace('.', ','),
                'Precio MercadoLibre (ARS)': f"{p_ml:.2f}".replace('.', ',')
            })
            productos_exportados += 1

print("------------------------------------------------------------------")
print(f"🏛️ ARCHER — ¡Éxito! Se exportaron {productos_exportados} productos a '{archivo_salida}'.")
print("------------------------------------------------------------------")