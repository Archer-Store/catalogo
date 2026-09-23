import json
import os
import sys
import urllib.parse
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

# Configuración y rutas
DB_NAME = "archer.db"
WHATSAPP_NUMBER = "5491168031083"

def obtener_productos_db():
    """Obtiene los productos directamente desde SQLite (archer.db) combinado con los diseños locales"""
    productos = []
    
    if not os.path.exists(DB_NAME):
        print("[ERROR] No se encontró la base de datos archer.db")
        return productos

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Intentar obtener de disenos_locales si existe, o de productos
    try:
        cursor.execute("SELECT franquicia, personaje, ruta_archivo FROM disenos_locales")
        disenos = cursor.fetchall()
    except:
        disenos = []

    # Obtener también matriz de precios de productos.csv / tabla productos
    precios_map = {}
    try:
        cursor.execute("SELECT codigo, producto, precio_sugerido, precio_ml FROM productos")
        for row in cursor.fetchall():
            codigo, prod_nombre, p_sug, p_ml = row
            # Asociar por nombre normalizado
            precios_map[prod_nombre.lower()] = {
                "precio_transf": p_sug or 17000,
                "precio_meli": p_ml or 27055,
                "link_meli": ""
            }
    except Exception as e:
        print(f"Aviso al leer precios de DB: {e}")

    conn.close()

    # Si hay diseños locales escaneados, armar el catálogo dinámico con ellos
    if disenos:
        for franq, personaje, ruta in disenos:
            # Formatear título profesional
            titulo_limpio = f"Dakimakura - {personaje.replace('_', ' ').title()}"
            
            # Buscar precio base de dakimakura 90cm
            precio_t = 17000.0
            precio_m = 27055.0
            for k, v in precios_map.items():
                if "dakimakura" in k:
                    precio_t = v["precio_transf"]
                    precio_m = v["precio_meli"]
                    break

            # Imagen (asegurar ruta web)
            foto_url = ruta if ruta.startswith("http") else f"./{ruta}"

            # Mensaje para WhatsApp destacando el beneficio por transferencia
            msg_wsp = f"¡Hola ARCHER! Quiero encargar la Dakimakura de {personaje} ({franq}). Aprovecho el precio especial por transferencia directa."
            wsp_url = f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(msg_wsp)}"

            productos.append({
                "personaje": personaje.replace('_', ' ').title(),
                "franquicia": franq,
                "categoria": "Dakimakura",
                "precio_transf": precio_t,
                "precio_meli": precio_m,
                "link_meli": "",
                "link_wsp": wsp_url,
                "destacado": True if "kafka" in personaje.lower() else False,
                "fotos": [foto_url]
            })
    else:
        # Fallback si no hay diseños escaneados, usar tabla productos
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, producto, precio_sugerido, precio_ml FROM productos")
        for row in cursor.fetchall():
            codigo, prod_nombre, p_sug, p_ml = row
            productos.append({
                "personaje": prod_nombre,
                "franquicia": "General",
                "categoria": "Merchandising",
                "precio_transf": p_sug or 5000,
                "precio_meli": p_ml or 10000,
                "link_meli": "",
                "link_wsp": f"https://wa.me/{WHATSAPP_NUMBER}?text={urllib.parse.quote(f'Hola ARCHER! Me interesa {prod_nombre}')}",
                "destacado": False,
                "fotos": ["https://via.placeholder.com/400x600?text=ARCHER+Merch"]
            })
        conn.close()

    return productos


