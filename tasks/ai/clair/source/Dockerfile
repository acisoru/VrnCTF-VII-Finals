FROM pytorch/pytorch:2.7.0-cuda12.6-cudnn9-runtime

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir \
    transformers \
    gguf \
    accelerate \
    fastapi[standard] \
    uvicorn[standard]

EXPOSE 5000

CMD ["uvicorn", "backend.backend:app", "--host", "0.0.0.0", "--port", "5000"]
#CMD ["fastapi", "dev", "backend.py"]
#CMD [ "python", "/app/backend/backend.py" ]
#ENTRYPOINT /bin/bash