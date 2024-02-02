from fastapi import FastAPI, Depends, Query
from pydantic import BaseModel

app = FastAPI()

class CatModel(BaseModel):
    name: str
    breed: str

class DogModel(BaseModel):
    name: str
    age: int

def get_model(model_type: str = Query(..., alias="type")):
    if model_type == "cat":
        return CatModel
    elif model_type == "dog":
        return DogModel
    else:
        raise ValueError("Unsupported model type")

@app.post("/pets/")
async def create_pet(model: BaseModel = Depends(get_model)):
    return model