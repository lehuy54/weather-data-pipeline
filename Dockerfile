FROM apache/airflow:3.0.6

USER root
RUN apt-get update && \
    apt-get install -y openjdk-17-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# Set JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
USER 50000

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt