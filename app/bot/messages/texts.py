"""Bot text constants.

All user-facing messages are defined here as static templates.
No AI-generated text – everything is deterministic.
"""

WELCOME_MESSAGE = (
    "🤖 سلام!\n"
    "برنامه هفتگیت رو از گزارش دانشگاهت برات مرتب میکنم.\n\n"
    "📄 فایل Report رو بفرست\n"
    "تا برات:\n"
    "✅ برنامه هفتگی\n"
    "✅ فایل HTML\n"
    "✅ تصویر قابل ذخیره\n\n"
    "بسازم."
)

PORTAL_DISABLED_MESSAGE = (
    "🌐 این قابلیت هنوز فعال نشده.\n\n"
    "فعلاً فایل Report دانشگاهت رو اینجا ارسال کن."
)

INVALID_FILE_MESSAGE = (
    "❌ این فایل قابل پردازش نیست.\n\n"
    "لطفاً فایل Report اصلی دانشگاه رو با فرمت Excel ارسال کن."
)

FILE_TOO_LARGE_MESSAGE = "❌ حجم فایل بیش از حد مجاز است."

EMPTY_FILE_MESSAGE = "❌ فایل خالی است."

PROCESSING_RECEIVED = "📥 فایل دریافت شد..."
PROCESSING_CHECKING = "🔍 در حال بررسی گزارش..."
PROCESSING_BUILDING = "⚙️ دارم برنامه رو مرتب میکنم..."
PROCESSING_IMAGE = "🖼️ دارم تصویر رو میسازم..."
PROCESSING_DONE = "✅ تموم شد!"

SUCCESS_TEMPLATE = (
    "✅ برنامه هفتگیت آماده شد!\n\n"
    "📚 تعداد درس: {total_courses}\n"
    "🎓 تعداد واحد: {total_units}\n"
    "📅 شنبه تا چهارشنبه\n\n"
    "دو خروجی برات آماده کردم:"
)

CONFLICT_WARNING = "⚠️ در برنامه شما تداخل زمانی وجود دارد."

ERROR_MESSAGE = (
    "❌ یه مشکلی موقع ساخت برنامه پیش اومد.\n\n"
    "فایل رو دوباره ارسال کن.\n"
    "اگر مشکل ادامه داشت، از بخش «گزارش خطا» استفاده کن."
)

RATELIMIT_MESSAGE = "⏳ لطفاً کمی صبر کنید و دوباره تلاش کنید."

SHARE_TEXT = (
    "🤖 با این ربات میتونی Report برنامه دانشگاهت رو "
    "تبدیل کنی به یه برنامه هفتگی مرتب و خوشگل!"
)

FUN_COMPLETION = (
    "📚 واحدهایت را به نظم درآوردم.\n"
    "حالا فقط بخش سخت ماجرا مانده:\n"
    "رفتن سر کلاس 😐"
)

HELP_MESSAGE = (
    "ℹ️ راهنمای استفاده از ربات\n\n"
    "۱. وارد سامانه دانشگاه شو\n"
    "۲. گزارش «تایید انتخاب واحد» رو به صورت Excel دانلود کن\n"
    "۳. فایل رو همینجا برام بفرست\n"
    "۴. برنامه هفتگی HTML و تصویر PNG دریافت کن\n\n"
    "فرمت‌های مجاز: .xls و .xlsx"
)

REBUILD_MESSAGE = "📄 فایل Report جدید رو ارسال کن."
