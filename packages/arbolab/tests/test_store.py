"""Tests for VariantStore persistence helpers."""

from __future__ import annotations

from pathlib import Path

import pytest
from arbolab.store import VariantStore


class DummyParquetWriter:
    """Simple object that mimics a dataframe with write_parquet()."""

    def __init__(self, payload: bytes = b"data") -> None:
        """Initialize with payload bytes.

        Args:
            payload: Bytes to write.
        """
        self.payload = payload

    def write_parquet(self, path: Path) -> None:
        """Write payload bytes to the target path.

        Args:
            path: Target file path.
        """
        path.write_bytes(self.payload)


def test_variant_store_write_variant_creates_file(tmp_path: Path) -> None:
    """Writes a variant parquet file to the canonical path.

    Args:
        tmp_path: Temporary directory fixture.
    """
    store = VariantStore(tmp_path)
    data = DummyParquetWriter(b"payload")

    path = store.write_variant(project_id=1, datastream_id=2, variant_name="raw", data=data)

    assert path.exists()
    assert path.read_bytes() == b"payload"
    assert "project_id=1" in str(path)
    assert "datastream_id=2" in str(path)


def test_variant_store_write_variant_existing_raises(tmp_path: Path) -> None:
    """Raises when a variant file already exists and clobber is false.

    Args:
        tmp_path: Temporary directory fixture.
    """
    store = VariantStore(tmp_path)
    data = DummyParquetWriter()

    store.write_variant(project_id=1, datastream_id=2, variant_name="raw", data=data)

    with pytest.raises(FileExistsError):
        store.write_variant(project_id=1, datastream_id=2, variant_name="raw", data=data)


def test_variant_store_write_variant_requires_write_parquet(tmp_path: Path) -> None:
    """Requires a data object implementing write_parquet().

    Args:
        tmp_path: Temporary directory fixture.
    """
    store = VariantStore(tmp_path)

    with pytest.raises(NotImplementedError):
        store.write_variant(project_id=1, datastream_id=2, variant_name="raw", data=object())
