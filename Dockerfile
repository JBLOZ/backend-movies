FROM python:3.12

WORKDIR /code

RUN apt-get update && apt-get install -y dos2unix netcat-openbsd iputils-ping dnsutils

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./scripts/wait-for-it.sh /code/scripts/wait-for-it.sh
RUN dos2unix /code/scripts/wait-for-it.sh && chmod +x /code/scripts/wait-for-it.sh

COPY ./src /code/src

ENV PYTHONPATH=src

# Use uvicorn directly for better production deployment
CMD ["/code/scripts/wait-for-it.sh", "db:3306", "-t", "60", "--", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]