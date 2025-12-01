"""
FastAPI Backend for Coin Classification
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .predictor import predict, load_models

app = FastAPI(
    title="Coin Classification API",
    description="API untuk klasifikasi koin rupiah menggunakan CNN dan Random Forest",
    version="1.0.0"
)

# CORS - allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite & CRA default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    print("Loading models...")
    load_models()
    print("Models loaded!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Coin Classification API is running"}


@app.get("/health")
async def health_check():
    """Health check for deployment"""
    return {"status": "healthy"}


@app.post("/predict")
async def predict_coin(file: UploadFile = File(...)):
    """
    Predict coin class from uploaded image
    
    Returns:
    - preprocessing_steps: images of each preprocessing step (base64)
    - predictions: results from CNN and Random Forest models
    - circle_detected: whether a coin circle was detected
    """
    # Validate file type
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image bytes
        image_bytes = await file.read()
        
        # Run prediction
        result = predict(image_bytes)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")
