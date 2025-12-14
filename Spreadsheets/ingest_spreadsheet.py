import csv
import os
import re
from pathlib import Path

import pandas as pd

from Cube.letterscheme import sort_face_precedence


def ingest_spreadsheet(file_name: Path, cols_first: bool):
    print("\n=== Starting ingest_spreadsheet ===")
    print(f"File: {file_name}")
    print(f"cols_first: {cols_first}")

    # Skip keywords - if any of these are in the sheet name, skip it
    skip_keywords = [
        "flip",
        "wing",
        "twist",
        "midge",
        "old",
        "2e2e",
        "center",
        "2c",
        "ltct",
        "t2c",
        "info",
        "readme",
    ]

    all_valid_buffers = {
        "UB",
        "UR",
        "UF",
        "UL",
        "LU",
        "LF",
        "LD",
        "LB",
        "FU",
        "FR",
        "FD",
        "FL",
        "RU",
        "RB",
        "RD",
        "RF",
        "BU",
        "BL",
        "BD",
        "BR",
        "DF",
        "DR",
        "DB",
        "DL",
        "UBL",
        "UBR",
        "UFR",
        "UFL",
        "LUB",
        "LUF",
        "LDF",
        "LDB",
        "FUL",
        "FUR",
        "FDR",
        "FDL",
        "RUF",
        "RUB",
        "RDB",
        "RDF",
        "BUR",
        "BUL",
        "BDL",
        "BDR",
        "DFL",
        "DFR",
        "DBR",
        "DBL",
    }
    sorted_buffers = sorted(all_valid_buffers, key=len, reverse=True)
    buffers_regex = "|".join(re.escape(buf) for buf in sorted_buffers)
    buffer_pattern = re.compile(r"^(" + buffers_regex + r")(?:[^A-Za-z]|$)")

    # Try to load Excel file
    try:
        xl_file = pd.ExcelFile(f"Spreadsheets/{file_name}")
        print("✓ Successfully loaded Excel file")
        print(f"Sheet names found: {xl_file.sheet_names}")
    except Exception as e:
        print(f"✗ ERROR loading Excel file: {e}")
        return

    dfs = {}

    # Parse sheets
    for sheet_name in xl_file.sheet_names:
        print(f"\nChecking sheet: '{sheet_name}'")

        # Check for skip keywords
        sheet_lower = sheet_name.lower()
        if any(keyword in sheet_lower for keyword in skip_keywords):
            print(f"  ✗ SKIPPING SHEET '{sheet_name}' - Contains skip keyword")
            continue

        match = buffer_pattern.search(sheet_name)
        if match:
            buffer_name = match.group(1).upper()
            buffer_name = sort_face_precedence(buffer_name)  # Normalize it
            print(
                f"  - Pattern matched: '{match.group(1)}' -> normalized to '{buffer_name}'"
            )
            if buffer_name in all_valid_buffers:
                try:
                    data_frame = xl_file.parse(sheet_name)
                    dfs[buffer_name] = data_frame
                    print(
                        f"  ✓ USING SHEET '{sheet_name}' as buffer '{buffer_name}' - Shape: {data_frame.shape}"
                    )
                except Exception as e:
                    print(f"  ✗ ERROR parsing sheet '{sheet_name}': {e}")
                    print(f"  ✗ SKIPPING SHEET '{sheet_name}' due to error")
            else:
                print(
                    f"  ✗ SKIPPING SHEET '{sheet_name}' - Buffer '{buffer_name}' not in valid list (shouldn't happen)"
                )
        else:
            print(f"  ✗ SKIPPING SHEET '{sheet_name}' - No buffer pattern match")

    if not dfs:
        print("\n✗ No valid buffer sheets found in the spreadsheet")
        return

    # Create output directory
    new_path = f"comms/{file_name}"
    print(f"\nCreating directory: {new_path}")
    try:
        if not os.path.exists(new_path):
            os.makedirs(new_path)
            print("✓ Directory created")
        else:
            print("✓ Directory already exists")
    except Exception as e:
        print(f"✗ ERROR creating directory: {e}")
        return

    print(f"\n{len(dfs)} sheets converted")

    # Save CSVs
    for buffer_name, dataframe in dfs.items():
        csv_path = f"comms/{file_name}/{buffer_name}.csv"
        try:
            dataframe.to_csv(csv_path, index=False)
            print(f"✓ Created {csv_path}")
        except Exception as e:
            print(f"✗ ERROR creating CSV {csv_path}: {e}")

    # Define patterns and functions
    pattern = r"(U|D|R|L|F|B){2,3}"
    sticker_pattern = re.compile(pattern)

    def filter_buffer(cell) -> str:
        if pd.isna(cell):
            return ""
        cell = str(cell).strip()
        match = sticker_pattern.search(cell)
        cell = cell if match is None else match.group().upper()

        if len(cell) == 3:
            return sort_face_precedence(cell)

        return cell

    def parse_header(header):
        if not header:
            return [""], None

        # Filter the first column header too
        first_col_filtered = filter_buffer(header[0]) if header else ""
        return_header = [first_col_filtered]

        # Determine expected length from first non-empty buffer in header (starting from index 1)
        expected_length = None
        for head_index in range(1, len(header)):
            filtered = filter_buffer(header[head_index])
            if filtered and expected_length is None:
                expected_length = len(filtered)
            return_header.append(filtered)

        print(f"  - Header expected buffer length: {expected_length}")
        print(f"  - First column header: '{header[0]}' -> '{first_col_filtered}'")
        return return_header, expected_length

    def parse_row(row, expected_length):
        if not row:
            return []
        row_index, *rest_of_row = row
        row_index = filter_buffer(row_index)

        # Validate row index matches expected length
        if expected_length and row_index and len(row_index) != expected_length:
            return None  # Signal invalid row

        rest_of_row = [str(i).strip() if not pd.isna(i) else "" for i in rest_of_row]
        return [row_index] + rest_of_row

    # Process CSVs
    print("\n=== Processing CSV files ===")
    for buffer_name in dfs.keys():
        csv_path = f"comms/{file_name}/{buffer_name}.csv"
        temp_path = f"comms/{file_name}/temp.csv"

        if not os.path.exists(csv_path):
            print(f"✗ Warning: {csv_path} not found, skipping...")
            continue

        print(f"\nProcessing {buffer_name}...")
        try:
            with (
                open(csv_path, newline="") as csvfile,
                open(temp_path, newline="", mode="w+") as temp_file,
            ):
                reader = csv.reader(csvfile)
                temp_writer = csv.writer(temp_file)
                all_rows = list(reader)

                print(f"  - Read {len(all_rows)} rows")

                if not cols_first:
                    print(f"  - Transposing data (cols_first=False)")
                    num_cols = max(len(row) for row in all_rows) if all_rows else 0
                    print(
                        f"  - Original dimensions: {len(all_rows)} rows x {num_cols} cols"
                    )
                    all_rows = [
                        [row[i] if i < len(row) else "" for row in all_rows]
                        for i in range(num_cols)
                    ]
                    print(f"  - After transpose: {len(all_rows)} rows")

                rows_written = 0
                rows_skipped = 0
                expected_length = None

                for row_num, row in enumerate(all_rows):
                    if len(buffer_name) + row_num > 24:
                        print(
                            f"  - Stopping at row {row_num} (len={len(buffer_name)} + {row_num} > 24)"
                        )
                        break

                    if row_num == 0:
                        parsed, expected_length = parse_header(row)
                        temp_writer.writerow(parsed)
                        print(
                            f"  - Header: {parsed[:5]}..."
                            if len(parsed) > 5
                            else f"  - Header: {parsed}"
                        )
                        rows_written += 1
                    else:
                        # For non-header rows, check if first column matches the pattern
                        first_col = row[0] if row else ""
                        first_col_str = str(first_col).strip()

                        # If first column doesn't have a pattern match at all, stop processing
                        if not sticker_pattern.search(first_col_str):
                            print(
                                f"  - Row {row_num}: First column '{first_col}' doesn't match pattern, stopping row processing"
                            )
                            break

                        # Parse the row and check if length matches
                        parsed = parse_row(row, expected_length)
                        if parsed is None:
                            first_col_filtered = filter_buffer(first_col_str)
                            print(
                                f"  - Row {row_num}: Skipping - first column '{first_col_filtered}' (len={len(first_col_filtered)}) doesn't match expected length {expected_length}"
                            )
                            rows_skipped += 1
                            continue

                        temp_writer.writerow(parsed)
                        rows_written += 1

                print(
                    f"  - Wrote {rows_written} rows, skipped {rows_skipped} rows to temp file"
                )

            os.remove(csv_path)
            os.rename(temp_path, csv_path)
            print(f"✓ Finished processing {buffer_name}")

        except Exception as e:
            print(f"✗ ERROR processing {buffer_name}: {e}")
            import traceback

            print(traceback.format_exc())

    print("\n=== ingest_spreadsheet complete ===\n")
