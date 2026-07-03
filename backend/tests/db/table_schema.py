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

    print("\n" + "=" * 100)
    print("PRISM DATABASE SCHEMA")
    print("=" * 100)

    try:
        tables = datastore.get_all_tables()

        for table in tables:

            table_name = table._table_details["table_name"]

            metadata = datastore.get_table_details(table_name)

            print("\n" + "=" * 100)
            print(f"TABLE: {table_name}")
            print("=" * 100)
            print(f"{'COLUMN':30} {'TYPE':15} {'MANDATORY':10} {'UNIQUE':10}")
            print("-" * 100)

            for column in metadata["column_details"]:
                print(
                    f"{column['column_name']:30}"
                    f"{column['data_type']:15}"
                    f"{str(column['is_mandatory']):10}"
                    f"{str(column['is_unique']):10}"
                )

        print("\n" + "=" * 100)

        return {"status": "success"}

    except Exception as e:
        print(e)
        return {
            "status": "failed",
            "error": str(e)
        }