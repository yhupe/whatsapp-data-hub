#!/bin/bash

# Starting telegram bot in background
echo "Starting Telegram Bot in background..."
PYTHONPATH=. python -m telegram_bot.bot &

# Start FastAPI (Main process watched by Fly.io)
echo "Starting FastAPI app in foreground..."
exec uvicorn main:app --host 0.0.0.0 --port 8000