FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY app ./app
COPY docs/mvp/context ./docs/mvp/context
COPY README.md ./

EXPOSE 8000

CMD ["python", "-m", "app.main", "--host", "0.0.0.0", "--port", "8000"]
