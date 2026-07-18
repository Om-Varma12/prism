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

@router.get("/casemaster-count")
def get_casemaster_count(request: Request):
    app = zcatalyst_sdk.initialize(req=request)
    zcql = app.zcql()
    try:
        total = zcql.execute_query("SELECT COUNT(ROWID) as cnt FROM CaseMaster")
        null_dates = zcql.execute_query("SELECT COUNT(ROWID) as cnt FROM CaseMaster WHERE IncidentFromDate IS NULL")
        trends = zcql.execute_query("""
            SELECT
                CaseMaster.IncidentFromDate as date
            FROM CaseMaster
            LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
            LEFT JOIN Unit ON CaseMaster.PoliceStationID = Unit.ROWID
            LEFT JOIN District ON Unit.DistrictID = District.ROWID
            WHERE CaseMaster.IncidentFromDate IS NOT NULL
            LIMIT 300
        """)
        return {
            "total_casemaster": total[0].get("CaseMaster", total[0]).get("cnt"),
            "null_dates": null_dates[0].get("CaseMaster", null_dates[0]).get("cnt"),
            "trends_returned_rows": len(trends),
            "sample_trends": trends[:3] if trends else []
        }
    except Exception as e:
        return {"error": str(e)}