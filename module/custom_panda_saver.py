from pathlib import Path
import sys
from typing import Any
from datetime import datetime
import shutil


def _is_dataframe_like(obj: Any) -> bool:
    """Return True if obj looks like a DataFrame (has a to_csv method)."""
    return hasattr(obj, "to_csv") and callable(obj.to_csv)


def safe_save(
    dataframe: Any,
    output_path: str,
    file_name: str,
    *,
    sep: str = ",",
    encoding: str = "utf-8",
    mode: str = "w",
    header: bool = True,
    index: bool = False,
    **kwargs,
) -> Path | None:
    """
    Write dataframe to a CSV file safely with optional backup.

    If the file already exists, the user is prompted to either:
        - Overwrite it
        - Backup the existing file before writing
        - Cancel the operation

    Returns
    -------
    Path | None
        Path of the file that was written, or None if operation was aborted.
    """

    # 1️⃣ Validate dataframe
    if not _is_dataframe_like(dataframe):
        raise TypeError(
            "First argument must be a pandas DataFrame (or an object with `to_csv`)."
        )

    # 2️⃣ Prepare output directory
    out_dir = Path(output_path).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / file_name

    # 3️⃣ Handle existing file
    if out_file.exists():
        answer = input(
            f"File '{out_file}' already exists. Overwrite (o), backup (b), or cancel (c)? [o/b/c]: "
        ).strip().lower()

        if answer.startswith("b"):  # Backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = out_dir / f"{out_file.stem}_backup_{timestamp}{out_file.suffix}"
            try:
                shutil.move(str(out_file), str(backup_file))
                print(f"💾 Existing file moved to backup: {backup_file}")
            except Exception as exc:
                print(f"❌ Failed to backup existing file: {exc}", file=sys.stderr)
                return None
        elif answer.startswith("o"):  # Overwrite
            pass  # Nothing extra needed
        else:
            print("❌ Skipping save – operation cancelled.")
            return None

    # 4️⃣ Write the new file
    try:
        dataframe.to_csv(
            out_file,
            sep=sep,
            encoding=encoding,
            mode=mode,
            header=header,
            index=index,
            **kwargs,
        )
    except Exception as exc:
        print(f"❌ Error while writing '{out_file}': {exc}", file=sys.stderr)
        return None

    print(f"✅ File written to: {out_file}")
    return out_file
