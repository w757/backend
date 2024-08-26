FROM python:3.8-slim

WORKDIR /app
COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV HOST=0.0.0.0
ENV PORT=5000

CMD ["python", "run.py"]
