from fastapi import FastAPI

app = FastAPI()
# Add this block to handle the "/" endpoint

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}