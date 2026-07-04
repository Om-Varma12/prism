from fastapi import APIRouter, Request
import zcatalyst_sdk

router = APIRouter(
    prefix="/db/test",
    tags=["debug"]
)


def get_datastore(req: Request):
    app = zcatalyst_sdk.initialize(req=req)
    return app.datastore()


@router.get("/schema")
def print_schema(request: Request):
    datastore = get_datastore(request)
    schema_dict = {}

    try:
        tables = datastore.get_all_tables()

        for table in tables:
            table_name = table._table_details["table_name"]
            metadata = datastore.get_table_details(table_name)
            cols = []
            for column in metadata["column_details"]:
                cols.append({
                    "column_name": column['column_name'],
                    "data_type": column['data_type'],
                    "is_mandatory": column['is_mandatory'],
                    "is_unique": column['is_unique']
                })
            schema_dict[table_name] = cols

        return {"status": "success", "schema": schema_dict}

    except Exception as e:
        print(e)
        return {
            "status": "failed",
            "error": str(e)
        }