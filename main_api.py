from fastapi import FastAPI
app = FastAPI(title="Đuka Noosphere API")

@app.post("/inject_mental_disorder")
def inject(pos: tuple, intensity: float):
    noosphere.inject_mental_disorder(pos, intensity)
    return {"status": "injected"}

@app.get("/reality_status")
def status():
    return {
        "collective_reality": noosphere.collective_reality_match(),
        "noosphere_field": noosphere.noosphere_field.mean(),
        "programmable_time": reality.reality_layer[:,:,1].mean()
    }
