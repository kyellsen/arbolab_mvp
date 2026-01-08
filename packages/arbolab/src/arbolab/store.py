from pathlib import Path
from typing import Any
import shutil

class VariantStore:
    """
    Manages persistence of Data Variants (Parquet files).
    Enforces the 'write-once' / 'append-only' philosophy for existing variants.
    """
    def __init__(self, variants_root: Path):
        self._root = variants_root
        
    def write_variant(self, 
                      project_id: int, 
                      datastream_id: int, 
                      variant_name: str, 
                      data: Any, # Expecting PyArrow Table or Polars DataFrame
                      clobber: bool = False) -> Path:
        """
        Writes a dataframe to the canonical variant path.
        Returns the relative path from workspace root (conceptually), 
        but implementation returns the absolute path for now.
        
        In a full impl, 'data' would be typed strictly.
        """
        
        # Canonical Structure: project_id=X/datastream_id=Y/
        # File name: {variant_name}.parquet
        
        # Partition-like directory structure
        dir_path = self._root / f"project_id={project_id}" / f"datastream_id={datastream_id}"
        dir_path.mkdir(parents=True, exist_ok=True)
        
        file_path = dir_path / f"{variant_name}.parquet"
        
        if file_path.exists() and not clobber:
             # Idempotency check: In a real system, we might hash the content.
             # MVP: If it exists, we assume it's done. 
             # But if user insists on re-run, they might fail or skip.
             # For explicit re-processing, usually a NEW variant name is preferred.
             # Here we raise to be safe, unless clobber is True.
             raise FileExistsError(f"Variant {variant_name} already exists for datastream {datastream_id}. Use a new variant or force overwrite.")

        # MVP: Support polars/pandas/arrow via protocol or strict types
        # Assuming duckdb/polars relation or arrow table
        
        if hasattr(data, "write_parquet"):
            data.write_parquet(file_path)
        else:
            # Fallback for simple testing if passed a simpler object or try conversion
            raise NotImplementedError("Only objects with write_parquet() (e.g. Polars/Arrow) supported in MVP Store.")
            
        return file_path
