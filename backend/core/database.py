from fastapi import Request
import zcatalyst_sdk

def get_datastore(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the datastore instance.
    """
    app = zcatalyst_sdk.initialize(req=request)
    return app.datastore()

def get_zcql(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the ZCQL service instance for executing queries.
    """
    app = zcatalyst_sdk.initialize(req=request)
    return app.zcql()
