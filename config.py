# ==============================================================================
# 📦 ARCHER — CENTRO DE CONFIGURACIÓN Y PRECIOS DE INSUMOS
# ==============================================================================
# Si suben los costos o cambiás tus parámetros comerciales, SOLO EDITÁS ESTE ARCHIVO.
# Todo el resto del sistema (Buscador, Cotizador, Calculadora, Ventas) se actualiza solo.

# 1. PRECIOS DE INSUMOS / PROVEEDORES
PRECIO_VELLON_KG      = 4900.0  # $ el kg de vellón siliconado
PRECIO_MICROFIBRA_M2  = 2700.0  # $ los 15.000 cm² de Microfibra
PRECIO_CORDURA_M2     = 3720.0  # $ los 15.000 cm² de Cordura
PRECIO_HOJA_A3        = 280.0   # $ por hoja tricapa A3
PRECIO_BOLETO         = 1500.0  # $ por boleto de colectivo

# 2. PARÁMETROS COMERCIALES DE ARCHER
MULTIPLICADOR_COSTO   = 2.3     # Multiplicador x2.3 sobre costo de producción
CANTIDAD_BOLETOS      = 2       # 2 boletos (Ida y vuelta = $3.000)
COMISION_ML = 0.143        # 14.3% Comisión por venta
COSTO_FIJO_ML = 2850.00    # $2.850 Costo fijo por unidad
COMISION_CUOTAS = 0.123    # 12.3% Costo por 6 cuotas sin interés

# 3. CÁLCULOS DERIVADOS UNIFICADOS (No hace falta modificar)
costo_gramo_vellon   = PRECIO_VELLON_KG / 1000.0
costo_cm2_microfibra = PRECIO_MICROFIBRA_M2 / 15000.0
costo_cm2_cordura    = PRECIO_CORDURA_M2 / 15000.0
costo_viaticos       = PRECIO_BOLETO * CANTIDAD_BOLETOS