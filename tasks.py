from typing import Optional
from sklearn.ensemble import RandomForestClassifier

forest_model: Optional[RandomForestClassifier] = None


def job(features):
    global forest_model

    if forest_model is None:
        return None
    return forest_model.predict(features)

