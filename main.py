
import csv
import json
from pathlib import Path


# Project paths
PROJECT_DIR = Path(__file__).resolve().parent
INPUT_FILE = PROJECT_DIR / "data" / "test_data.csv"
OUTPUT_DIR = PROJECT_DIR / "output"

CLEAN_FILE = OUTPUT_DIR / "customers_clean.json"
ERROR_FILE = OUTPUT_DIR / "invalid_rows.json"

REQUIRED_COLUMNS = {"name", "age", "email"}


def clean_name(value):
    return value.strip().title()


def clean_email(value):
    email = value.strip().lower()

    if not email:
        return None

    if "@" not in email:
        return None

    local_part, domain = email.rsplit("@", 1)

    if not local_part or "." not in domain:
        return None

    if domain.startswith(".") or domain.endswith("."):
        return None

    if any(char.isspace() for char in email):
        return None

    return email


def clean_age(value):
    """Convert an age to an integer and check its range."""
    value = value.strip()

    if not value:
        return None

    try:
        age = int(value)
    except ValueError:
        return None

    if age < 0 or age > 120:
        return None

    return age


def clean_row(row):
    errors = []

    # Handle missing values safely
    raw_name = (row.get("name") or "").strip()
    raw_age = (row.get("age") or "").strip()
    raw_email = (row.get("email") or "").strip()

    # Clean name
    if not raw_name:
        name = None
        errors.append("Missing name")
    else:
        name = clean_name(raw_name)

    # Clean age
    age = clean_age(raw_age)

    if age is None:
        errors.append("Missing or invalid age")

    # Clean email
    email = clean_email(raw_email)

    if email is None:
        errors.append("Missing or invalid email")

    cleaned_record = {
        "name": name,
        "age": age,
        "email": email
    }

    return cleaned_record, errors


def write_json(file_path, data):
    """Write Python data to a formatted JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)


def process_csv():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT_FILE}"
        )

    valid_records = []
    invalid_records = []
    seen_emails = set()

    total_rows = 0

    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row")

        # Normalize header names
        reader.fieldnames = [
            (header or "").strip().lower()
            for header in reader.fieldnames
        ]

        if len(set(reader.fieldnames)) != len(reader.fieldnames):
            raise ValueError("CSV contains duplicate column names")

        missing_columns = REQUIRED_COLUMNS - set(reader.fieldnames)

        if missing_columns:
            raise ValueError(
                f"Missing required columns: "
                f"{', '.join(sorted(missing_columns))}"
            )

        for row_number, row in enumerate(reader, start=2):
            total_rows += 1

            cleaned_record, errors = clean_row(row)

            # Detect duplicate emails only when the email is valid
            email = cleaned_record["email"]

            if email is not None:
                if email in seen_emails:
                    errors.append("Duplicate email")
                else:
                    seen_emails.add(email)

            if errors:
                invalid_records.append({
                    "row_number": row_number,
                    "original_data": row,
                    "cleaned_data": cleaned_record,
                    "errors": errors
                })
            else:
                valid_records.append(cleaned_record)

    # Export results
    write_json(CLEAN_FILE, valid_records)
    write_json(ERROR_FILE, invalid_records)

    # Print summary
    print("\nData cleaning completed!")
    print(f"Total rows: {total_rows}")
    print(f"Valid rows: {len(valid_records)}")
    print(f"Invalid rows: {len(invalid_records)}")
    print(f"Clean JSON: {CLEAN_FILE}")
    print(f"Error report: {ERROR_FILE}")


if __name__ == "__main__":
    try:
        process_csv()
    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}")
