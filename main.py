import os
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import Groq
from dotenv import load_dotenv
from enum import Enum

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize FastAPI and Groq
app = FastAPI()
client = Groq(api_key=GROQ_API_KEY)

# CORS setup (3ashan el Frontend y-3raf yekalemna)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_FILE = "food_db.json"

# --- EL EKHTYARAT (Drop-down Menus) ---
class ToneEnum(str, Enum):
    professional = "professional"
    funny = "funny"
    mouth_watering = "mouth-watering"
    casual = "casual"

class TypeEnum(str, Enum):
    food = "food"
    drink = "drink"
    dessert = "dessert"

# --- LOAD & SAVE DATABASE ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {} # Law el malaf fady aw moshkela f-formato, yebda2 3la ndafa
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(db, file, indent=4)

food_db = load_db()

# --- HEALTH CHECK ---
@app.get("/health")
def health_check():
    return {"status": "healthy", "database_items": len(food_db)}

# --- EL ENDPOINT EL ASASY ---
@app.get("/api/food")
def get_food(
    name: str, 
    item_type: TypeEnum = TypeEnum.food, 
    tone: ToneEnum = ToneEnum.professional
):
    name_lower = name.lower()
    
    # 1. LOCAL SEARCH (Bndawar 3al Akla + El Tone el matloub)
    if name_lower in food_db:
        if "descriptions" in food_db[name_lower] and tone.value in food_db[name_lower]["descriptions"]:
            if food_db[name_lower]["descriptions"][tone.value]:
                return {
                    "status": "success",
                    "source": "local_database",
                    "name": name,
                    "type": item_type.value,
                    "tone": tone.value,
                    "description": food_db[name_lower]["descriptions"][tone.value]
                }

    # 2. ASK GROQ AI (Han-tlub mno El Tone el mtkhar BAS)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are an elite culinary copywriter. The user will provide a {item_type.value}. 
Write a single, elegant description (around 25 to 40 words) matching exactly a '{tone.value}' tone. 
- professional: High-end restaurant menu style.
- funny: Clever, witty, and relatable.
- mouth-watering: Deeply sensory, focusing on cravings.
- casual: Warm, inviting, and friendly.
Do not include any other text, just the description."""
                },
                {
                    "role": "user",
                    "content": f"Item: {name}"
                }
            ],
            temperature=0.75,
            max_tokens=100  # Raga3naha 100 3ashan howa by-kteb wasf wahed bas dlw2ty
        )
        
        # B-nestlem el wasf el wahed bas
        ai_description = response.choices[0].message.content.strip()
        
        # 3. SAVE TO DATABASE (N-save el Tone da bas)
        if name_lower not in food_db:
            food_db[name_lower] = {
                "name": name,
                "type": item_type.value,
                "descriptions": {}
            }
            
        # Han-zawed el wasf el gdid 3ala el descriptions el adima (law feh)
        food_db[name_lower]["descriptions"][tone.value] = ai_description
        
        save_db(food_db)

        return {
            "status": "success",
            "source": "groq_ai",
            "name": name,
            "type": item_type.value,
            "tone": tone.value,
            "description": ai_description
        }

    except Exception as e:
        return {
            "status": "error",
            "source": "fallback",
            "name": name,
            "description": "A deliciously prepared item, ready to be enjoyed.",
            "details": str(e)
        }
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)    