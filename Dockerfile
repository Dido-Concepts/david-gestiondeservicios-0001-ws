
FROM python:3.12-alpine

WORKDIR /app

COPY dist/app-0.1.0-py3-none-any.whl .

RUN pip install --no-cache-dir pip setuptools wheel

RUN pip install --no-cache-dir app-0.1.0-py3-none-any.whl

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
