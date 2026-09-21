---
name: telegram-bot-patterns
description: Aiogram 3.x best practices, router patterns, callback query handling, error formatting, and user flow patterns for Telegram bots.
---

# Telegram Bot Patterns (Aiogram 3.x)

This skill provides production-grade architectural patterns for building Telegram bots with `aiogram 3.x`.

## 1. Dispatcher and Router Separation
Never put all handlers in one file. Group handlers by domain into separate `Router()` instances:
- `start.py`: Entry points, deep-linking, referral codes
- `upload.py`: File receipt, validation, background processing dispatch
- `callbacks.py`: Inline button callback handling
- `admin.py`: Privileged commands protected by admin ID checks

## 2. Deep Linking and Referrals
Extract referral tokens from the `/start` payload:
```python
@router.message(CommandStart())
async def cmd_start(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("ref_"):
        referral_code = args[1]
        # record referral
```

## 3. Progress Updates and User Feedback
Always keep the user informed during multi-step background operations:
1. Send initial message: `📥 فایل دریافت شد...`
2. Update existing message: `edit_text("⚙️ در حال پردازش...")`
3. Deliver documents via `BufferedInputFile` with descriptive Persian/ASCII filenames.

## 4. Never Expose Stack Traces
Display clear, polite, actionable error messages to the user. Log the full traceback internally with the corresponding `job_id`.
