import os
import sys
import subprocess

# ==============================================================================
# ARCHER — PANEL DE CONTROL PRINCIPAL
# ==============================================================================

def ejecutar_script(nombre_script):
    """Ejecuta cualquier script de la carpeta de forma aislada."""
    try:
        subprocess.run([sys.executable, nombre_script])
    except FileNotFoundError:
        print(f"\n❌ Error: No se encontró el archivo '{nombre_script}' en la carpeta actual.")
    except Exception as e:
        print(f"\n❌ Ocurrió un error al ejecutar '{nombre_script}': {e}")

def menu_principal():
    while True:
        print("\n" + "=" * 65)
        print("          🏛️ ARCHER — SISTEMA INTEGRAL DE GESTIÓN")
        print("=" * 65)
        print(" 1. 🔎 Buscador Rápido de Precios")
        print(" 2. 💬 Generador de Cotizaciones (WhatsApp / IG)")
        print(" 3. 🛒 Registro de Ventas y Finanzas")
        print(" 4. 📊 Exportar Lista de Precios a Excel")
        print(" 5. 📋 Ver Catálogo Completo (Calculadora de Costos)")
        print(" 0. 🚪 Salir")
        print("=" * 65)
        
        opcion = input("👉 Elegí una opción (0-5): ").strip()

        if opcion == '1':
            ejecutar_script("buscador.py")
        elif opcion == '2':
            ejecutar_script("cotizador.py")
        elif opcion == '3':
            ejecutar_script("ventas.py")
        elif opcion == '4':
            ejecutar_script("exportar_excel.py")
        elif opcion == '5':
            ejecutar_script("calculadora_catalogo.py")
        elif opcion in ['0', 'salir', 'exit']:
            print("\n👋 ¡Gracias por usar Archer! Hasta la próxima.\n")
            break
        else:
            print("\n⚠️ Opción no válida. Por favor elegí un número del 0 al 5.")

if __name__ == '__main__':
    menu_principal()