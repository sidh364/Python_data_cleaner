# CSV-JSON Cleaner

A small Python utility that reads customer data from a CSV file, cleans and validates each row, and exports the results as JSON.

## Features

- Trims whitespace from values.
- Formats names in title case.
- Normalizes email addresses to lowercase.
- Validates email structure.
- Converts ages to integers and accepts values from 0 through 120.
- Detects duplicate valid email addresses.
- Separates valid records from invalid rows.
- Reports the original data, cleaned data, and validation errors for each invalid row.

## Project structure

```text
CSV-JSON_Cleaner/
├── main.py
├── data/
│   └── test_data.csv
└── output/
    ├── customers_clean.json
    └── invalid_rows.json
```

## Requirements

- Python 3.8 or later
- No third-party packages

## Input format

Place the source file at `data/test_data.csv`. The CSV must contain these required columns:

```csv
name,email,age
Alice,alice@example.com,30
```

Column names are normalized by trimming whitespace and converting them to lowercase. Missing required columns, duplicate column names, or a missing header row stop processing with an error.

## Run the cleaner

From the `CSV-JSON_Cleaner` directory, run:

```bash
python main.py
```

The script creates the `output` directory when needed and overwrites the output JSON files on each run.

## Output files

### `output/customers_clean.json`

Contains records that pass all validation checks:

```json
[
    {
        "name": "Alice",
        "age": 30,
        "email": "alice@example.com"
    }
]
```

### `output/invalid_rows.json`

Contains every row with one or more errors. Each entry includes:

- `row_number`: the CSV row number, including the header row
- `original_data`: values read from the CSV
- `cleaned_data`: the values after cleaning, including `null` for invalid fields
- `errors`: the validation messages for that row

Example:

```json
[
    {
        "row_number": 3,
        "original_data": {
            "name": "Bob",
            "email": "bob@example.com",
            "age": "not-a-number"
        },
        "cleaned_data": {
            "name": "Bob",
            "age": null,
            "email": "bob@example.com"
        },
        "errors": [
            "Missing or invalid age"
        ]
    }
]
```

The script also prints a summary containing the total, valid, and invalid row counts and the paths to both output files.
