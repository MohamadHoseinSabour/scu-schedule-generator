# SCU Schedule Generator - Architecture & Project Rules

This document defines the core guidelines, architectural principles, security policies, and implementation standards for the **SCU Schedule Generator** project.

---

## 1. Project Overview

The **SCU Schedule Generator** is a Python-based backend application designed to extract, normalize, and visualize course schedule reports from the Shahid Chamran University of Ahvaz (SCU) academic portal (e.g., Golestan/Sama system exports).

The platform transforms raw, merged-cell Excel files into standardized, beautiful, conflict-checked weekly visual schedules available in multiple formats:
- **Offline-ready HTML schedules** with rich interactive layouts
- **High-resolution image exports (PNG/JPEG)** for sharing on mobile devices
- **Distribution via Telegram Bot (`aiogram 3`) and REST API (`FastAPI`)**

---

## 2. Core Principles & Philosophy

1. **Strict Decoupling**: Parsing logic, domain models, rendering engines, and delivery interfaces (bot/web) are isolated.
2. **Canonical Schedule Model**: All data flows through a single source of truth:
   $$\text{Excel/Portal} \longrightarrow \text{Parser} \longrightarrow \text{Canonical Model} \longrightarrow \text{Renderer}$$
3. **No Hardcoded Course Data**: Never hardcode course names, codes, units, or times from reference files. All schedules must be dynamically parsed and validated.
4. **Resilience & Fault Tolerance**: Academic portal reports frequently change merged cells, formatting, and character encodings. Parsers must be resilient and report clear warnings rather than crash silently.
5. **Offline Independence**: Rendered HTML schedules must function completely offline without relying on external CDNs for CSS, JS, or fonts.

---

## 3. Data Rules

### 3.1 Reference Excel Specification (`Report.xls`)
The reference input file is a legacy BIFF8 format (`.xls`) spreadsheet exported from the university portal with the following structure:
- **Sheet Configuration**: 1 worksheet named `"Page 1"`, dimensions: 51 rows $\times$ 47 columns, containing 132 merged cell ranges.
- **Student Metadata**: Rows 6 to 13 contain student identity, student ID, faculty, major, degree level, and academic standing.
- **Header Row**: Row 15 contains the column definitions:
  - Course Code (`کد درس`): Columns 42–47
  - Course Group (`گروه`): Columns 39–42
  - Course Title (`نام درس`): Columns 30–39
  - Course Units (`واحد`): Columns 28–30
  - Weekly Schedule (`برنامه هفتگی`): Columns 16–28
  - Exam Date & Time (`امتحان`): Columns 10–16
  - Instructor (`مدرس`): Columns 4–10
  - Tuition (`شهریه`): Columns 0–4
- **Course Data Rows**: Rows 16 through 33, where each course spans **2 merged rows** (indices: 16, 18, 20, 22, 24, 26, 28, 30, 32).
- **Summary Row**: Row 35, Column 28 contains total registered units (e.g., `"20.00"`).
- **Reference Volume**: 9 courses, totaling 20 units.

### 3.2 Weekly Schedule String Format
- Each course's weekly schedule field contains one or more sessions separated by newline and comma (`\n،`).
- Format per session: `[day_abbrev]-[HH:MM]-[HH:MM]-[location]-[frequency]`
- **Day Abbreviation Mapping**:
  - `ش` $\rightarrow$ شنبه (Saturday)
  - `ی` $\rightarrow$ یکشنبه (Sunday)
  - `د` $\rightarrow$ دوشنبه (Monday)
  - `س` $\rightarrow$ سه‌شنبه (Tuesday)
  - `چ` $\rightarrow$ چهارشنبه (Wednesday)
  - `پ` $\rightarrow$ پنج‌شنبه (Thursday)
  - `ج` $\rightarrow$ جمعه (Friday)

### 3.3 Text & Digit Normalization
- **Persian/Arabic Digits**: Always normalize Eastern Arabic (`٠-٩`) and Persian (`۰-۹`) digits to standard ASCII digits (`0-9`).
- **Persian Characters**: Normalize Arabic characters (such as `ي` to `ی` and `ك` to `ک`), zero-width non-joiners (ZWNJ), and whitespace.
- **Time Validation**: Ensure valid `HH:MM` 24-hour time ranges where `start_time < end_time`.

