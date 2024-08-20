from dagster import AssetExecutionContext, ResourceDefinition
from dagster_dbt import DbtCliResource, dbt_assets, DagsterDbtTranslator
from dagster_airbyte import load_assets_from_airbyte_instance

from typing import Any, Mapping, Optional, Sequence

from .constants import dbt_manifest_path, airbyte_resource

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
