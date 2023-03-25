FROM python:3.8-slim-buster


# Install Java
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         openjdk-11-jre-headless \
  && apt-get install -y procps \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV SPARK_HOME=/opt/spark

ENV SPARK_MASTER default
ENV SPARK_WORKER_CORES=1
ENV SPARK_WORKER_MEMORY=1g
ENV SPARK_DRIVER_MEMORY=1g
ENV SPARK_EXECUTOR_MEMORY=1g

RUN  apt-get update \
  && apt-get install -y wget \
  && rm -rf /var/lib/apt/lists/*

RUN wget -O apache-spark.tgz "https://dlcdn.apache.org/spark/spark-3.2.3/spark-3.2.3-bin-hadoop2.7.tgz" \
    && mkdir -p /opt/spark \
    && tar -xvf apache-spark.tgz -C /opt/spark --strip-components=1 \
    && rm apache-spark.tgz


CMD ["/bin/sh", "-c", "$SPARK_HOME/bin/spark-class org.apache.spark.deploy.worker.Worker $SPARK_MASTER"]