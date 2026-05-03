from fastapi import FastAPI

app = FastAPI(title="AI Speaking Coach v2")

@app.get("/")
def home():
    return {"message": "Backend is running clean ✅"}