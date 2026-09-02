import requests

NOTION_TOKEN = "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"
DATABASE_ID = "3c467edf6aa3804bb22eff38cf888fd0"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

payload = {
    "parent": {"database_id": DATABASE_ID},
    "properties": {
        "Personaje": {
            "title": [{"text": {"content": "Changli"}}]
        },
        "Franquicia": {
            "select": {"name": "Wuthering Waves"}
        },
        "Estado": {
            "status": {"name": "In progress"}
        },
        "Link MeLi": {
            "url": "https://mercadolibre.com.ar"
        }
    }
}

response = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)

if response.status_code == 200:
    print("¡Conexión exitosa! Se creó la fila de Changli en Notion.")
else:
    print(f"Error ({response.status_code}): {response.text}")