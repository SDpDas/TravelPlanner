from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import sqlite3
from datetime import datetime
import os
import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('itinerary.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS itinerary
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  location TEXT NOT NULL,
                  date TEXT NOT NULL,
                  description TEXT,
                  image_url TEXT)''')
    # Add image_url column if missing
    try:
        c.execute("ALTER TABLE itinerary ADD COLUMN image_url TEXT")
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()

init_db()

# Initialize LangChain with Google Gemini
def get_llm():
    return ChatGoogleGenerativeAI(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="gemini-1.5-flash",
        temperature=0.7,
        max_tokens=1000
    )

# Prompt template for generating location descriptions
prompt_template = PromptTemplate(
    input_variables=["location"],
    template="Provide a concise yet engaging description of {location} as a travel destination, highlighting key cultural, historical, and natural attractions in 200-300 words, suitable for a travel itinerary."
)

# Function to generate image using Hugging Face Stable Diffusion
def generate_image(location):
    api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not api_key:
        print("Hugging Face API key not set")
        return None  # Fallback if no API key
    url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": f"A scenic view of {location}, vibrant and detailed, suitable for a travel itinerary"
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            # Save image temporarily (or use a CDN in production)
            image_path = f"static/{location.replace(' ', '_')}.jpg"
            with open(image_path, "wb") as f:
                f.write(response.content)
            return f"http://localhost:5000/{image_path}"
        else:
            print(f"Image generation failed: {response.text}")
            return None
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

# Function to generate description using LangChain
def generate_description(location):
    llm = get_llm()
    chain = prompt_template | llm
    response = chain.invoke({"location": location})
    return response.content

# API to add a location and date
@app.route('/api/itinerary', methods=['POST'])
def add_itinerary():
    data = request.get_json()
    location = data.get('location')
    date = data.get('date')
    
    if not location or not date:
        return jsonify({"error": "Location and date are required"}), 400
    
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid date format, use YYYY-MM-DD"}), 400
    
    # Generate description and image
    description = generate_description(location)
    image_url = generate_image(location)
    
    # Store in database
    conn = sqlite3.connect('itinerary.db')
    c = conn.cursor()
    c.execute("INSERT INTO itinerary (location, date, description, image_url) VALUES (?, ?, ?, ?)",
              (location, date, description, image_url))
    conn.commit()
    conn.close()
    
    return jsonify({
        "message": "Itinerary added",
        "location": location,
        "date": date,
        "description": description,
        "image_url": image_url
    }), 201

# API to get all itineraries
@app.route('/api/itinerary', methods=['GET'])
def get_itinerary():
    conn = sqlite3.connect('itinerary.db')
    c = conn.cursor()
    c.execute("SELECT location, date, description, image_url FROM itinerary ORDER BY date")
    itineraries = [{"location": row[0], "date": row[1], "description": row[2], "image_url": row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(itineraries)

if __name__ == '__main__':
    # Create static folder for images if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=True, port=5000)