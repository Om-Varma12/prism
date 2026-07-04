import zcatalyst_sdk
try:
    app = zcatalyst_sdk.initialize()
    print("Initialized without req!")
    ds = app.datastore()
    tables = ds.get_all_tables()
    for table in tables:
        table_name = table._table_details["table_name"]
        print(table_name)
        metadata = ds.get_table_details(table_name)
        for col in metadata["column_details"]:
            print(f"  {col['column_name']}: {col['data_type']}")
except Exception as e:
    print("Failed:", e)
