FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
EXPOSE 8501

CMD uvicorn deploy.app:app --host 0.0.0.0 --port 8000 & \
    streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0