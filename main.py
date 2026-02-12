from fastapi import FastAPI

app = FastAPI()

@app.get("/ main")
async def root():
    return{"message: hello world"}
 