# ------------------------------------------------------------------
# safe_saving.py
# ------------------------------------------------------------------
"""
Utility that writes a Pandas (or Pandas‑compatible) DataFrame to disk
only after confirming that the target file can be overwritten.

The function signature is deliberately minimal:

    safe_save(dataframe, output_path, file_name, **kwargs)

* `dataframe` – must be a pandas DataFrame (or an object that offers a
  ``to_csv`` method).  A TypeError is raised if this is not the case.
* `output_path` – directory (string or Path) where the file should live.
* `file_name`   – file name (string, no path component).

Optional keyword arguments are forwarded directly to
``dataframe.to_csv`` (sep, encoding, header, index, …).
"""

from pathlib import Path
import sys
from typing import Any, Dict, Tuple, Optional

def _is_dataframe_like(obj: Any) -> bool:
    """
    Very small helper – returns True if *obj* looks like a DataFrame.
    The test is purposely lightweight: it checks for a ``to_csv`` method.
    """
    return hasattr(obj, "to_csv") and callable(obj.to_csv)


def safe_save(
    dataframe: Any,
    output_path: str,
    file_name: str,
    *,
    sep: str = "\t",
    encoding: str = "utf-8",
    mode: str = "w",
    header: bool = True,
    index: bool = False,
    **kwargs,
) -> bool:
    """
    Write *dataframe* to a CSV/TSV file, prompting the user before
    overwriting an existing file.

    Parameters
    ----------
    dataframe : Any
        Pandas DataFrame (or object that implements ``to_csv``).
    output_path : str or Path
        Directory where the file should be written.
    file_name : str
        File name (no directory component).
    sep : str, optional
        Field separator – defaults to tab.
    encoding : str, optional
        Text encoding – defaults to UTF‑8.
    mode : str, optional
        File mode – ``"w"`` (write) or ``"a"`` (append).  Default: ``"w"``.
    header : bool, optional
        Whether to write column names.  Default: ``True``.
    index : bool, optional
        Whether to write row indices.  Default: ``False``.
    **kwargs
        Any other keyword arguments forwarded to ``dataframe.to_csv``.
    Returns
    -------
    bool
        ``True`` if the file was written, ``False`` if the operation was
        aborted or failed.
    """

    # ------------------------------------------------------------------
    # 1️⃣  Validate the first argument
    # ------------------------------------------------------------------
    if not _is_dataframe_like(dataframe):
        raise TypeError(
            "First argument must be a pandas DataFrame (or an object that implements `to_csv`)."
        )

    # ------------------------------------------------------------------
    # 2️⃣  Resolve the full file path
    # ------------------------------------------------------------------
    out_dir = Path(output_path).expanduser().resolve()
    out_file = out_dir / file_name

    # Create the directory if it does not exist
    out_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 3️⃣  Prompt the user if the file already exists
    # ------------------------------------------------------------------
    if out_file.exists():
        answer = input(
            f"File '{out_file}' already exists. Overwrite? (y/n): "
        ).strip().lower()
        if not answer.startswith("y"):
            print("Skipping save – user declined to overwrite.")
            return False  # No write performed

    # ------------------------------------------------------------------
    # 4️⃣  Attempt the write operation
    # ------------------------------------------------------------------
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
        return False

    print(f"✅ File written to: {out_file}")
    return out_file