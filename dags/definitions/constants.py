import os
from pathlib import Path

from dagster import EnvVar
from dagster_airbyte import AirbyteResource
from dagster_dbt import DbtCliResource

# airbyte constants
# ---------------------------------------------------
airbyte_resource = AirbyteResource(
    host=EnvVar("AIRBYTE_HOST"),
    port=EnvVar("AIRBYTE_PORT"),
    # If using basic auth
    username=EnvVar("AIRBYTE_USERNAME"),
    password=EnvVar("AIRBYTE_PASSWORD"),
)

# dbt constants
# ---------------------------------------------------
dbt_project_dir = Path(__file__).joinpath("..", "dbt-trino-homeserver").resolve()
dbt_profiles_dir = Path(__file__).joinpath("..", "dbt-trino-homeserver", "config").resolve()
dbt_resource = DbtCliResource(
    project_dir=os.fspath(dbt_project_dir),
    profiles_dir=os.fspath(dbt_profiles_dir)
)

# If DAGSTER_DBT_PARSE_PROJECT_ON_LOAD is set, a manifest will be created at run time.
# Otherwise, we expect a manifest to be present in the project's target directory.
if EnvVar("DAGSTER_DBT_PARSE_PROJECT_ON_LOAD"):
    dbt_manifest_path = (
        dbt_resource.cli(
            ["--quiet", "parse"],
            target_path=Path("target"),
        )
        .wait()
        .target_path.joinpath("manifest.json")
    )
else:
    dbt_manifest_path = dbt_project_dir.joinpath("target", "manifest.json")
