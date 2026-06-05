
import json, os
DB_FILE="database.json"
DEFAULT_CATEGORIES=[
"Tecnología y Electrónica","Moda y Accesorios","Hogar y Decoración",
"Salud y Belleza","Deportes y Aire Libre","Alimentos y Bebidas",
"Juguetes y Bebés","Automotriz"
]

def read_db():
    if not os.path.exists(DB_FILE):
        return {"products":[],"categories":DEFAULT_CATEGORIES}
    with open(DB_FILE,"r",encoding="utf-8") as f:
        return json.load(f)

def write_db(data):
    with open(DB_FILE,"w",encoding="utf-8") as f:
        json.dump(data,f,ensure_ascii=False,indent=2)
