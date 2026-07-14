# Analytics & Patterns Page - Setup Guide

This document provides setup instructions for the Analytics & Patterns page dependencies and Cron job configuration.

## Dependencies Installation

### Prophet (Forecasting)

Prophet is required for generating 30-day crime forecasts. Install it with:

```bash
pip install prophet
```

Prophet requires:
- Python 3.8 or higher
- pandas
- numpy
- matplotlib
- cmdstanpy (automatically installed with Prophet)

### scikit-learn (DBSCAN Clustering)

scikit-learn is required for spatial hotspot clustering using DBSCAN:

```bash
pip install scikit-learn
```

### pandas (Data Manipulation)

pandas is required for data manipulation in both forecasting and aggregation:

```bash
pip install pandas
```

### All Analytics Dependencies

To install all required dependencies at once:

```bash
pip install prophet scikit-learn pandas
```

## Cron Job Setup

The forecast generation Cron job should run daily at 2 AM to generate fresh 30-day forecasts for each crime category.

### Cron Job Script

The Cron job script is located at: `backend/jobs/forecast_cron.py`

### Manual Execution

To run the forecast generation manually:

```bash
cd backend
python jobs/forecast_cron.py
```

### Scheduling with Cron (Linux)

Add the following line to your crontab (`crontab -e`):

```
0 2 * * * cd /path/to/prism/backend && python jobs/forecast_cron.py >> /var/log/prism-forecast.log 2>&1
```

### Scheduling with Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task
3. Set trigger to daily at 2:00 AM
4. Set action to run: `python`
5. Add arguments: `jobs/forecast_cron.py`
6. Set "Start in" to the backend directory path

### Catalyst Cron (Recommended for Production)

If deploying to Zoho Catalyst, use the built-in Cron job feature:

1. Navigate to Catalyst Console
2. Go to Cron Jobs
3. Create a new job
4. Set schedule to daily at 2:00 AM
5. Set command: `python jobs/forecast_cron.py`
6. Set working directory to the backend folder

## Database Table Setup

The `crime_forecasts` table must exist in the Catalyst Datastore before running the Cron job. The schema is documented in `backend/db/db-table-schema.md` under section 9.6.

### Manual Table Creation (if needed)

If the table doesn't exist, create it with the following columns:
- `ROWID` (INT, Primary Key)
- `crime_category` (VARCHAR)
- `forecast_date` (DATE)
- `predicted_value` (INT)
- `lower_bound` (INT)
- `upper_bound` (INT)
- `generated_at` (DATETIME)
- `forecast_days` (INT)

## Verification

After setup, verify the system is working:

1. **Test Prophet Installation**: Run `python -c "from prophet import Prophet; print('Prophet installed successfully')"`
2. **Test DBSCAN Installation**: Run `python -c "from sklearn.cluster import DBSCAN; print('DBSCAN installed successfully')"`
3. **Run Manual Forecast**: Execute `python jobs/forecast_cron.py` and check for errors
4. **Check Database**: Verify `crime_forecasts` table is populated with forecast data
5. **Test API Endpoints**: Call `/api/analytics/trends` to ensure forecast data is returned

## Troubleshooting

### Prophet Import Error

If you get an import error for Prophet, ensure you have the correct version of cmdstanpy:

```bash
pip install --upgrade cmdstanpy
```

### DBSCAN Memory Error

If DBSCAN clustering fails due to memory issues, reduce the sample size in the hotspot query by lowering the LIMIT value in `routers/analytics.py`.

### Cron Job Not Running

Check the Cron job logs for errors. Common issues:
- Python path not found (use full path to python executable)
- Working directory not set (use absolute paths or set working directory)
- Database connection issues (verify Catalyst credentials)
