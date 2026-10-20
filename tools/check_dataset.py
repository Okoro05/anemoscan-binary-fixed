"""Check a photos folder and a hemoglobin CSV for problems BEFORE opening Colab.

Usage: python tools/check_dataset.py PHOTOS_FOLDER HEMOGLOBIN.csv [--image-only]
"""

import csv
import re
import statistics
import sys
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
ALIASES = {
    "patient_id": ["patientid", "patient", "id"],
    "image": ["image_name", "filename", "file_name", "file", "photo"],
    "hb": ["hb_value", "hb_values", "hemoglobin", "haemoglobin", "hb_g_dl", "hb_level"],
    "gender": ["sex"],
    "age": ["age_years", "age_yrs"],
}


def parse_number(raw, what):
    match = re.search(r"[-+]?\d*\.?\d+", str(raw).replace(",", "."))
    if not match:
        raise ValueError(f"no number found in the {what} value {raw!r}")
    return float(match.group())


def parse_gender(raw):
    text = str(raw).strip().lower()
    if text in ("m", "male"):
        return "male"
    if text in ("f", "female"):
        return "female"
    raise ValueError(f"cannot read gender value {raw!r} (use Male or Female)")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    image_only = "--image-only" in sys.argv
    if len(args) != 2:
        print(__doc__)
        return 2
    photos_dir, csv_path = Path(args[0]), Path(args[1])
    if not photos_dir.is_dir() or not csv_path.is_file():
        print("Check the two paths: the photos folder and the CSV file must both exist.")
        return 2

    names = [p.name for p in photos_dir.rglob("*") if p.suffix.lower() in IMG_EXTS]
    by_lower = {n.lower(): n for n in names}
    by_compact = {re.sub(r"\s+", "", n.lower()): n for n in names}
    by_stem = {Path(n).stem.lower(): n for n in names}

    def resolve(name):
        key = str(name).strip()
        compact = re.sub(r"\s+", "", key.lower())
        for table, probe in ((by_lower, key.lower()), (by_compact, compact), (by_stem, Path(compact).stem)):
            if probe in table:
                return table[probe]
        return None

    with open(csv_path, newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        print("The CSV has no rows.")
        return 1

    columns = {re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_"): c for c in rows[0].keys()}
    for target, aliases in ALIASES.items():
        if target not in columns:
            for alias in aliases:
                if alias in columns:
                    columns[target] = columns[alias]
                    break
    required = ["patient_id", "image", "hb"] + ([] if image_only else ["gender", "age"])
    missing = [c for c in required if c not in columns]
    if missing:
        print(f"MISSING COLUMNS: {missing}. Your CSV has: {list(rows[0].keys())}")
        return 1

    good, problems = [], []
    for index, row in enumerate(rows):
        sheet_row = index + 2
        try:
            fname = resolve(row[columns["image"]])
            if fname is None:
                raise ValueError(f"the photo {row[columns['image']]!r} was not found in {photos_dir}")
            record = {"patient": row[columns["patient_id"]].strip() or Path(fname).stem, "image": fname,
                      "hb": parse_number(row[columns["hb"]], "hb")}
            if not 2 <= record["hb"] <= 25:
                raise ValueError(f"hb {record['hb']} is outside the believable range of 2 to 25 g/dL")
            if not image_only:
                record["age"] = parse_number(row[columns["age"]], "age")
                if not 0 <= record["age"] <= 120:
                    raise ValueError(f"age {record['age']} is outside the believable range of 0 to 120")
                record["gender"] = parse_gender(row[columns["gender"]])
            good.append(record)
        except ValueError as error:
            problems.append((sheet_row, str(error)))

    print(f"\nPhotos found: {len(names)}    CSV rows: {len(rows)}    Usable rows: {len(good)}")
    if problems:
        print(f"\n{len(problems)} problem row(s):")
        for sheet_row, message in problems:
            print(f"  row {sheet_row}: {message}")

    used = {g["image"] for g in good}
    unused = sorted(set(names) - used)
    if unused:
        print(f"\n{len(unused)} photo(s) are not listed in the CSV (they will be ignored).")

    warnings = []
    if good:
        hb = [g["hb"] for g in good]
        print(f"\nPatients: {len({g['patient'] for g in good})}")
        print(f"Hb (g/dL): min {min(hb):.1f}  max {max(hb):.1f}  mean {statistics.mean(hb):.2f}")
        if len(good) < 100:
            warnings.append(f"Only {len(good)} usable photos.")
        if max(hb) - min(hb) < 3:
            warnings.append("The Hb values span less than 3 g/dL.")
    if warnings:
        print("\nTHINGS TO KNOW:")
        for warning in warnings:
            print(f"  - {warning}")

    if problems or len(good) < 10:
        print("\nResult: fix the problems above, then run this check again.")
        return 1
    print("\nResult: the files are ready for Colab.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
