import os

from dagster import Definitions
from dagster_dbt import DbtCliResource

from .assets import dwh_dbt_assets, airbyte_assets
from .constants import dbt_project_dir
from .schedules import schedules

defs = Definitions(
    assets = [airbyte_assets, dwh_dbt_assets],
    resources = {
        "dbt": DbtCliResource(project_dir = os.fspath(dbt_project_dir))
    },
    schedules = schedules
)
