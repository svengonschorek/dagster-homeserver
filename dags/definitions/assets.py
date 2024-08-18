from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, dbt_assets
from dagster_airbyte import load_assets_from_airbyte_instance

from .constants import dbt_manifest_path, airbyte_instance

airbyte_assets = load_assets_from_airbyte_instance(
    airbyte_instance,
    key_prefix = ["binance"]
)

@dbt_assets(manifest=dbt_manifest_path)
def dwh_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
