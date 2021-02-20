FROM tiangolo/uvicorn-gunicorn-fastapi:python3.6

COPY requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt

COPY ./ /app
