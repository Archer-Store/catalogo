import json
import os
import sys
import urllib.parse
import requests
import sqlite3

sys.stdout.reconfigure(encoding='utf-8')

# Credenciales y configuración
NOTION_TOKEN = "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"
DATABASE_ID = "3c467edf6aa3804bb22eff38cf888fd0"
WHATSAPP_NUMBER = "5491168031083"
DB_NAME = "archer.db"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}

def obtener_precios_variantes():
    """Obtiene el diccionario exacto de variantes y precios desde SQLite"""
    variantes = {}
    if not os.path.exists(DB_NAME):
        return variantes
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, producto, precio_sugerido, precio_ml FROM productos WHERE codigo IN ('DAKI90S', 'DAKI90D', 'DAKIBUSTO', 'FDAKI90S', 'FDAKI90D', 'FU90S', 'FU90D')")
        for codigo, prod, p_sug, p_ml in cursor.fetchall():
            variantes[codigo] = {
                "nombre": prod,
                "precio_transf": p_sug or 17000.0,
                "precio_meli": p_ml or 27055.0
            }
        conn.close()
    except Exception as e:
        print(f"[AVISO] Error al leer variantes de SQLite: {e}")
    
    # Fallback si está vacío
    if not variantes:
        variantes = {
            "DAKI90S": {"nombre": "Dakimakura 90x30cm (Simple)", "precio_transf": 17000.0, "precio_meli": 27055.0},
            "DAKI90D": {"nombre": "Dakimakura 90x30cm (Doble)", "precio_transf": 20000.0, "precio_meli": 30565.0},
            "DAKIBUSTO": {"nombre": "Dakimakura Busto 60x30cm", "precio_transf": 11500.0, "precio_meli": 19560.0},
            "FDAKI90S": {"nombre": "Funda + Almohada 90cm Simple", "precio_transf": 19400.0, "precio_meli": 31440.0},
            "FDAKI90D": {"nombre": "Funda + Almohada 90cm Doble", "precio_transf": 22585.0, "precio_meli": 32990.0},
            "FU90S": {"nombre": "Solo Funda 90cm Simple", "precio_transf": 9000.0, "precio_meli": 16075.0},
            "FU90D": {"nombre": "Solo Funda 90cm Doble", "precio_transf": 12100.0, "precio_meli": 20460.0},
        }
    return variantes