def generar_html(productos):
    json_data = json.dumps(productos, ensure_ascii=False)

    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARCHER - Anime & Merch Collectibles</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }}
        body {{ background-color: #0d0714; color: #ffffff; padding-bottom: 40px; }}
        
        header {{ text-align: center; padding: 30px 15px; background: linear-gradient(180deg, #190d28 0%, #0d0714 100%); border-bottom: 1px solid #2a1645; }}
        header h1 {{ font-size: 2.4rem; color: #ffffff; letter-spacing: 3px; font-weight: 800; text-transform: uppercase; }}
        header p {{ color: #a68ec3; font-size: 1rem; margin-top: 5px; }}
        
        .controls {{ max-width: 1100px; margin: 25px auto; padding: 0 15px; display: flex; flex-direction: column; gap: 15px; }}
        .search-bar {{ width: 100%; padding: 14px 20px; background: #190d28; border: 1px solid #331b52; border-radius: 30px; color: #fff; font-size: 1rem; outline: none; transition: 0.3s; }}
        .search-bar:focus {{ border-color: #00ff87; box-shadow: 0 0 15px rgba(0, 255, 135, 0.3); }}
        
        .filters {{ display: flex; gap: 10px; overflow-x: auto; padding-bottom: 5px; scrollbar-width: none; }}
        .filters::-webkit-scrollbar {{ display: none; }}
        .filter-btn {{ background: #190d28; border: 1px solid #331b52; color: #a68ec3; padding: 8px 18px; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer; white-space: nowrap; transition: 0.3s; }}
        .filter-btn.active, .filter-btn:hover {{ background: #00ff87; color: #0d0714; border-color: #00ff87; font-weight: bold; }}
        
        .grid {{ max-width: 1100px; margin: 0 auto; display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; padding: 0 15px; }}
        @media (min-width: 768px) {{ .grid {{ grid-template-columns: repeat(4, 1fr); gap: 20px; }} }}
        
        .card {{ background: #190d28; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); display: flex; flex-direction: column; position: relative; }}
        .card:hover {{ transform: translateY(-5px); border-color: #00ff87; box-shadow: 0 10px 25px rgba(0, 255, 135, 0.2); z-index: 2; }}
        
        .badge {{ position: absolute; top: 10px; left: 10px; background: #00ff87; color: #0d0714; font-size: 0.7rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; z-index: 3; text-transform: uppercase; }}
        .franq-tag {{ position: absolute; top: 10px; right: 10px; background: rgba(137, 87, 229, 0.85); color: #fff; font-size: 0.65rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; z-index: 3; max-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        
        .carousel {{ position: relative; width: 100%; aspect-ratio: 1 / 2; overflow: hidden; background: #000; }}
        .carousel img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }}
        .card:hover .carousel img {{ transform: scale(1.05); }}
        
        .card-body {{ padding: 14px; display: flex; flex-direction: column; flex-grow: 1; }}
        .title {{ font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 4px; line-height: 1.3; }}
        .sub {{ font-size: 0.75rem; color: #a68ec3; margin-bottom: 12px; }}
        
        .prices {{ margin-top: auto; margin-bottom: 12px; background: rgba(0,0,0,0.2); padding: 8px; border-radius: 8px; }}
        .price-wsp {{ font-size: 1.15rem; font-weight: 800; color: #00ff87; }}
        .price-wsp-label {{ font-size: 0.65rem; color: #a68ec3; text-transform: uppercase; letter-spacing: 0.5px; }}
        
        .btn-group {{ display: flex; flex-direction: column; gap: 8px; }}
        .btn {{ width: 100%; padding: 11px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; border: none; cursor: pointer; text-decoration: none; text-align: center; display: inline-block; transition: 0.2s; }}
        .btn-meli {{ background: #ffe600; color: #000; }}
        .btn-meli:hover {{ background: #ffd000; }}
        .btn-wsp {{ background: #00ff87; color: #0d0714; }}
        .btn-wsp:hover {{ background: #00cc6a; box-shadow: 0 0 12px rgba(0, 255, 135, 0.4); }}
    </style>
</head>
<body>

    <header>
        <h1>ARCHER</h1>
        <p>Anime & Merch Collectibles</p>
    </header>

    <div class="controls">
        <input type="text" id="searchInput" class="search-bar" placeholder="Buscar por personaje, anime o franquicia..." oninput="renderProductos()">
        <div class="filters" id="filterContainer">
            <button class="filter-btn active" onclick="filtrarCategoria('Todos', this)">Todos</button>
            <button class="filter-btn" onclick="filtrarCategoria('Dakimakura', this)">Dakimakuras</button>
            <button class="filter-btn" onclick="filtrarCategoria('Reloj', this)">Relojes</button>
            <button class="filter-btn" onclick="filtrarCategoria('Almohada', this)">Almohadas</button>
            <button class="filter-btn" onclick="filtrarCategoria('Taza', this)">Tazas</button>
        </div>
    </div>

    <div class="grid" id="productGrid"></div>

    <script>
        const productos = {json_data};
        let catActual = 'Todos';

        function filtrarCategoria(cat, btn) {{
            catActual = cat;
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            if(btn) btn.classList.add('active');
            renderProductos();
        }}

        function renderProductos() {{
            const grid = document.getElementById('productGrid');
            const search = document.getElementById('searchInput').value.toLowerCase().trim();
            grid.innerHTML = '';

            let count = 0;
            productos.forEach((p) => {{
                const matchCat = catActual === 'Todos' || p.categoria.toLowerCase() === catActual.toLowerCase();
                const matchSearch = p.personaje.toLowerCase().includes(search) || p.franquicia.toLowerCase().includes(search) || p.categoria.toLowerCase().includes(search);

                if (matchCat && matchSearch) {{
                    count++;
                    const card = document.createElement('div');
                    card.className = 'card';
                    
                    let badgeHTML = p.destacado ? `<div class="badge">🔥 Destacado</div>` : '';
                    let franqHTML = p.franquicia ? `<div class="franq-tag">${{p.franquicia}}</div>` : '';
                    let meliBtnHTML = p.link_meli ? `<a href="${{p.link_meli}}" target="_blank" class="btn btn-meli">Ver en MercadoLibre</a>` : '';

                    let precioTransfFmt = Number(p.precio_transf).toLocaleString('es-AR', {{ style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }});

                    card.innerHTML = `
                        ${{badgeHTML}}
                        ${{franqHTML}}
                        <div class="carousel">
                            <img src="${{p.fotos[0]}}" alt="${{p.personaje}}" loading="lazy">
                        </div>
                        <div class="card-body">
                            <div class="title">${{p.personaje}}</div>
                            <div class="sub">${{p.categoria}} — ${{p.franquicia}}</div>
                            
                            <div class="prices">
                                <div class="price-wsp-label">Precio por Transferencia</div>
                                <div class="price-wsp">${{precioTransfFmt}}</div>
                            </div>

                            <div class="btn-group">
                                <a href="${{p.link_wsp}}" target="_blank" class="btn btn-wsp">💬 Encargar por WhatsApp</a>
                                ${{meliBtnHTML}}
                            </div>
                        </div>
                    `;
                    grid.appendChild(card);
                }}
            }});

            if(count === 0) {{
                grid.innerHTML = `<div style="grid-column: 1 / -1; text-align: center; color: #a68ec3; padding: 40px;">No se encontraron productos para tu búsqueda.</div>`;
            }}
        }}

        // Render inicial al cargar la página
        renderProductos();
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✨ ¡Catálogo index.html generado y optimizado con éxito!")

if __name__ == "__main__":
    prods = obtener_productos_db()
    generar_html(prods)
