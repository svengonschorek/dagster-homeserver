"""
To add a daily schedule that materializes your dbt assets, uncomment the following lines.
"""
from dagster import ScheduleDefinition, define_asset_job
import dagster as dg

schedules = [
    ScheduleDefinition(
        job = define_asset_job(
            "all_assets",
            selection = "*"
        ),
        cron_schedule = "@daily"
    )
]
