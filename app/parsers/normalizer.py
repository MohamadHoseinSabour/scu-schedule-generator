import re

class Normalizer:
    DAY_ABBREV = {
        'ش': 'شنبه', 'ی': 'یکشنبه', 'د': 'دوشنبه',
        'س': 'سهشنبه', 'چ': 'چهارشنبه', 'پ': 'پنجشنبه', 'ج': 'جمعه'
    }

    @staticmethod
    def normalize_digits(text: str) -> str:
        if not text:
            return text
        persian_digits = '۰۱۲۳۴۵۶۷۸۹'
        arabic_digits = '٠١٢٣٤٥٦٧٨٩'
        english_digits = '0123456789'
        
        translation_table = str.maketrans(persian_digits + arabic_digits, english_digits * 2)
        return text.translate(translation_table)

    @staticmethod
    def normalize_day(text: str) -> str:
        text = Normalizer.clean_text(text)
        if text in Normalizer.DAY_ABBREV:
            return Normalizer.DAY_ABBREV[text]
        return Normalizer.normalize_day_name(text)

    @staticmethod
    def normalize_time(text: str) -> str:
        text = Normalizer.normalize_digits(text)
        text = Normalizer.clean_text(text)
        # Ensure HH:MM format
        parts = text.split(':')
        if len(parts) == 2:
            return f"{int(parts[0]):02d}:{int(parts[1]):02d}"
        return text

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return text
        # Remove ZWNJ and ZWJ
        text = text.replace('\u200c', '').replace('\u200d', '')
        # Normalize whitespace
        text = ' '.join(text.split())
        return text.strip()

    @staticmethod
    def normalize_day_name(text: str) -> str:
        text = Normalizer.clean_text(text)
        text = text.replace(' ', '')
        return text
