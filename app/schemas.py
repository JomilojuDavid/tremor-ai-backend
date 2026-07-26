from pydantic import BaseModel

class SensorData(BaseModel):
    aX: float
    aY: float
    aZ: float
    gX: float
    gY: float
    gZ: float