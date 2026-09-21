"""Tests for Telegram bot callbacks (on-demand HTML delivery)."""

from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import CallbackQuery, Message

from app.bot.handlers.callbacks import get_html_on_demand_callback


@pytest.mark.asyncio
async def test_get_html_on_demand_success(tmp_path):
    # Prepare a mock HTML file in storage/outputs
    outputs_dir = Path("storage/outputs")
    outputs_dir.mkdir(parents=True, exist_ok=True)
    test_stem = "teststem12345"
    html_file = outputs_dir / f"{test_stem}.html"
    html_file.write_text("<html><body>Test Schedule</body></html>", encoding="utf-8")

    try:
        mock_callback = MagicMock(spec=CallbackQuery)
        mock_callback.data = f"get_html:{test_stem}"
        mock_callback.answer = AsyncMock()
        mock_message = MagicMock(spec=Message)
        mock_message.answer_document = AsyncMock()
        mock_callback.message = mock_message

        await get_html_on_demand_callback(mock_callback)

        assert mock_callback.answer.called
        assert mock_message.answer_document.called
        call_args = mock_message.answer_document.call_args
        buffered_file = call_args[0][0]
        assert buffered_file.filename == "barname_haftegi.html"
    finally:
        html_file.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_get_html_on_demand_expired():
    mock_callback = MagicMock(spec=CallbackQuery)
    mock_callback.data = "get_html:nonexistentstem999"
    mock_callback.answer = AsyncMock()

    await get_html_on_demand_callback(mock_callback)

    assert mock_callback.answer.called
    # Should alert user about expired file
    alert_text = mock_callback.answer.call_args[0][0]
    assert "منقضی" in alert_text
