import os
import re
import requests
from urllib.parse import urlparse

def es_json_valido(response):
    """Verifica si la respuesta web es un JSON real y no una página HTML."""
    try:
        data = response.json()
        return data if isinstance(data, dict) else None
    except Exception:
        return None

def obtener_datos_shopify(url_usuario):
    """Prueba inteligentemente distintas rutas de Shopify para extraer los productos."""
    url_limpia = url_usuario.split("?")[0].rstrip("/")
    parsed = urlparse(url_limpia)
    base_domain = f"{parsed.scheme}://{parsed.netloc}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    # 1. Si pegaste un link directo a un producto
    if "/products/" in url_limpia and not url_limpia.endswith("/products"):
        url_json = f"{url_limpia}.json"
        res = requests.get(url_json, headers=headers, timeout=10)
        data = es_json_valido(res)
        if data and "product" in data:
            return [data["product"]]

    # 2. Si pegaste una colección específica
    if "/collections/" in url_limpia:
        url_json = f"{url_limpia}/products.json?limit=250"
        res = requests.get(url_json, headers=headers, timeout=10)
        data = es_json_valido(res)
        if data and "products" in data:
            return data["products"]

    # 3. Probar los catálogos globales estándar de Shopify
    endpoints_a_probar = [
        f"{base_domain}/collections/all/products.json?limit=250",
        f"{base_domain}/products.json?limit=250"
    ]

    for endpoint in endpoints_a_probar:
        try:
            res = requests.get(endpoint, headers=headers, timeout=10)
            data = es_json_valido(res)
            if data and "products" in data and len(data["products"]) > 0:
                return data["products"]
        except Exception:
            continue

    return None

def descargar_de_shopify(url_usuario, carpeta_salida="Disenos"):
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    print("🔍 Analizando sitio web...")

    productos = obtener_datos_shopify(url_usuario)

    if not productos:
        print("\n❌ Esta página no es compatible con el motor de Shopify (o tiene el catálogo privado).")
        print("💡 Recomendación: Para páginas no-Shopify (como Nin-Nin Game o Zerochan), usa la extensión ImageAssistant.")
        return

    print(f"\n📦 ¡Conectado con éxito! Se encontraron {len(productos)} producto(s). Descargando imágenes en HD...\n")

    descargados_totales = 0
    for prod in productos:
        titulo = prod.get("title", "sin_titulo")
        titulo_limpio = re.sub(r'[\\/*?:"<>|]', "", titulo).strip()
        images = prod.get("images", [])

        for idx, img in enumerate(images):
            img_url = img["src"]
            ext = img_url.split(".")[-1].split("?")[0]

            nombre_archivo = f"{titulo_limpio}_{idx+1}.{ext}"
            path_guardado = os.path.join(carpeta_salida, nombre_archivo)

            try:
                img_bytes = requests.get(img_url, headers=headers, timeout=10).content
                with open(path_guardado, "wb") as f:
                    f.write(img_bytes)

                descargados_totales += 1
                print(f"⬇️ [{descargados_totales}] Guardado: {nombre_archivo}")
            except Exception as e:
                print(f"⚠️ No se pudo descargar la imagen: {e}")

    print(f"\n🎉 ¡Listo! Se descargaron {descargados_totales} imágenes en la carpeta '{carpeta_salida}'.")

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 DESCARGADOR AUTOMÁTICO DE IMÁGENES HD (SHOPIFY)")
    print("=" * 60)

    while True:
        url_input = input("\n🔗 Pega la URL (o presiona ENTER para salir): ").strip()

        if not url_input:
            print("\n👋 ¡Hasta luego!")
            break

        descargar_de_shopify(url_input)
        print("\n" + "-" * 60)