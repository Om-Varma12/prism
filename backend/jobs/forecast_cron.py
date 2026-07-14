"""
Cron job script for generating crime forecasts using Prophet.

This script runs daily at 2 AM to generate 30-day forecasts for each
crime category and stores the results in the crime_forecasts table.
"""
import zcatalyst_sdk
from datetime import datetime
from analytics.forecasting import Forecaster
from analytics.trends import TREND_CATEGORIES


def fetch_historical_data(zcql, crime_category: str) -> list[dict]:
    """
    Fetch historical crime data for a specific category.
    
    Args:
        zcql: ZCQL client instance
        crime_category: Name of the crime category from TREND_CATEGORIES
    
    Returns:
        List of dictionaries with 'date' and 'count' keys
    """
    # Get crime types for this category
    crime_types = TREND_CATEGORIES.get(crime_category, [])
    
    if not crime_types:
        return []
    
    # Build query with IN clause for multiple crime types
    crime_types_str = "', '".join(crime_types)
    query = f"""
        SELECT
            DATE(CaseMaster.IncidentFromDate) as date,
            COUNT(*) as count
        FROM CaseMaster
        LEFT JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.ROWID
        WHERE CrimeSubHead.CrimeHeadName IN ('{crime_types_str}')
        AND CaseMaster.IncidentFromDate IS NOT NULL
        GROUP BY DATE(CaseMaster.IncidentFromDate)
        ORDER BY date ASC
        LIMIT 300
    """
    
    result = zcql.execute_query(query)
    rows = result if isinstance(result, list) else []
    
    return [
        {
            "date": row.get("date"),
            "count": row.get("count", 0),
        }
        for row in rows
    ]


def store_forecast(datastore, forecast_data: dict):
    """
    Store forecast results in the crime_forecasts table.
    
    Args:
        datastore: Catalyst datastore instance
        forecast_data: Dictionary with crime_category, forecast_data, and metadata
    """
    try:
        # Delete existing forecasts for this category
        table = datastore.table("crime_forecasts")
        existing = table.get_records()
        for record in existing:
            if record.get("crime_category") == forecast_data["crime_category"]:
                table.delete_record(record.get("ROWID"))
        
        # Insert new forecast records
        for forecast_point in forecast_data["forecast_data"]:
            table.insert_record({
                "crime_category": forecast_data["crime_category"],
                "forecast_date": forecast_point["date"],
                "predicted_value": forecast_point["predicted_value"],
                "lower_bound": forecast_point["lower_bound"],
                "upper_bound": forecast_point["upper_bound"],
                "generated_at": forecast_data["generated_at"],
                "forecast_days": forecast_data["forecast_days"],
            })
        
        print(f"[Forecast] Stored {len(forecast_data['forecast_data'])} forecast points for {forecast_data['crime_category']}")
    except Exception as exc:
        print(f"[Error] Failed to store forecast for {forecast_data['crime_category']}: {exc}")


def generate_all_forecasts():
    """
    Main function to generate forecasts for all crime categories.
    
    This function is called by the Cron job scheduler.
    """
    print("[Forecast] Starting forecast generation...")
    
    try:
        # Initialize Catalyst SDK
        catalyst_app = zcatalyst_sdk.initialize()
        zcql = catalyst_app.zcql()
        datastore = catalyst_app.datastore()
        
        # Initialize forecaster
        forecaster = Forecaster()
        
        # Generate forecasts for each crime category
        for crime_category in TREND_CATEGORIES.keys():
            print(f"[Forecast] Processing category: {crime_category}")
            
            # Fetch historical data
            historical_data = fetch_historical_data(zcql, crime_category)
            
            if len(historical_data) < 2:
                print(f"[Forecast] Insufficient data for {crime_category}, skipping")
                continue
            
            # Generate forecast
            forecast_result = forecaster.forecast_crime_category(
                historical_data,
                crime_category,
                days=30,
            )
            
            # Store forecast
            store_forecast(datastore, forecast_result)
        
        print("[Forecast] Forecast generation completed successfully")
        return {"status": "success", "categories_processed": len(TREND_CATEGORIES)}
    
    except Exception as exc:
        print(f"[Error] Forecast generation failed: {exc}")
        return {"status": "error", "message": str(exc)}


if __name__ == "__main__":
    # Run forecast generation when script is executed directly
    result = generate_all_forecasts()
    print(result)
