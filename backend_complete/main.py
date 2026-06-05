from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from dotenv import load_dotenv
from app.database import read_db, write_db
import os
import uuid
import json

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Product Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/")
def root():
    return {"message": "API funcionando 🚀"}
# -------------------------
# MODELO REQUEST
# -------------------------
class GenerateRequest(BaseModel):
    name: str
    category: str
    features: list[str]
    brand: str | None = None
    tone: str = "professional"
    targetAudience: str | None = None


# -------------------------
# ENDPOINTS BÁSICOS
# -------------------------
@app.get("/api/products")
def products():
    return read_db()["products"]


@app.get("/api/categories")
def categories():
    return read_db()["categories"]


@app.get("/api/stats")
def stats():
    db = read_db()

    return {
        "totalGenerated": len(db["products"]),
        "hoursSaved": 0,
        "categoryDistribution": []
    }


# -------------------------
# GENERACIÓN CON GEMINI (CORREGIDO)
# -------------------------
@app.post("/api/generate")
def generate(req: GenerateRequest):

    api_key = os.getenv("GEMINI_API_KEY")

    print("====================================")
    print("API KEY:", api_key)
    print("====================================")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="GEMINI_API_KEY no encontrada en el archivo .env"
        )

    try:
        client = genai.Client(api_key=api_key)

        prompt = f"""
Actúa como un experto en marketing digital y ecommerce.

Producto: {req.name}
Categoría: {req.category}
Marca: {req.brand}
Características: {", ".join(req.features)}
Público objetivo: {req.targetAudience}
Tono: {req.tone}

Devuelve SOLO un JSON válido con esta estructura exacta:

{{
  "title": "string",
  "description": "string",
  "benefits": ["string"],
  "seoKeywords": ["string"],
  "ctas": ["string"]
}}

IMPORTANTE:
- No agregues texto adicional
- No uses markdown
- Solo JSON válido
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        # -------------------------
        # PARSEO SEGURO DEL JSON
        # -------------------------
        raw = response.text.strip()

        # limpiar posibles ```json
        raw = raw.replace("```json", "").replace("```", "")

        data = json.loads(raw)

        # -------------------------
        # RESPUESTA FINAL (CONTRATO FRONTEND)
        # -------------------------
        return {
            "success": True,
            "title": data.get("title", ""),
            "description": data.get("description", ""),
            "benefits": data.get("benefits", []),
            "seoKeywords": data.get("seoKeywords", []),
            "ctas": data.get("ctas", [])
        }

    except Exception as e:
        print("ERROR GEMINI:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# -------------------------
# GUARDAR PRODUCTO
# -------------------------
@app.post("/api/products")
def save_product(payload: dict):

    db = read_db()

    payload["id"] = str(uuid.uuid4())

    db["products"].append(payload)

    write_db(db)

    return payload