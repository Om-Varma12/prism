import zcatalyst_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from tests.db.data_insertion import router as insertion_router
from tests.db.truncate import router as truncate_router
from tests.db.table_schema import router as schema_router
from tests.db.insert_derived_data import router as derived_insertion_router
from tests.db.truncate_derived import router as derived_truncate_router
from routers.dashboard import router as dashboard_router

app = FastAPI()

app.include_router(router=insertion_router)
app.include_router(router=truncate_router)
app.include_router(router=schema_router)
app.include_router(router=derived_insertion_router)
app.include_router(router=derived_truncate_router)
app.include_router(router=dashboard_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home(request: Request):
    catalyst_app = zcatalyst_sdk.initialize(req=request)
    return {"status": "SDK initialized"}