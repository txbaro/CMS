from fastapi import FastAPI

app = FastAPI(title="Collaborative CMS API")

@app.get("/")
async def root():
    return {"message": "Backend FastAPI is running!"}