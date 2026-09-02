import csv

personajes = [
    # Honkai: Star Rail
    ("Kafka", "Honkai Star Rail", "Waifu"),
    ("Firefly", "Honkai Star Rail", "Waifu"),
    ("Acheron", "Honkai Star Rail", "Waifu"),
    ("March 7th", "Honkai Star Rail", "Waifu"),
    ("Jingliu", "Honkai Star Rail", "Waifu"),
    ("Sparkle", "Honkai Star Rail", "Waifu"),
    ("Ruan Mei", "Honkai Star Rail", "Waifu"),
    ("Black Swan", "Honkai Star Rail", "Waifu"),
    ("Blade", "Honkai Star Rail", "Husbando"),
    ("Dan Heng", "Honkai Star Rail", "Husbando"),
    
    # Genshin Impact
    ("Raiden Shogun", "Genshin Impact", "Waifu"),
    ("Hu Tao", "Genshin Impact", "Waifu"),
    ("Furina", "Genshin Impact", "Waifu"),
    ("Yelan", "Genshin Impact", "Waifu"),
    ("Ganyu", "Genshin Impact", "Waifu"),
    ("Shenhe", "Genshin Impact", "Waifu"),
    ("Arlecchino", "Genshin Impact", "Waifu"),
    ("Nahida", "Genshin Impact", "Anime"),
    ("Zhongli", "Genshin Impact", "Husbando"),
    ("Neuvillette", "Genshin Impact", "Husbando"),

    # Re:Zero
    ("Rem", "Re:Zero", "Waifu"),
    ("Ram", "Re:Zero", "Waifu"),
    ("Emilia", "Re:Zero", "Waifu"),
    ("Echidna", "Re:Zero", "Waifu"),

    # Jujutsu Kaisen
    ("Gojo Satoru", "Jujutsu Kaisen", "Husbando"),
    ("Toji Fushiguro", "Jujutsu Kaisen", "Husbando"),
    ("Ryomen Sukuna", "Jujutsu Kaisen", "Anime"),
    ("Maki Zenin", "Jujutsu Kaisen", "Waifu"),
    ("Nobara Kugisaki", "Jujutsu Kaisen", "Waifu"),

    # Demon Slayer (Kimetsu no Yaiba)
    ("Nezuko Kamado", "Demon Slayer", "Anime"),
    ("Mitsuri Kanroji", "Demon Slayer", "Waifu"),
    ("Shinobu Kocho", "Demon Slayer", "Waifu"),
    ("Kanao Tsuyuri", "Demon Slayer", "Waifu"),

    # Chainsaw Man
    ("Makima", "Chainsaw Man", "Waifu"),
    ("Power", "Chainsaw Man", "Waifu"),
    ("Reze", "Chainsaw Man", "Waifu"),

    # Sousou no Frieren
    ("Frieren", "Sousou no Frieren", "Anime"),
    ("Fern", "Sousou no Frieren", "Waifu"),

    # Populares / Tendencias / Clásicos
    ("Yor Forger", "Spy x Family", "Waifu"),
    ("Hatsune Miku", "Vocaloid", "Virtual Singer"),
    ("2B", "NieR Automata", "Waifu"),
    ("Asuka Langley", "Evangelion", "Waifu"),
    ("Rei Ayanami", "Evangelion", "Waifu"),
    ("Albedo", "Overlord", "Waifu"),
    ("Marin Kitagawa", "My Dress-Up Darling", "Waifu"),
    ("Artoria Pendragon", "Fate Stay Night", "Waifu"),
    ("Jeanne d'Arc", "Fate Grand Order", "Waifu"),
    ("Asuna", "Blue Archive", "Waifu"),
    ("Karin", "Blue Archive", "Waifu"),
    ("Mikasa Ackerman", "Attack on Titan", "Waifu"),
    ("Levi Ackerman", "Attack on Titan", "Husbando"),
    ("Nami", "One Piece", "Waifu"),
    ("Nico Robin", "One Piece", "Waifu"),
    ("Boa Hancock", "One Piece", "Waifu"),
    ("Megumin", "Konosuba", "Waifu"),
    ("Aqua", "Konosuba", "Waifu"),
    ("Mirko", "My Hero Academia", "Waifu"),
    ("Himiko Toga", "My Hero Academia", "Waifu"),
    ("Hitori Gotoh", "Bocchi the Rock!", "Anime")
]

ruta_archivo = "personajes.csv"

# Escribimos el archivo CSV con codificación utf-8-sig para compatibilidad con Windows/Excel
with open(ruta_archivo, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["personaje", "serie", "tags"])  # Cabecera
    for p in personajes:
        writer.writerow(p)

print(f"✅ Se actualizaron {len(personajes)} personajes correctamente en '{ruta_archivo}'.")