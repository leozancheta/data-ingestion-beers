FROM apache/airflow:2.8.1-python3.10
USER root
RUN pip install --upgrade pip && \
    pip install pandas pyspark requests pyarrow fastparquet
USER airflow