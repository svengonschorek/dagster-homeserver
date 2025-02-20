from .common.trigger_pyspark_job import trigger_pyspark

from dagster import AssetExecutionContext, ResourceDefinition, asset
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
from dagster_airbyte import load_assets_from_airbyte_instance

from typing import Any, Mapping, Optional, Sequence

from .constants import dbt_manifest_path, airbyte_resource

# define spark assets
# ---------------------------------
def create_dynamic_spark_assets(asset_names):
    assets = []
    
    for name in asset_names:
        @asset(name=name, group_name="spark")
        def generated_asset():
            spark_file_path = "/opt/spark/scripts/extract_load.py"
            job_args = name
            trigger_pyspark(spark_file_path, args=job_args)
        
        assets.append(generated_asset)
    
    return assets

asset_names = [
    "s3_binance_orders_spot",
    "s3_binance_payins",
    "s3_binance_trades_futures",
    "s3_binance_trades_spot",
    "s3_binance_transactions_futures",
    "s3_binance_transactions_spot",
    "s3_bybit_botdetails",
    "s3_bybit_bottrades"
]

spark_assets = create_dynamic_spark_assets(asset_names)

# define airbyte assets
# ---------------------------------
airbyte_assets = load_assets_from_airbyte_instance(
    airbyte=airbyte_resource,
    key_prefix = ["binance"],
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
