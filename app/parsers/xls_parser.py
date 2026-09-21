import xlrd
from pathlib import Path

def read_xls(file_path: Path) -> xlrd.Book:
    return xlrd.open_workbook(str(file_path), formatting_info=True)
