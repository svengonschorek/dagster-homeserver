from .common.trigger_pyspark_job import trigger_pyspark

from dagster import AssetExecutionContext, ResourceDefinition, asset, AssetKey
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
from dagster_airbyte import load_assets_from_airbyte_instance

from typing import Any, Mapping, Optional, Sequence

from .constants import dbt_manifest_path, airbyte_resource

# define spark assets
# ---------------------------------
def create_spark_assets(asset_names):
    assets = []
    def make_asset(name, load_type):

        @asset(
            name=name,
            key_prefix="spark",
            group_name="spark",
            deps=AssetKey(["airbyte", name])
        )
        def generated_asset():
            spark_file_path = "/opt/spark/scripts/extract_load.py"
            trigger_pyspark(spark_file_path, src_name=name, load_type=load_type)
        
        return generated_asset

    for asset_name in asset_names:
        assets.append(make_asset(asset_name["name"], asset_name["load_type"]))
    
    return assets

asset_names = [
    {"name": "s3_binance_klines", "load_type": "incremental"},
    {"name": "s3_binance_orders_spot", "load_type": "full"},
    {"name": "s3_binance_payins", "load_type": "full"},
    {"name": "s3_binance_trades_futures", "load_type": "full"},
    {"name": "s3_binance_trades_spot", "load_type": "full"},
    {"name": "s3_binance_transactions_futures", "load_type": "full"},
    {"name": "s3_binance_transactions_spot", "load_type": "full"},
    {"name": "s3_bybit_botdetails", "load_type": "full"},
    {"name": "s3_bybit_bottrades", "load_type": "full"}
]

spark_assets = create_spark_assets(asset_names)

# define airbyte assets
# ---------------------------------
def connection_to_group(name: str) -> str:
    return 'airbyte'

airbyte_assets = load_assets_from_airbyte_instance(
    airbyte=airbyte_resource,
    key_prefix = ["airbyte"],
    connection_to_group_fn=connection_to_group
)

# define dbt assets
# ---------------------------------
class CustomDagsterDbtTranslator(DagsterDbtTranslator):
    def get_owners(
        self, dbt_resource_props: Mapping[str, Any]
    ) -> Optional[Sequence[str]]:
        return ["sven.gonschorek@bi-solutions-hamburg.com"]
    
    def get_group_name(self, dbt_resource_props: Mapping[str, Any]) -> str | None:
        return "dbt_assets"

@dbt_assets(
    manifest=dbt_manifest_path,
    dagster_dbt_translator=CustomDagsterDbtTranslator()
)
def dwh_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()
