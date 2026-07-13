import zcatalyst_sdk
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
from dotenv import load_dotenv
load_dotenv()

from tests.db.data_insertion import router as insertion_router
from tests.db.truncate import router as truncate_router
from tests.db.table_schema import router as schema_router
from tests.db.insert_derived_data import router as derived_insertion_router
from tests.db.truncate_derived import router as derived_truncate_router
from tests.db.add_conversation_metadata_columns import router as schema_columns_router
from routers.dashboard import router as dashboard_router
from routers.network import router as network_router
from tests.db.insert_recent_cases import router as recent_cases_router
from tests.db.update_alerts_acknowledgment import router as alerts_ack_router
from tests.db.update_dashboard_stats import router as dashboard_stats_router
from tests.db.auto_sync_alerts import router as auto_sync_router, sync_alert_count
from routers.chat import router as chat_router
from tests.db.populate_network_data import router as populate_network_router
from core.database import get_datastore, get_zcql

app = FastAPI()

# Initialize APScheduler
scheduler = AsyncIOScheduler()

# Scheduled job function
async def scheduled_sync_alerts():
    """Scheduled job to sync alert count every 5 minutes."""
    try:
        print("[Scheduler] Starting alert count sync...")
        # Initialize Catalyst SDK without request context
        catalyst_app = zcatalyst_sdk.initialize()
        zcql = catalyst_app.zcql()
        datastore = catalyst_app.datastore()
        
        result = sync_alert_count(zcql, datastore)
        print(f"[Scheduler] Sync completed: {result}")
    except Exception as e:
        print(f"[Scheduler] Error during sync: {e}")

# Add scheduled job (every 5 minutes)
scheduler.add_job(
    scheduled_sync_alerts,
    trigger=IntervalTrigger(minutes=5),
    id='sync_alert_count',
    name='Sync Alert Count',
    replace_existing=True
)

# Startup event
@app.on_event("startup")
async def startup_event():
    print("[Startup] Starting APScheduler...")
    scheduler.start()
    print("[Startup] APScheduler started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    print("[Shutdown] Stopping APScheduler...")
    scheduler.shutdown()
    print("[Shutdown] APScheduler stopped")

app.include_router(router=insertion_router)
app.include_router(router=truncate_router)
app.include_router(router=schema_router)
app.include_router(router=derived_insertion_router)
app.include_router(router=derived_truncate_router)
app.include_router(router=schema_columns_router)
app.include_router(router=dashboard_router)
app.include_router(router=network_router)
app.include_router(router=recent_cases_router)
app.include_router(router=alerts_ack_router)
app.include_router(router=dashboard_stats_router)
app.include_router(router=auto_sync_router)
app.include_router(router=chat_router)
app.include_router(router=populate_network_router)

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
