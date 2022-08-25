FROM apache/airflow:2.3.3-python3.9

USER root
RUN apt-get update
RUN apt-get install openssh-server -y
RUN apt-get install vim -y
RUN apt-get install net-tools -y

USER airflow
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Seoul
ENV AIRFLOW__CORE__DEFAULT_TIMEZONE=Asia/Seoul

COPY mongo.env /tmp/mongo.env
COPY fred.env /tmp/fred.env

COPY requirements.txt /tmp/requirements.txt

RUN pip install --user --upgrade pip
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt
