FROM python:3.9-slim

WORKDIR /app

RUN pip install flask

COPY peter_greet.jpg .

COPY app.py .

EXPOSE 5000

ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["flask", "run", "--host=0.0.0.0"]