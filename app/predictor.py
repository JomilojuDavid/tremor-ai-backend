from app.mode import model


FEATURE_NAMES = [
    "aX",
    "aY",
    "aZ",
    "gX",
    "gY",
    "gZ",
]


def predict(sensor):
    values = pd.DataFrame(
        [[
            sensor.aX,
            sensor.aY,
            sensor.aZ,
            sensor.gX,
            sensor.gY,
            sensor.gZ,
        ]],
        columns=FEATURE_NAMES,
    )

    prediction = model.predict(values)[0]

    probabilities = model.predict_proba(values)[0]
    confidence = float(max(probabilities))

    return prediction, confidence