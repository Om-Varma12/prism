"""
Crime forecasting using Prophet for trend prediction.

This module provides the Forecaster class that uses Facebook Prophet
to generate 30-day crime forecasts based on historical data.
"""
from datetime import datetime, timedelta
from typing import Optional
import pandas as pd


class Forecaster:
    """
    Forecasts crime trends using Facebook Prophet.
    
    Trains Prophet models on historical crime data and generates
    30-day forecasts with confidence intervals.
    """

    def __init__(self):
        pass

    def train_model(
        self,
        historical_data: list[dict],
    ) -> Optional[object]:
        """
        Train a Prophet model on historical crime data.
        
        Args:
            historical_data: List of dictionaries with 'date' and 'count' keys
        
        Returns:
            Trained Prophet model or None if training fails
        """
        if not historical_data or len(historical_data) < 2:
            return None

        try:
            from prophet import Prophet
            
            # Convert to DataFrame
            df = pd.DataFrame(historical_data)
            
            # Rename columns for Prophet
            df = df.rename(columns={"date": "ds", "count": "y"})
            
            # Ensure date column is datetime
            df["ds"] = pd.to_datetime(df["ds"])
            
            # Sort by date
            df = df.sort_values("ds")
            
            # Create and train Prophet model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                interval_width=0.8,  # 80% confidence interval
            )
            
            model.fit(df)
            
            return model
        except ImportError:
            print("[Warning] Prophet library not installed. Install with: pip install prophet")
            return None
        except Exception as exc:
            print(f"[Warning] Failed to train Prophet model: {exc}")
            return None

    def generate_forecast(
        self,
        model: object,
        days: int = 30,
    ) -> list[dict]:
        """
        Generate forecast using trained Prophet model.
        
        Args:
            model: Trained Prophet model
            days: Number of days to forecast (default: 30)
        
        Returns:
            List of forecast dictionaries with date, predicted_value,
            lower_bound, and upper_bound
        """
        if model is None:
            return []

        try:
            from prophet import Prophet
            
            # Create future dataframe
            future = model.make_future_dataframe(periods=days)
            
            # Generate forecast
            forecast = model.predict(future)
            
            # Extract forecast data (only the future periods)
            forecast_data = []
            historical_length = len(model.history)
            
            for i in range(historical_length, len(forecast)):
                row = forecast.iloc[i]
                forecast_data.append({
                    "date": row["ds"].strftime("%Y-%m-%d"),
                    "predicted_value": int(round(row["yhat"])),
                    "lower_bound": int(round(row["yhat_lower"])),
                    "upper_bound": int(round(row["yhat_upper"])),
                })
            
            return forecast_data
        except Exception as exc:
            print(f"[Warning] Failed to generate forecast: {exc}")
            return []

    def forecast_crime_category(
        self,
        historical_data: list[dict],
        crime_category: str,
        days: int = 30,
    ) -> dict:
        """
        Generate forecast for a specific crime category.
        
        Args:
            historical_data: List of dictionaries with 'date' and 'count' keys
            crime_category: Name of the crime category
            days: Number of days to forecast (default: 30)
        
        Returns:
            Dictionary with crime_category, forecast_data, and metadata
        """
        model = self.train_model(historical_data)
        forecast_data = self.generate_forecast(model, days)
        
        return {
            "crime_category": crime_category,
            "forecast_data": forecast_data,
            "generated_at": datetime.utcnow().isoformat(),
            "forecast_days": days,
        }
