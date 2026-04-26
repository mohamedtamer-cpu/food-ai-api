import json
import os
from difflib import get_close_matches
from groq import Groq
from fastapi import FastAPI, Query
from dotenv import load_dotenv

# 1. Load variables from .env file
load_dotenv()

# 2. Setup Groq using the secure API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY)

# 3. Initialize FastAPI App
app = FastAPI(title="Food AI Search API", version="1.0")

# 4. Load the JSON database
food_list = []
food_db = {}

def load_database():
    global food_list, food_db
    try:
        with open('food_db.json', 'r', encoding='utf-8') as f:
            food_list = json.load(f)
        # Convert to dictionary for fast searching (lowercase keys)
        food_db = {item["name"].lower(): item["description"] for item in food_list}
        print(f"Database loaded successfully with {len(food_list)} items.")
    except FileNotFoundError:
        print("Warning: food_db.json file not found! A new one will be created.")
        food_list = []
        food_db = {}

# Run the load function when the app starts
load_database()

def save_to_json(new_food_list):
    """Saves the updated list back to the JSON file."""
    try:
        with open('food_db.json', 'w', encoding='utf-8') as f:
            json.dump(new_food_list, f, ensure_ascii=False, indent=4) 
    except Exception as e:
        print(f"Error saving to JSON: {e}")

# 5. Define the API Endpoint
@app.get("/api/food")
def get_food_info(name: str = Query(..., description="Food name to search")):
    query = name.lower().strip()

    # Step 1: Local Search (80% accuracy threshold to prevent mismatches)
    matches = get_close_matches(query, food_db.keys(), n=1, cutoff=0.8)

    if matches:
        matched_name = matches[0]
        return {
            "status": "success",
            "source": "local_json",
            "name": matched_name.title(),
            "description": food_db[matched_name]
        }

    # Step 2: Fallback to Groq AI
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional menu writer. Describe the following food item in a short, appetizing way (maximum 15 to 20 words). Focus only on the taste and ingredients. Do not add conversational text."
                },
                {
                    "role": "user",
                    "content": f"Food item: {name}"
                }
            ],
            temperature=0.6,
            max_tokens=40
        )
        ai_description = response.choices[0].message.content.strip()

        # Step 3: Auto-save the new dish
        formatted_name = name.title()
        
        # Update current memory
        food_db[query] = ai_description
        food_list.append({
            "name": formatted_name,
            "description": ai_description
        })
        
        # Write to file
        save_to_json(food_list)

        return {
            "status": "success",
            "source": "groq_ai",
            "name": formatted_name,
            "description": ai_description
        }

    except Exception as e:
        # Step 4: Emergency Fallback (if internet drops or API fails)
        return {
            "status": "error",
            "source": "fallback",
            "name": name.title(),
            "description": "A delicious and freshly prepared dish, crafted with high-quality ingredients.",
            "details": str(e)
        }

# Optional: Allows you to run the file directly for local testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)