def obtener_productos_notion():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        response = requests.post(url, headers=headers, timeout=20)
    except Exception as e:
        print(f"[ERROR] Excepción al conectar con Notion: {e}")
        return []

    if response.status_code != 200:
        print(f"[ERROR] Error al conectar con Notion ({response.status_code}): {response.text}")
        return []

    data = response.json()
    productos = []
    variantes_db = obtener_precios_variantes()

    for page in data.get("results", []):
        props = page["properties"]

        title_list = props.get("Personaje", {}).get("title", []) or props.get("Nombre", {}).get("title", [])
        personaje = title_list[0]["plain_text"] if title_list else "Producto"

        franq_prop = props.get("Franquicia", {})
        franquicia = "General"
        if franq_prop.get("type") == "select" and franq_prop.get("select"):
            franquicia = franq_prop["select"]["name"]

        cat_select = props.get("Categoría", {}).get("select", {})
        categoria = cat_select.get("name", "Dakimakura") if cat_select else "Dakimakura"

        link_meli = props.get("Link MeLi", {}).get("url") or ""
        destacado = props.get("Destacado", {}).get("checkbox", False)

        fotos = []
        cover = page.get("cover")
        if cover:
            if cover["type"] == "external":
                fotos.append(cover["external"]["url"])
            elif cover["type"] == "file":
                fotos.append(cover["file"]["url"])

        fotos_sec = props.get("Fotos Secundarias", {}).get("rich_text", [])
        if fotos_sec:
            urls = fotos_sec[0]["plain_text"].split(",")
            for u in urls:
                u_clean = u.strip()
                if u_clean and u_clean not in fotos:
                    fotos.append(u_clean)

        if not fotos:
            fotos = ["https://via.placeholder.com/400x600?text=ARCHER+Merch"]

        productos.append({
            "personaje": personaje,
            "franquicia": franquicia,
            "categoria": categoria,
            "link_meli": link_meli,
            "destacado": destacado,
            "fotos": fotos,
            "variantes": variantes_db
        })

    print(f"[INFO] Se obtuvieron {len(productos)} productos desde Notion.")
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
        
        .card {{ background: #190d28; border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); display: flex; flex-direction: column; position: relative; cursor: pointer; }}
        .card:hover {{ transform: translateY(-5px); border-color: #00ff87; box-shadow: 0 10px 25px rgba(0, 255, 135, 0.2); z-index: 2; }}
        
        .badge {{ position: absolute; top: 10px; left: 10px; background: #00ff87; color: #0d0714; font-size: 0.7rem; font-weight: 800; padding: 4px 10px; border-radius: 6px; z-index: 3; text-transform: uppercase; }}
        .franq-tag {{ position: absolute; top: 10px; right: 10px; background: rgba(137, 87, 229, 0.85); color: #fff; font-size: 0.65rem; font-weight: 700; padding: 3px 8px; border-radius: 6px; z-index: 3; max-width: 120px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
        
        .carousel {{ position: relative; width: 100%; aspect-ratio: 1 / 2; overflow: hidden; background: #000; }}
        .carousel img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }}
        .card:hover .carousel img {{ transform: scale(1.05); }}
        
        .card-body {{ padding: 14px; display: flex; flex-direction: column; flex-grow: 1; }}
        .title {{ font-size: 0.95rem; font-weight: 700; color: #fff; margin-bottom: 4px; line-height: 1.3; }}
        .sub {{ font-size: 0.75rem; color: #a68ec3; margin-bottom: 10px; }}
        
        .prices {{ margin-top: auto; margin-bottom: 12px; background: rgba(0,0,0,0.25); padding: 10px; border-radius: 8px; display: flex; flex-direction: column; gap: 4px; }}
        .price-row {{ display: flex; justify-content: space-between; align-items: center; }}
        .price-wsp-label {{ font-size: 0.65rem; color: #00ff87; font-weight: 700; text-transform: uppercase; }}
        .price-wsp {{ font-size: 0.95rem; font-weight: 800; color: #00ff87; }}
        
        .btn {{ width: 100%; padding: 10px; border-radius: 8px; font-weight: 700; font-size: 0.8rem; border: none; cursor: pointer; text-decoration: none; text-align: center; display: inline-block; transition: 0.2s; background: #00ff87; color: #0d0714; }}
        .btn:hover {{ background: #00cc6a; box-shadow: 0 0 12px rgba(0, 255, 135, 0.4); }}

        /* MODAL DE DETALLE (ESTILO MERCADO LIBRE) */
        .modal-overlay {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(13, 7, 20, 0.85); backdrop-filter: blur(8px); z-index: 1000; display: none; justify-content: center; align-items: center; padding: 15px; }}
        .modal-container {{ background: #190d28; border: 1px solid #331b52; border-radius: 20px; max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto; display: flex; flex-direction: column; position: relative; animation: modalPop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); }}
        @media (min-width: 768px) {{ .modal-container {{ flex-direction: row; }} }}
        @keyframes modalPop {{ from {{ transform: scale(0.8); opacity: 0; }} to {{ transform: scale(1); opacity: 1; }} }}
        
        .modal-close {{ position: absolute; top: 15px; right: 15px; background: rgba(255,255,255,0.1); color: #fff; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1.2rem; cursor: pointer; z-index: 10; display: flex; align-items: center; justify-content: center; transition: 0.2s; }}
        .modal-close:hover {{ background: #00ff87; color: #0d0714; }}

        .modal-gallery {{ flex: 1; padding: 20px; display: flex; flex-direction: column; align-items: center; background: #0a0410; border-top-left-radius: 20px; border-bottom-left-radius: 20px; }}
        .modal-main-img {{ width: 100%; aspect-ratio: 1 / 2; object-fit: cover; border-radius: 12px; margin-bottom: 12px; border: 1px solid #331b52; }}
        .modal-thumbnails {{ display: flex; gap: 8px; overflow-x: auto; width: 100%; padding-bottom: 5px; }}
        .thumb {{ width: 55px; height: 75px; object-fit: cover; border-radius: 6px; cursor: pointer; border: 2px solid transparent; opacity: 0.6; transition: 0.2s; }}
        .thumb.active, .thumb:hover {{ border-color: #00ff87; opacity: 1; }}

        .modal-info {{ flex: 1.2; padding: 25px; display: flex; flex-direction: column; gap: 15px; }}
        .modal-title {{ font-size: 1.5rem; font-weight: 800; color: #fff; }}
        .modal-sub {{ font-size: 0.85rem; color: #a68ec3; }}
        
        .variant-select-box {{ display: flex; flex-direction: column; gap: 6px; }}
        .variant-label {{ font-size: 0.75rem; color: #a68ec3; font-weight: 700; text-transform: uppercase; }}
        .variant-dropdown {{ background: #0d0714; border: 1px solid #331b52; color: #fff; padding: 10px 15px; border-radius: 8px; font-size: 0.95rem; outline: none; cursor: pointer; }}
        .variant-dropdown:focus {{ border-color: #00ff87; }}

        .ficha-tecnica {{ background: rgba(0,0,0,0.25); padding: 12px; border-radius: 10px; font-size: 0.8rem; color: #c9b1e2; display: flex; flex-direction: column; gap: 4px; }}
        .ficha-tecnica b {{ color: #fff; }}

        .modal-prices {{ background: rgba(0,255,135,0.05); border: 1px solid rgba(0,255,135,0.2); padding: 15px; border-radius: 12px; display: flex; flex-direction: column; gap: 8px; }}
        .modal-price-transf {{ font-size: 1.5rem; font-weight: 900; color: #00ff87; }}
        .modal-price-meli {{ font-size: 1.1rem; font-weight: 700; color: #ffe600; }}

        .modal-btn-group {{ display: flex; flex-direction: column; gap: 10px; margin-top: auto; }}
        .btn-meli {{ background: #ffe600; color: #000; }}
        .btn-meli:hover {{ background: #ffd000; }}
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

    <!-- MODAL DE DETALLE -->
    <div class="modal-overlay" id="productModal" onclick="cerrarModalFuera(event)">
        <div class="modal-container" id="modalContainer">
            <button class="modal-close" onclick="cerrarModal()">✕</button>
            <div class="modal-gallery">
                <img id="modalMainImg" class="modal-main-img" src="" alt="Vista previa">
                <div class="modal-thumbnails" id="modalThumbnails"></div>
            </div>
            <div class="modal-info">
                <div>
                    <div class="modal-sub" id="modalFranq">Franquicia</div>
                    <h2 class="modal-title" id="modalTitle">Personaje</h2>
                </div>

                <div class="variant-select-box">
                    <label class="variant-label">Seleccionar Versión / Variante:</label>
                    <select id="variantSelect" class="variant-dropdown" onchange="actualizarVarianteModal()"></select>
                </div>

                <div class="ficha-tecnica">
                    <div><b>Medida:</b> 90 cm x 30 cm</div>
                    <div><b>Estampado:</b> Alta definición a doble faz / simple faz</div>
                    <div><b>Confección:</b> Microfibra premium + Relleno de vellón siliconado</div>
                </div>

                <div class="modal-prices">
                    <div>
                        <div style="font-size: 0.7rem; color: #00ff87; text-transform: uppercase; font-weight: 700;">Precio por Transferencia</div>
                        <div class="modal-price-transf" id="modalPriceTransf">$0</div>
                    </div>
                    <div>
                        <div style="font-size: 0.7rem; color: #ffe600; text-transform: uppercase; font-weight: 700;">Precio Mercado Libre</div>
                        <div class="modal-price-meli" id="modalPriceMeli">$0</div>
                    </div>
                </div>

                <div class="modal-btn-group">
                    <a id="modalBtnWsp" href="#" target="_blank" class="btn btn-wsp">💬 Encargar por WhatsApp</a>
                    <a id="modalBtnMeli" href="#" target="_blank" class="btn btn-meli" style="display:none;">Ver en MercadoLibre</a>
                </div>
            </div>
        </div>
    </div>

    <script>
        const productos = {json_data};
        let catActual = 'Todos';
        let productoActual = null;
        const whatsappNumber = "{WHATSAPP_NUMBER}";

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
            productos.forEach((p, index) => {{
                const matchCat = catActual === 'Todos' || p.categoria.toLowerCase() === catActual.toLowerCase();
                const matchSearch = p.personaje.toLowerCase().includes(search) || p.franquicia.toLowerCase().includes(search) || p.categoria.toLowerCase().includes(search);

                if (matchCat && matchSearch) {{
                    count++;
                    const card = document.createElement('div');
                    card.className = 'card';
                    card.onclick = () => abrirModal(index);
                    
                    let badgeHTML = p.destacado ? `<div class="badge">🔥 Destacado</div>` : '';
                    let franqHTML = p.franquicia ? `<div class="franq-tag">${{p.franquicia}}</div>` : '';

                    // Precio base (DAKI90S por defecto para la tarjeta)
                    let precioBase = p.variantes && p.variantes['DAKI90S'] ? p.variantes['DAKI90S'].precio_transf : 17000;
                    let precioBaseMeli = p.variantes && p.variantes['DAKI90S'] ? p.variantes['DAKI90S'].precio_meli : 27055;
                    let precioTransfFmt = Number(precioBase).toLocaleString('es-AR', {{ style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }});
                    let precioMeliFmt = Number(precioBaseMeli).toLocaleString('es-AR', {{ style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }});

                    card.innerHTML = `
                        ${{badgeHTML}}
                        ${{franqHTML}}
                        <div class="carousel">
                            <img src="${{p.fotos[0]}}" alt="${{p.personaje}}" loading="lazy">
                        </div>
                        <div class="card-body">
                            <div class="title">Dakimakura - ${{p.personaje}}</div>
                            <div class="sub">${{p.franquicia}}</div>
                            
                            <div class="prices">
                                <div class="price-row">
                                    <span class="price-wsp-label">Transferencia</span>
                                    <span class="price-wsp">${{precioTransfFmt}}</span>
                                </div>
                                <div class="price-row">
                                    <span class="price-meli-label" style="font-size:0.65rem; color:#ffe600;">Mercado Libre</span>
                                    <span class="price-meli" style="font-size:0.85rem; color:#ffe600;">${{precioMeliFmt}}</span>
                                </div>
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

        function abrirModal(index) {{
            productoActual = productos[index];
            document.getElementById('modalTitle').innerText = "Dakimakura - " + productoActual.personaje;
            document.getElementById('modalFranq').innerText = productoActual.franquicia;

            // Galería de fotos / carrusel
            const mainImg = document.getElementById('modalMainImg');
            const thumbs = document.getElementById('modalThumbnails');
            thumbs.innerHTML = '';

            if(productoActual.fotos && productoActual.fotos.length > 0) {{
                mainImg.src = productoActual.fotos[0];
                productoActual.fotos.forEach((foto, i) => {{
                    const t = document.createElement('img');
                    t.src = foto;
                    t.className = 'thumb ' + (i === 0 ? 'active' : '');
                    t.onclick = () => {{
                        mainImg.src = foto;
                        document.querySelectorAll('.thumb').forEach(th => th.classList.remove('active'));
                        t.classList.add('active');
                    }};
                    thumbs.appendChild(t);
                }});
            }}

            // Rellenar variantes de precios
            const selectVar = document.getElementById('variantSelect');
            selectVar.innerHTML = '';
            if (productoActual.variantes) {{
                for (const [key, v] of Object.entries(productoActual.variantes)) {{
                    const opt = document.createElement('option');
                    opt.value = key;
                    opt.innerText = `${{v.nombre}} ($ ${{v.precio_transf.toLocaleString('es-AR')}})`;
                    selectVar.appendChild(opt);
                }}
            }}

            actualizarVarianteModal();
            document.getElementById('productModal').style.display = 'flex';
        }}

        function actualizarVarianteModal() {{
            const selectVar = document.getElementById('variantSelect');
            const codigoVar = selectVar.value;
            const varianteData = productoActual.variantes[codigoVar];

            if(varianteData) {{
                let transfFmt = Number(varianteData.precio_transf).toLocaleString('es-AR', {{ style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }});
                let meliFmt = Number(varianteData.precio_meli).toLocaleString('es-AR', {{ style: 'currency', currency: 'ARS', maximumFractionDigits: 0 }});

                document.getElementById('modalPriceTransf').innerText = transfFmt;
                document.getElementById('modalPriceMeli').innerText = meliFmt;

                // Enlace WhatsApp personalizado con variante
                let msgWsp = `¡Hola ARCHER! Quiero encargar la Dakimakura de ${{productoActual.personaje}} (${{productoActual.franquicia}}) en versión: ${{varianteData.nombre}}. Aprovecho el precio por transferencia.`;
                document.getElementById('modalBtnWsp').href = `https://wa.me/${{whatsappNumber}}?text=${{encodeURIComponent(msgWsp)}}`;
            }}

            // Botón Mercado Libre
            const btnMeli = document.getElementById('modalBtnMeli');
            if(productoActual.link_meli) {{
                btnMeli.href = productoActual.link_meli;
                btnMeli.style.display = 'block';
            }} else {{
                btnMeli.style.display = 'none';
            }}
        }}

        function cerrarModal() {{
            document.getElementById('productModal').style.display = 'none';
        }}

        function cerrarModalFuera(e) {{
            if(e.target.id === 'productModal') {{
                cerrarModal();
            }}
        }}

        renderProductos();
    </script>
</body>
</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_template)
    print("✨ ¡Catálogo index.html generado con Modal de Detalle, Carrusel de Variantes y Precios por Categoría!")

if __name__ == "__main__":
    prods = obtener_productos_notion()
    if prods:
        generar_html(prods)
    else:
        print("[ERROR] No se pudieron obtener productos de Notion.")
