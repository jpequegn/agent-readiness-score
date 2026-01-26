FROM python:3.11-slim as base

WORKDIR /app

FROM base as development
RUN pip install --no-cache-dir pytest pytest-cov ruff black
COPY . .
RUN pip install -e .

CMD ["python"]
