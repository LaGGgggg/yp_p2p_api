#!/bin/bash

PURPLE='\033[0;35m'
NO_COLOR='\033[0m'

cd API

echo "${PURPLE}Apply database migrations${NO_COLOR}"
alembic upgrade head

echo "${PURPLE}Run server${NO_COLOR}"
uvicorn core.main:app --port 8000
