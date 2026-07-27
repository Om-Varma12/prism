"""
PRISM — Insert New Data Route (20 Rows Per Table)
=================================================
Wrapper route file that dynamically reloads insert_new_data_impl.py on each request
to prevent caching in the local non-reloading Appsail environment.
"""

from fastapi import Request, APIRouter, Depends
from core.database import get_zcql
import importlib

router = APIRouter(prefix="/db", tags=["new-data-insertion"])

@router.get("/tests/insert-new-data")
def insert_new_data(request: Request, zcql=Depends(get_zcql)):
    # Dynamically import and reload the implementation module
    import tests.db.insert_new_data_impl as impl
    importlib.reload(impl)
    return impl.run_insert(request, zcql)
