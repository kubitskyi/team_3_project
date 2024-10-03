from fastapi import FastAPI
import uvicorn

from src.routes import users

app = FastAPI()

app.include_router(users.router, prefix='/api')


@app.get("/")
def read_root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="localhost",
        port=8000,
        reload=True
    )