import csv

# ==============================================================================
# ARCHER — GENERADOR DE COTIZACIONES PARA WHATSAPP / IG DM
# ==============================================================================

# Precios de proveedores
PRECIO_VELLON_KG      = 4900.0
PRECIO_MICROFIBRA_M2  = 2700.0
PRECIO_CORDURA_M2     = 3720.0
PRECIO_HOJA_A3        = 280.0
PRECIO_BOLETO         = 1500.0

# Parámetros comerciales
MULTIPLICADOR_COSTO = 2.3
CANTIDAD_BOLETOS    = 2
COMISION_ML         = 0.15
COSTO_FIJO_ML       = 1500.0

# Costos unitarios
costo_gramo_vellon   = PRECIO_VELLON_KG / 1000.0
costo_cm2_microfibra = PRECIO_MICROFIBRA_M2 / 15000.0
costo_cm2_cordura    = PRECIO_CORDURA_M2 / 15000.0
costo_viaticos       = PRECIO_BOLETO * CANTIDAD_BOLETOS

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
                    'p_efectivo': p_sug,
                    'p_ml': p_ml
                })
    except FileNotFoundError:
        print("❌ Error: No se encontró el archivo 'productos.csv'.")
    return catalogo

def generar_cotizacion():
    catalogo = cargar_catalogo()
    if not catalogo:
        return

    print("=" * 65)
    print("        🏛️ ARCHER — GENERADOR DE PRESUPUESTOS Y COTIZACIONES")
    print("=" * 65)

    nombre_cliente = input("👤 Nombre del cliente (opcional): ").strip()
    if not nombre_cliente:
        nombre_cliente = "Cliente"

    print("\n💳 Método de pago principal:")
    print(" 1. Transferencia / Efectivo (Precio Sugerido)")
    print(" 2. Mercado Libre / Tarjeta")
    opcion_pago = input("Seleccioná opción (1 o 2, por defecto 1): ").strip()
    es_ml = (opcion_pago == '2')

    carrito = []

    while True:
        print("\n" + "-" * 65)
        busqueda = input("🔎 Buscar por CÓDIGO o NOMBRE (o 'listo' para finalizar): ").strip().lower()

        if busqueda in ['listo', '0', 'fin']:
            break

        if not busqueda:
            continue

        # Busca coincidencias tanto en EL CÓDIGO como en EL NOMBRE
        coincidencias = [
            p for p in catalogo 
            if busqueda in p['nombre'].lower() or busqueda in p['codigo'].lower()
        ]

        if not coincidencias:
            print("❌ No se encontraron productos con ese código o nombre.")
            continue

        print("\nResultados encontrados:")
        for idx, prod in enumerate(coincidencias, start=1):
            precio = prod['p_ml'] if es_ml else prod['p_efectivo']
            tag_codigo = f"[{prod['codigo']}] " if prod['codigo'] else ""
            print(f" {idx}. {tag_codigo}{prod['nombre']} - ${precio:,.2f}")

        try:
            sel = int(input("\nEscribí el número del producto a agregar (0 para cancelar): "))
            if sel == 0 or sel > len(coincidencias):
                continue
            
            prod_seleccionado = coincidencias[sel - 1]
            cant = int(input(f"¿Cuántas unidades de '{prod_seleccionado['nombre']}'?: "))
            if cant <= 0:
                continue

            precio_unitario = prod_seleccionado['p_ml'] if es_ml else prod_seleccionado['p_efectivo']
            carrito.append({
                'nombre': prod_seleccionado['nombre'],
                'cantidad': cant,
                'precio_unitario': precio_unitario,
                'subtotal': precio_unitario * cant
            })
            print(f"✅ Agregado: {cant}x {prod_seleccionado['nombre']}")

        except ValueError:
            print("⚠️ Selección inválida.")

    if not carrito:
        print("\n⚠️ No agregaste ningún producto a la cotización.")
        return

    # Generación de la plantilla para enviar por mensaje
    total = sum(item['subtotal'] for item in carrito)
    metodo_texto = "Mercado Libre / Tarjeta" if es_ml else "Efectivo / Transferencia"

    print("\n" + "=" * 65)
    print("📋 COPIÁ Y PEGÁ EL SIGUIENTE TEXTO EN TU CHAT:")
    print("=" * 65 + "\n")

    mensaje = f"Hola {nombre_cliente}! 👋 Te paso el presupuesto detallado de *Archer* 🏛️:\n\n"
    for item in carrito:
        mensaje += f"▪️ {item['cantidad']}x {item['nombre']} -> ${item['subtotal']:,.2f}\n"

    mensaje += f"\n💰 *TOTAL ({metodo_texto}): ${total:,.2f}*\n"
    mensaje += "\n📌 *Condiciones:*"
    mensaje += "\n• Todos nuestros productos son de excelente calidad y confección artesanal."
    mensaje += "\n• Demora de producción aproximada: 3 a 5 días hábiles."
    mensaje += "\n\nQuedamos a tu disposición para confirmar tu pedido! 😊✨"

    print(mensaje)
    print("\n" + "=" * 65)

if __name__ == '__main__':
    generar_cotizacion()