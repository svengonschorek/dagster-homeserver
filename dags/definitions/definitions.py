import os
import dagster as dg
from dagster import Definitions

from .assets import dwh_dbt_assets, airbyte_assets, spark_assets
from .constants import dbt_resource, airbyte_resource
from .schedules import schedules

defs = Definitions(
    assets = [
        airbyte_assets,
        dwh_dbt_assets,
        *spark_assets
    ],
    resources = {
        "dbt": dbt_resource
    },
    schedules = schedules,
    executor=dg.multiprocess_executor.configured({"max_concurrent": 1})
)
