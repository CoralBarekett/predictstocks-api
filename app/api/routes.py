from fastapi import APIRouter
from app.models.schemas import StockPredictionRequest, StockPrediction
from app.services.predictor import generate_prediction

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok"}

@router.post("/predict", response_model=StockPrediction)
async def predict_stock(req: StockPredictionRequest):
    return await generate_prediction(req)