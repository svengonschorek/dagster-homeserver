# CLAUDE.md - Dagster Project Guide

## Commands
- **Start Environment**: `docker-compose up -d`
- **Stop Environment**: `docker-compose down`
- **View Logs**: `docker-compose logs -f [service_name]`
- **Rebuild Container**: `docker-compose build [service_name]`
- **Run CLI**: `dagster dev -f dags/definitions/definitions.py`
- **Run Tests**: `python -m pytest tests/`
- **Run Single Test**: `python -m pytest tests/path_to_test.py::test_function_name`
- **Lint Code**: `flake8 dags/`
- **Check Types**: `mypy dags/`

## Code Style Guidelines
- **Imports**: Group imports by standard lib, third-party, then local. Sort alphabetically within groups.
- **Typing**: Use type hints for function parameters and return types. Import types from `typing`.
- **Naming**: Use snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants.
- **Asset Definition**: Group assets by type (e.g., spark_assets, airbyte_assets, dbt_assets).
- **Error Handling**: Use appropriate exception handling. Log errors with `get_dagster_logger()`.
- **Documentation**: Add docstrings to functions and classes. Document parameter types and descriptions.
- **Function Length**: Keep functions focused and under 50 lines when possible.
- **Whitespace**: Use 4 spaces for indentation. Add blank lines between logical sections.
