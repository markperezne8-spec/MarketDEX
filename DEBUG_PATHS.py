"""
Debug script to trace path resolution at runtime
"""
import os
import sys
from pathlib import Path

print("=" * 80)
print("RUNTIME PATH DEBUGGING")
print("=" * 80)

# Show current working directory
print(f"\nos.getcwd() = {os.getcwd()}")
print(f"sys.executable = {sys.executable}")

# Import and trace paths.py
print("\n" + "=" * 80)
print("IMPORTING: app.core.paths")
print("=" * 80)

from app.core import paths

# Show __file__ path in paths.py
print(f"\npaths.__file__ = {paths.__file__}")
print(f"Path(paths.__file__).resolve() = {Path(paths.__file__).resolve()}")

# Calculate what PROJECT_ROOT should be
file_path = Path(paths.__file__).resolve()
print(f"\nManual calculation from paths.py __file__:")
print(f"  .parents[0] = {file_path.parents[0]} (core directory)")
print(f"  .parents[1] = {file_path.parents[1]} (app directory)")
print(f"  .parents[2] = {file_path.parents[2]} (MarketDEX directory)")

# Show actual values from paths module
print("\n" + "=" * 80)
print("VALUES IN app.core.paths MODULE")
print("=" * 80)
print(f"\nPROJECT_ROOT = {paths.PROJECT_ROOT}")
print(f"  type: {type(paths.PROJECT_ROOT)}")
print(f"  is absolute: {paths.PROJECT_ROOT.is_absolute()}")

print(f"\nDATA_DIR = {paths.DATA_DIR}")
print(f"DATABASE_DIR = {paths.DATABASE_DIR}")
print(f"LOG_DIR = {paths.LOG_DIR}")

# Check if these are relative or absolute
print(f"\nDATA_DIR.is_absolute() = {paths.DATA_DIR.is_absolute()}")
print(f"DATABASE_DIR.is_absolute() = {paths.DATABASE_DIR.is_absolute()}")

# Now trace database.py
print("\n" + "=" * 80)
print("IMPORTING: app.database.database")
print("=" * 80)

from app.database import database

print(f"\ndatabase.__file__ = {database.__file__}")
print(f"database.DATABASE_DIR = {database.DATABASE_DIR}")
print(f"database.DB_PATH = {database.DB_PATH}")
print(f"  type: {type(database.DB_PATH)}")
print(f"  is_absolute: {database.DB_PATH.is_absolute()}")

print(f"\nFinal DB_PATH after resolve():")
print(f"  database.DB_PATH.resolve() = {database.DB_PATH.resolve()}")

# Check what actually exists on disk
print("\n" + "=" * 80)
print("FILESYSTEM CHECK")
print("=" * 80)

data_path = Path(os.getcwd()) / "data"
marketdex_data_path = Path("c:\\Projects\\MarketDEX") / "data"
resolved_data_path = database.DATABASE_DIR.parent

print(f"\nChecking for relative './data' directory:")
print(f"  {data_path} exists? {data_path.exists()}")

print(f"\nChecking for absolute data directory:")
print(f"  {marketdex_data_path} exists? {marketdex_data_path.exists()}")

print(f"\nResolved DATABASE_DIR parent:")
print(f"  {resolved_data_path} exists? {resolved_data_path.exists()}")

print("\n" + "=" * 80)
