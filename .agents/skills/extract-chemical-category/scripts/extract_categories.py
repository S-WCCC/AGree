import csv
import sys
from pathlib import Path

CATEGORY_CANDIDATES = [
    'functional_category',
    'chemical_category',
    'use_category',
    'category',
    'function_category',
    'application_category',
    'class',
    'application',
    'function',
    'use',
]

IDENTIFIER_CANDIDATES = [
    'name',
    'chemical_name',
    'compound_name',
    'cas',
    'cas_number',
    'pubchem_cid',
    'cid',
    'smiles',
    'inchikey',
    'inchi',
]


def normalize_header(value: str) -> str:
    return value.strip().lower().replace(' ', '_')


def choose_columns(fieldnames: list[str], candidates: list[str]) -> list[str]:
    normalized = {normalize_header(name): name for name in fieldnames}
    chosen = []
    for candidate in candidates:
        if candidate in normalized:
            chosen.append(normalized[candidate])
    return chosen


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: extract_categories.py <input.csv> [output.csv]')
        return 2

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f'Input CSV not found: {input_path}')
        return 2

    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_name(input_path.stem + '_categories.csv')

    with input_path.open('r', encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print('CSV has no header row')
            return 2

        identifier_cols = choose_columns(reader.fieldnames, IDENTIFIER_CANDIDATES)
        category_cols = choose_columns(reader.fieldnames, CATEGORY_CANDIDATES)

        if not category_cols:
            print('No likely category columns found.')
            print('Available columns:')
            for name in reader.fieldnames:
                print(f'- {name}')
            return 1

        output_fields = identifier_cols + category_cols
        if 'normalized_category' not in output_fields:
            output_fields.append('normalized_category')

        rows = []
        for row in reader:
            out = {key: row.get(key, '') for key in identifier_cols + category_cols}
            first_category = ''
            for col in category_cols:
                value = (row.get(col) or '').strip()
                if value:
                    first_category = value
                    break
            out['normalized_category'] = first_category.strip().lower() if first_category else ''
            rows.append(out)

    with output_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()
        writer.writerows(rows)

    print(f'Input: {input_path}')
    print(f'Detected category columns: {", ".join(category_cols)}')
    print(f'Output: {output_path}')
    print(f'Rows written: {len(rows)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
