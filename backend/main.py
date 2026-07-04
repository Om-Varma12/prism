import zcatalyst_sdk
from fastapi import FastAPI, Request

from tests.db.data_insertion import router as insertion_router
from tests.db.truncate import router as truncate_router
from tests.db.table_schema import router as schema_router
from routers.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(router=insertion_router)
app.include_router(router=truncate_router)
app.include_router(router=schema_router)
app.include_router(router=dashboard_router)

@app.get("/")
def home(request: Request):
    catalyst_app = zcatalyst_sdk.initialize(req=request)
    return {"status": "SDK initialized"}