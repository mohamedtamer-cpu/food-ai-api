# 🍽️ Food AI Search API (Microservice)

A fast, Dockerized microservice built with **FastAPI** and **Groq AI (Llama 3.3 70b)** to search for and generate appetizing food descriptions. 

## ✨ Features
- **Smart Local Cache:** Searches `food_db.json` first with 80% accuracy to save API costs and reduce response time.
- **AI Fallback:** If a dish isn't found locally, it asks Groq AI for a short, professional description.
- **Auto-Save:** Newly generated AI descriptions are automatically saved to the local database.
- **Docker Ready:** Easy to deploy anywhere.

## 🚀 How to Run (Using Docker)

**1. Clone the repository:**
```bash
git clone [https://github.com/mohamedtamer-cpu/food-ai-api.git](https://github.com/mohamedtamer-cpu/food-ai-api.git)
cd food-ai-api