---

## 4. Architecture Rules

```
┌─────────────────────────────────────────────────────────┐
│                    Input Sources                        │
│   (Excel Upload via Bot/API or Direct Portal Adapter)   │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                     Parser Layer                        │
│   (BaseScheduleParser ABC -> ExcelScheduleParser)       │
└───────────────────────────┬─────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Canonical Domain Models                    │
│    (ScheduleReport, Course, CourseSession, WeekDay)     │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
┌───────────────────────────┐   ┌───────────────────────────┐
│     Validation Engine     │   │      Render Engines       │
│  (Conflict detection,     │   │  (Jinja2 HTML Template,   │
│   unit sums, anomalies)   │   │   Playwright/Pillow Img)  │
└───────────────────────────┘   └─────────────┬─────────────┘
                                              │
                                              ▼
                                ┌───────────────────────────┐
                                │     Delivery / Bot UI     │
                                │   (Aiogram 3 / FastAPI)   │
                                └───────────────────────────┘
```

1. **Abstract Base Classes**:
   - `BaseScheduleParser`: Defines interface `parse(file_bytes_or_path) -> ScheduleReport`.
   - `BasePortalAdapter`: Defines portal login, session management, and report extraction interface.
2. **Single Responsibility Principle (SRP)**:
   - `app/parsers/`: Solely parses raw documents into domain models.
   - `app/domain/`: Pure data structures and business domain validation rules.
   - `app/render/`: Transforms domain models into HTML, images, or calendar files.
   - `app/services/`: Application use cases coordinating parsers, validation, and storage.
   - `app/bot/`: Telegram bot presentation layer (handlers, keyboards, messages).
   - `app/db/`: Database persistence and repository pattern.
3. **Offline Rendering**:
   - The HTML template must bundle all CSS styles inline or embed local fonts using `@font-face` with base64 data URIs or relative static paths.
   - Never reference `cdn.jsdelivr.net`, `cdnjs.cloudflare.com`, or Google Fonts.

---

## 5. Security Rules

1. **Credential Protection**:
   - **NEVER** log passwords, student credentials, captcha solutions, or session tokens.
   - Portal credentials submitted by users for scraping must only be processed in memory and immediately discarded.
2. **Input Validation & Sanitization**:
   - Validate file headers and MIME types for uploaded files (reject non-Excel uploads).
   - Enforce file size limit (`MAX_FILE_SIZE_MB`, default: 10MB).
   - Sanitize all string inputs displayed in HTML templates to prevent XSS.
3. **Storage & Ephemeral Data Lifecycle**:
   - User uploads and generated schedules must be stored with randomized UUID filenames.
   - Temporary files must be automatically purged after `OUTPUT_TTL_HOURS` (default: 24h) via background maintenance workers.
4. **Rate Limiting & Abuse Prevention**:
   - Enforce rate limits on file processing (`RATE_LIMIT_FILES` per `RATE_LIMIT_WINDOW_MINUTES`).
   - Restrict administrative endpoints and bot commands to `ADMIN_TELEGRAM_IDS`.

---

## 6. Coding & Engineering Rules

1. **Python Standards**: Python 3.12+ exclusively.
2. **Type Hints**: Strict type hints on all function signatures, methods, and return values.
3. **Data Modeling**: Use **Pydantic v2** (`BaseModel`, `Field`, `model_validator`) for domain models and **pydantic-settings** for configuration.
4. **Asynchronous Execution**:
   - All I/O operations (file writing, bot updates, HTTP requests, database queries) must be asynchronous (`async`/`await`) using `aiofiles`, `httpx`, `aiosqlite`/`asyncpg`.
   - Heavy rendering tasks (e.g. headless browser screenshotting) must be delegated to workers or executed in dedicated executors.
5. **Documentation**:
   - Every module, class, and public function must include an English docstring explaining purpose, parameters, and return types.
6. **Testing**:
   - Maintain high unit test coverage with `pytest` and `pytest-asyncio`.
   - Always verify parsers against reference datasets without mocking the raw data away.
