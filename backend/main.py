
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CoordinateRequest(BaseModel):
    lat: float
    lng: float

class CropRecommendation(BaseModel):
    crop: str
    profit: int
    scalability: str

class RecommendationResponse(BaseModel):
    recommendations: List[CropRecommendation]

SOILGRIDS_URL = "https://rest.soilgrids.org/query"

def get_soil_data(lat: float, lng: float):
    try:
        response = requests.get(f"{SOILGRIDS_URL}?lon={lng}&lat={lat}")
        data = response.json()
        ph = data['properties']['phh2o']['mean'] if 'phh2o' in data['properties'] else None
        return {"ph": ph}
    except Exception as e:
        print("Soil API Error:", e)
        return {"ph": None}

NASA_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"

def get_climate_data(lat: float, lng: float):
    try:
        params = {
            "parameters": "T2M,PRECTOT",
            "community": "AG",
            "longitude": lng,
            "latitude": lat,
            "format": "JSON"
        }
        response = requests.get(NASA_URL, params=params)
        data = response.json()
        t2m = data['properties']['parameter']['T2M']['ANN']
        rainfall = data['properties']['parameter']['PRECTOT']['ANN']
        return {"temperature": t2m, "rainfall": rainfall}
    except Exception as e:
        print("Climate API Error:", e)
        return {"temperature": None, "rainfall": None}

def recommend_crops(soil, climate):
    ph = soil.get("ph")
    rainfall = climate.get("rainfall")
    recommendations = []
    if ph and ph > 6.5 and rainfall and rainfall > 600:
        recommendations.append({"crop": "Soybean", "profit": 45000, "scalability": "High"})
    if ph and 6.0 <= ph <= 7.0:
        recommendations.append({"crop": "Wheat", "profit": 35000, "scalability": "Medium"})
    if rainfall and rainfall < 500:
        recommendations.append({"crop": "Mustard", "profit": 30000, "scalability": "Medium"})
    if not recommendations:
        recommendations.append({"crop": "Millet", "profit": 25000, "scalability": "High"})
    return recommendations

@app.post("/recommend", response_model=RecommendationResponse)
def recommend(coords: CoordinateRequest):
    soil_data = get_soil_data(coords.lat, coords.lng)
    climate_data = get_climate_data(coords.lat, coords.lng)
    recs = recommend_crops(soil_data, climate_data)
    return {"recommendations": recs}
