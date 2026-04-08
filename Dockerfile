FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "src.envs.biotech_env.server.app:app", "--host", "0.0.0.0", "--port", "7860"]