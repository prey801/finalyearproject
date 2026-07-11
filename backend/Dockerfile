FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

WORKDIR /app

COPY backend/requirements.txt /app/backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY . /app/

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
