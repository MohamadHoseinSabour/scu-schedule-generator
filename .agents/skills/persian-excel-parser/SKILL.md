---
name: persian-excel-parser
description: Specialized rules, algorithms, and best practices for parsing university and Persian/Arabic Excel reports with merged cells, Persian/Arabic numerals, and multi-line schedule cells.
---

# Persian Excel Parser Skill

This skill documents how to reliably extract and normalize Persian university academic schedule reports (specifically SCU/Golestan/Sama formats).

## 1. Persian & Arabic Digit Normalization
Never process Persian (`۰-۹`) or Eastern Arabic (`٠-٩`) digits directly in math, time parsing, or database queries. Always normalize to ASCII (`0-9`):

```python
PERSIAN_TO_ASCII = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def normalize_digits(text: str) -> str:
    if not text:
        return ""
    return str(text).translate(PERSIAN_TO_ASCII)
```

## 2. Text Normalization
- Replace Arabic characters: `ي` -> `ی` and `ك` -> `ک`.
- Normalize or strip Zero-Width Non-Joiner (ZWNJ / `\u200c`) where appropriate.
- Strip leading and trailing whitespace and zero-width spaces (`\u200d`, `\ufeff`).

## 3. Weekly Schedule String Parsing Pattern
In SCU Golestan reports, course weekly schedule cells combine day, time, location, and frequency:
`[day_abbrev]-[HH:MM]-[HH:MM]-[location]-[frequency]`
Multiple sessions are joined by `\n،` or `\n,`.

### Mapping Table:
| Abbrev | Day | English |
| :--- | :--- | :--- |
| `ش` | شنبه | Saturday |
| `ی` | یکشنبه | Sunday |
| `د` | دوشنبه | Monday |
| `س` | سه‌شنبه | Tuesday |
| `چ` | چهارشنبه | Wednesday |
| `پ` | پنجشنبه | Thursday |
| `ج` | جمعه | Friday |

## 4. Handling Merged Rows
Academic portal exports use merged cells for readability:
- A single course often occupies two consecutive rows (e.g. rows 16 & 17).
- Access values using top-left coordinates of the merged range.
- When iterating through rows, step by the merge stride (typically `step=2`).
