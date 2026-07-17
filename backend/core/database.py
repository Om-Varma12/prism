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

def get_cache(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the cache service instance.
    """
    try:
        app = zcatalyst_sdk.initialize(req=request)
    except Exception:
        app = zcatalyst_sdk.initialize()
    return app.cache()

def get_stratus(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the Stratus service instance.
    """
    try:
        app = zcatalyst_sdk.initialize(req=request)
    except Exception:
        app = zcatalyst_sdk.initialize()
    return app.stratus()

def get_cache_segment(request: Request):
    """
    FastAPI dependency that initializes the Zoho Catalyst SDK
    and returns the cache segment instance with specific segment ID.
    """
    try:
        app = zcatalyst_sdk.initialize(req=request)
    except Exception:
        app = zcatalyst_sdk.initialize()
    
    cache_service = app.cache()
    # Use specific segment ID instead of default
    segment_service = cache_service.segment(segment_id='46143000000079007')
    return segment_service
