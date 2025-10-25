# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
import os
from .ai_search import AISearchConnector
from .open_ai import OpenAIConnector


class ConnectorFactory:
    @staticmethod
    def get_database_connector():
        try:
            if os.environ["Text2Sql__DatabaseEngine"].upper() == "DATABRICKS":
                from .databricks_sql import (
                    DatabricksSqlConnector,
                )

                return DatabricksSqlConnector()
            elif os.environ["Text2Sql__DatabaseEngine"].upper() == "SNOWFLAKE":
                from .snowflake_sql import (
                    SnowflakeSqlConnector,
                )

                return SnowflakeSqlConnector()
            elif os.environ["Text2Sql__DatabaseEngine"].upper() == "TSQL":
                from .tsql_sql import TsqlSqlConnector

                return TsqlSqlConnector()
            elif os.environ["Text2Sql__DatabaseEngine"].upper() == "POSTGRES":
                from .postgres_sql import (
                    PostgresSqlConnector,
                )

                return PostgresSqlConnector()
            elif os.environ["Text2Sql__DatabaseEngine"].upper() == "SQLITE":
                from .sqlite_sql import SQLiteSqlConnector

                return SQLiteSqlConnector()
            else:
                raise ValueError(
                    f"""Database engine {
                        os.environ['Text2Sql__DatabaseEngine']} not found"""
                )
        except ImportError:
            raise ValueError(
                f"""Failed to import {
                    os.environ['Text2Sql__DatabaseEngine']} SQL Connector. Check you have installed the optional dependencies for this database engine."""
            )

    @staticmethod
    def get_ai_search_connector():
        # Return None if AI Search is disabled
        if os.environ.get("Text2Sql__UseAISearch", "True").lower() != "true":
            return None
        return AISearchConnector()

    @staticmethod
    def get_open_ai_connector():
        return OpenAIConnector()
