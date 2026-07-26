import numpy as np
from app.mode import model

def predict(sensor):
    
    values = np.array([[sensor.aX, sensor.aY, sensor.aZ, sensor.gX, sensor.gY, sensor.gZ]])
    
    prediction = model.predict(values)[0]
    
    probabilities = model.predict_proba(values)[0]
    
    confidence = float(max(probabilities))

    return prediction, confidence
