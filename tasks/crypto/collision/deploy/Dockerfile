FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt server.py flag.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y socat && apt-get clean

CMD ["socat", "tcp-l:1111,reuseaddr,fork", "EXEC:'timeout 120 python3 server.py',pty,stderr,echo=0"]