from fastapi import Request
import zcatalyst_sdk

def get_datastore(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the datastore instance.
    """
    try:
        app = zcatalyst_sdk.initialize(req=request)
    except Exception:
        app = zcatalyst_sdk.initialize()
    return app.datastore()

def get_zcql(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the ZCQL service instance for executing queries.
    """
    try:
        app = zcatalyst_sdk.initialize(req=request)
    except Exception:
        app = zcatalyst_sdk.initialize()
    return app.zcql()
