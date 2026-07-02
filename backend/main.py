from fastapi import FastAPI, Request
import zcatalyst_sdk

app = FastAPI()

@app.get("/")
def home(request: Request):
    catalyst = zcatalyst_sdk.initialize(req=request)

    datastore = catalyst.datastore()

    print(datastore)
    return {"status": "SDK initialized"}