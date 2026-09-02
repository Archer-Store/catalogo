import csv
import os
from datetime import datetime

# ==============================================================================
# ARCHER — REGISTRADOR DE VENTAS Y MÉTRICAS FINANCIERAS
# ==============================================================================

# Precios de proveedores (para cálculo automático de costo)
PRECIO_VELLON_KG      = 4900.0
PRECIO_MICROFIBRA_M2  = 2700.0
PRECIO_CORDURA_M2     = 3720.0
PRECIO_HOJA_A3        = 280.0
PRECIO_BOLETO         = 1500.0

MULTIPLICADOR_COSTO = 2.3
CANTIDAD_BOLETOS    = 2
COMISION_ML         = 0.15
COSTO_FIJO_ML       = 1500.0

costo_gramo_vellon   = PRECIO_VELLON_KG / 1000.0
costo_cm2_microfibra = PRECIO_MICROFIBRA_M2 / 15000.0
costo_cm2_cordura    = PRECIO_CORDURA_M2 / 15000.0
costo_viaticos       = PRECIO_BOLETO * CANTIDAD_BOLETOS

ARCHIVO_VENTAS = 'ventas.csv'

def inicializar_archivo_ventas():
    if not os.path.exists(ARCHIVO_VENTAS):
        with open(ARCHIVO_VENTAS, mode='w', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow(['Fecha', 'Producto', 'Cantidad', 'Canal', 'Precio Total ARS', 'Costo Total ARS', 'Ganancia Neta ARS'])

def cargar_catalogo():
    catalogo = []
    try:
        with open('productos.csv', mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                codigo = fila.get('codigo', '')
                nombre = fila['producto']
                
                costo_insumo = (float(fila['cant_vellon_g']) * costo_gramo_vellon) + float(fila['costo_insumo_directo'])
                costo_tela = (float(fila['cm2_microfibra']) * costo_cm2_microfibra) + (float(fila['cm2_cordura']) * costo_cm2_cordura)
                costo_hojas = float(fila['cant_hojas']) * PRECIO_HOJA_A3
                c_prod = costo_insumo + costo_tela + costo_hojas

                if c_prod > 0:
                    p_sug = (c_prod * MULTIPLICADOR_COSTO) + costo_viaticos
                    p_ml = (p_sug + COSTO_FIJO_ML) / (1 - COMISION_ML)
                else:
                    p_sug = 0.0
                    p_ml = 0.0

                catalogo.append({
                    'codigo': codigo,
                    'nombre': nombre,
                    'costo_unitario': c_prod,
                    'precio_efectivo': p_sug,
                    'precio_ml': p_ml
                })
    except FileNotFoundError:
        print("❌ Error: No se encontró 'productos.csv'.")
    return catalogo

def registrar_venta():
    catalogo = cargar_catalogo()
    if not catalogo:
        return

    print("\n" + "=" * 65)
    print("                🛒 ARCHER — REGISTRAR NUEVA VENTA")
    print("=" * 65)

    busqueda = input("🔎 Código o nombre del producto vendido: ").strip().lower()
    
    # Busca por CÓDIGO o por NOMBRE
    coincidencias = [
        p for p in catalogo 
        if busqueda in p['nombre'].lower() or busqueda in p['codigo'].lower()
    ]

    if not coincidencias:
        print("❌ Producto no encontrado.")
        return

    print("\nSeleccioná el producto:")
    for idx, prod in enumerate(coincidencias, start=1):
        tag_codigo = f"[{prod['codigo']}] " if prod['codigo'] else ""
        print(f" {idx}. {tag_codigo}{prod['nombre']}")

    try:
        sel = int(input("Número: "))
        if sel < 1 or sel > len(coincidencias):
            return
        prod_sel = coincidencias[sel - 1]

        cant = int(input(f"Cantidad de '{prod_sel['nombre']}': "))
        if cant <= 0:
            return

        print("\nCanal de venta / Método:")
        print(" 1. Directa (Efectivo / Transferencia)")
        print(" 2. Mercado Libre")
        opcion_canal = input("Opción (1 u 2): ").strip()

        if opcion_canal == '2':
            canal = "Mercado Libre"
            precio_unitario = prod_sel['precio_ml']
        else:
            canal = "Directa"
            precio_unitario = prod_sel['precio_efectivo']

        # Cálculos de la venta
        precio_total = precio_unitario * cant
        costo_total = prod_sel['costo_unitario'] * cant
        ganancia_neta = precio_total - costo_total
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

        # Guardar en ventas.csv
        with open(ARCHIVO_VENTAS, mode='a', newline='', encoding='utf-8') as f:
            escritor = csv.writer(f)
            escritor.writerow([fecha_actual, prod_sel['nombre'], cant, canal, f"{precio_total:.2f}", f"{costo_total:.2f}", f"{ganancia_neta:.2f}"])

        print("\n" + "-" * 65)
        print(f"✅ ¡VENTA REGISTRADA CON ÉXITO!")
        print(f"   • Producto: {cant}x {prod_sel['nombre']} ({canal})")
        print(f"   • Venta Total: ${precio_total:,.2f}")
        print(f"   • Costo Total: ${costo_total:,.2f}")
        print(f"   • Ganancia Neta: ${ganancia_neta:,.2f}")
        print("-" * 65)

    except ValueError:
        print("⚠️ Entrada no válida.")

def ver_reporte_financiero():
    if not os.path.exists(ARCHIVO_VENTAS):
        print("\n⚠️ Aún no hay ventas registradas.")
        return

    total_ingresos = 0.0
    total_costos = 0.0
    total_ganancia = 0.0
    total_unidades = 0
    cantidad_ventas = 0

    with open(ARCHIVO_VENTAS, mode='r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            cantidad_ventas += 1
            total_unidades += int(fila['Cantidad'])
            total_ingresos += float(fila['Precio Total ARS'])
            total_costos += float(fila['Costo Total ARS'])
            total_ganancia += float(fila['Ganancia Neta ARS'])

    print("\n" + "=" * 65)
    print("          🏛️ ARCHER — METRICAS Y RESUMEN FINANCIERO")
    print("=" * 65)
    print(f"📊 Registros de Venta:      {cantidad_ventas}")
    print(f"📦 Productos Vendidos:      {total_unidades} unidades")
    print(f"💵 Ingresos Totales (Caja): ${total_ingresos:,.2f}")
    print(f"🛠️ Costos de Producción:    ${total_costos:,.2f}")
    print("-" * 65)
    print(f"📈 GANANCIA NETA REAL:       ${total_ganancia:,.2f}")
    
    if total_ingresos > 0:
        margen_promedio = (total_ganancia / total_ingresos) * 100
        print(f"🎯 Margen de Ganancia:     {margen_promedio:.2f}%")
    print("=" * 65)

def menu():
    inicializar_archivo_ventas()
    while True:
        print("\n--- ARCHER SISTEMA DE VENTAS ---")
        print("1. Registrar una nueva venta")
        print("2. Ver reporte de ingresos y ganancia neta")
        print("0. Salir")
        opcion = input("Elegí una opción: ").strip()

        if opcion == '1':
            registrar_venta()
        elif opcion == '2':
            ver_reporte_financiero()
        elif opcion in ['0', 'salir', 'exit']:
            print("\n👋 ¡Hasta luego!\n")
            break

if __name__ == '__main__':
    menu()