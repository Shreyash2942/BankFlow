"""Shared Iceberg catalog, merge, and quality helpers for BankFlow Gold jobs."""

from __future__ import annotations

import re

DEFAULT_CATALOG = "bankflow"
DEFAULT_SILVER_NAMESPACE = "silver"
DEFAULT_GOLD_NAMESPACE = "gold"
DEFAULT_METASTORE_URI = "thrift://localhost:9083"
DEFAULT_WAREHOUSE = "hdfs://localhost:9000/bankflow/lakehouse"
DEFAULT_NAMESPACE_LOCATION = "hdfs://localhost:9000/bankflow/gold"
SQL_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def validate_identifiers(config, *names: str) -> None:
    for name in names:
        if not SQL_IDENTIFIER.fullmatch(getattr(config, name)):
            raise ValueError(f"{name} must be a safe SQL identifier.")


def validate_runtime_settings(config) -> None:
    for name in ("metastore_uri", "warehouse", "namespace_location", "app_name"):
        value = getattr(config, name)
        if not value.strip() or "'" in value:
            raise ValueError(f"{name} must be non-blank and must not contain a quote.")
    if not config.metastore_uri.startswith("thrift://"):
        raise ValueError("metastore_uri must use thrift://.")
    for name in ("warehouse", "namespace_location"):
        if not getattr(config, name).startswith("hdfs://"):
            raise ValueError(f"{name} must use shared HDFS storage.")


def namespace_sql(config) -> str:
    return (
        f"CREATE NAMESPACE IF NOT EXISTS {config.catalog}.{config.gold_namespace} "
        f"LOCATION '{config.namespace_location}'"
    )


def merge_upsert_sql(
    identifier: str,
    columns: dict[str, str],
    view_name: str,
    keys: tuple[str, ...],
) -> str:
    if not SQL_IDENTIFIER.fullmatch(view_name):
        raise ValueError("view_name must be a safe SQL identifier.")
    if not keys or any(not SQL_IDENTIFIER.fullmatch(key) for key in keys):
        raise ValueError("keys must contain safe SQL identifiers.")
    if any(key not in columns for key in keys):
        raise ValueError("Every merge key must be present in columns.")
    join = " AND ".join(f"target.{key} = source.{key}" for key in keys)
    updates = ", ".join(
        f"target.{column} = source.{column}" for column in columns if column not in keys
    )
    names = ", ".join(columns)
    values = ", ".join(f"source.{column}" for column in columns)
    return f"""
MERGE INTO {identifier} AS target
USING {view_name} AS source
ON {join}
WHEN MATCHED THEN UPDATE SET {updates}
WHEN NOT MATCHED THEN INSERT ({names}) VALUES ({values})
""".strip()


def build_spark_session(config):
    from pyspark.sql import SparkSession

    spark = (
        SparkSession.builder.appName(config.app_name)
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.sql.shuffle.partitions", "4")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config(
            f"spark.sql.catalog.{config.catalog}",
            "org.apache.iceberg.spark.SparkCatalog",
        )
        .config(f"spark.sql.catalog.{config.catalog}.type", "hive")
        .config(f"spark.sql.catalog.{config.catalog}.uri", config.metastore_uri)
        .config(f"spark.sql.catalog.{config.catalog}.warehouse", config.warehouse)
        .config(
            f"spark.sql.catalog.{config.catalog}.io-impl",
            "org.apache.iceberg.hadoop.HadoopFileIO",
        )
        .getOrCreate()
    )
    try:
        (
            spark._jvm.Thread.currentThread()  # noqa: SLF001
            .getContextClassLoader()
            .loadClass("org.apache.iceberg.spark.SparkCatalog")
        )
    except Exception as exc:
        spark.stop()
        raise RuntimeError("The installed Iceberg Spark runtime is required.") from exc
    spark.sparkContext.setLogLevel(config.log_level)
    return spark


def validate_table_schema(spark, identifier: str, expected: dict[str, str]) -> None:
    actual = {field.name: field.dataType.simpleString() for field in spark.table(identifier).schema}
    if actual != expected:
        raise RuntimeError(f"Existing table {identifier} does not match Day 20 schema: {actual!r}.")


def quality_violation_counts(dataframe, rules: dict[str, str]) -> dict[str, int]:
    """Return rule failure counts and fail the job when any Gold invariant is broken."""
    from pyspark.sql import functions as F

    expressions = [
        F.sum(F.when(F.expr(predicate), 1).otherwise(0)).cast("long").alias(name)
        for name, predicate in rules.items()
    ]
    result = dataframe.agg(*expressions).first().asDict() if expressions else {}
    counts = {name: int(result.get(name) or 0) for name in rules}
    failures = {name: count for name, count in counts.items() if count}
    if failures:
        raise RuntimeError(f"Gold quality checks failed: {failures!r}.")
    return counts
