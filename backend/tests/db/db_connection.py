from fastapi import FastAPI
import zcatalyst_sdk

app = FastAPI()

@app.get("/")
def home():
    catalyst = zcatalyst_sdk.initialize()

    datastore = catalyst.datastore()

    return {"status": "SDK initialized successfully"}