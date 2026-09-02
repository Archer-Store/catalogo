import csv
from config import (
    costo_gramo_vellon,
    costo_cm2_microfibra,
    costo_cm2_cordura,
    costo_viaticos,
    PRECIO_HOJA_A3,
    PRECIO_BOLETO,
    MULTIPLICADOR_COSTO,
    CANTIDAD_BOLETOS,
    COMISION_ML,
    COSTO_FIJO_ML,
    COMISION_CUOTAS # <--- Agregamos la importación acá
)

# ... (resto de las impresiones en consola) ...

with open('productos.csv', mode='r', encoding='utf-8-sig') as archivo:
    primera_linea = archivo.readline()
    delimitador = ';' if ';' in primera_linea else ','
    archivo.seek(0)

    lector = csv.DictReader(archivo, delimiter=delimitador)
    
    for fila in lector:
        fila = {k.strip(): (v.strip() if v else v) for k, v in fila.items() if k}
        
        producto = fila['producto']
        costo_insumo = (float(fila['cant_vellon_g']) * costo_gramo_vellon) + float(fila['costo_insumo_directo'])
        costo_tela = (float(fila['cm2_microfibra']) * costo_cm2_microfibra) + (float(fila['cm2_cordura']) * costo_cm2_cordura)
        costo_hojas = float(fila['cant_hojas']) * PRECIO_HOJA_A3

        costo_produccion = costo_insumo + costo_tela + costo_hojas

        if costo_produccion > 0:
            precio_sugerido = (costo_produccion * MULTIPLICADOR_COSTO) + costo_viaticos
            
            # Sumamos las comisiones (14.3% + 12.3% = 26.6%)
            comision_total = COMISION_ML + COMISION_CUOTAS
            
            # Calculamos el precio final publicado para recibir intacto el 'precio_sugerido'
            precio_ml = (precio_sugerido + COSTO_FIJO_ML) / (1 - comision_total)
        else:
            precio_sugerido = 0.0
            precio_ml = 0.0

        print(f"{producto:<35} | ${costo_produccion:>8,.2f} | ${precio_sugerido:>28,.2f} | ${precio_ml:>14,.2f}")
        
print("=" * 105)
print(f"📌 Viáticos incluidos en Precio Sugerido: ${costo_viaticos:,.2f} ({CANTIDAD_BOLETOS} boletos x ${PRECIO_BOLETO:,.2f})")
print("=" * 105)