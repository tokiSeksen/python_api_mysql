# Dockerfile

FROM python:3.7

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["sh", "-c", "sleep 10 && python ./app/app.py"]
