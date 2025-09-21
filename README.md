# OpenWeatherAPI Data Pipeline | Data Engineering Project

Tập trung vào việc học cách kết nối một số các công nghệ DE phổ biến để làm việc với nhau trong Docker, không transform dữ liệu quá phức tạp hay đi sâu vào tối ưu, setup phức tạp như production.

---

## 📑 Mục lục
- [🎯 Giới thiệu](#-giới-thiệu)
- [🧩 Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)
- [📈 Luồng dữ liệu](#-luồng-dữ-liệu)
- [⚙️ Hướng dẫn cài đặt & chạy](#️-hướng-dẫn-cài-đặt--chạy)
- [🔗 Giao diện quản trị](#-url-truy-cập)

---

## 🎯 Giới thiệu

Project này đóng vai trò như một project toàn diện để xây dựng một pipeline dữ liệu end-to-end.  
Bao gồm toàn bộ các bước từ **thu thập dữ liệu thời tiết thực tế được fetching từ OpenWeather API bởi Kafka**, đến **xử lý dữ liệu với Spark**, và cuối cùng là **lưu trữ kết quả vào PostgreSQL**. Tất cả luồng dữ liệu đó đều được **trigger theo lịch trình tự động bởi Airflow** → đây là một bài toán **batch processing** điển hình, nơi dữ liệu được xử lý theo từng lô định kỳ thay vì realtime.

Pipeline sử dụng một bộ công nghệ hiện đại bao gồm **Apache Airflow, Python, Apache Kafka, Apache Spark và PostgreSQL**.  
Toàn bộ hệ thống được **container hóa bằng Docker** để giúp việc triển khai trở nên dễ dàng, đồng nhất và có thể mở rộng.

---

## 🧩 Kiến trúc hệ thống
![System Architecture](Kiến trúc hệ thống.png)
Data source: Sử dụng API từ OpenWeatherAPI để lấy dữ liệu về thời tiết ở thời điểm hiện tại, dữ liệu lấy từ 3 thành phố: Hải Phòng, Hà Nội và Thành phố Hồ Chí Minh
Apache Airflow: Đảm nhiệm quá trình điều phối toàn bộ pipeline (bao gồm trigger Kafka fetch API, submit Spark job và đẩy dữ liệu vào Postgres)
Apache Kafka: message broker để truyền dữ liệu, sử dụng KRaft mode - lưu trữ và phân phối message, tự quản lí metadata của chính nó, loại bỏ sự phụ thuộc vào Zookeeper
Apache Spark: Spark Cluster chịu trách nhiệm xử lý dữ liệu, trong đó Master node điều phối công việc còn Worker node thực hiện xử lý và ghi kết quả vào PostgreSQL
PostgreSQL: Quản lí metdata của Airflow và nơi lưu trữ dữ liệu đã được xử lí từ Spark


---


## 📈 Luồng dữ liệu
1. **Airflow** trigger DAG định kỳ → gọi Python script.  
2. Script gọi **OpenWeather API** → lấy dữ liệu 3 thành phố → gửi vào **Kafka topic `weather-data`**.  
3. **Spark job** (submit sử dụng `SparkSubmitOperator`) đọc từ Kafka → xử lý dữ liệu:  
   - Chuẩn hóa schema  
   - Phân loại mức nhiệt độ (lạnh / mát / nóng)  
4. Spark ghi dữ liệu vào bảng PostgreSQL `weather_processed`.  
5. Có thể xem dữ liệu qua **pgAdmin UI** hoặc chạy **SQL query**.  


---

## ⚙️ Hướng dẫn cài đặt & chạy

1. Clone repository:
    ```bash
    git clone 
    ```
2. Vào https://openweathermap.org/api lấy API KEY, sau đó tạo file .env và gán:
    ```bash
    OPENWEATHER_API_KEY=
    ```
3. Gán thêm biến sau vào .env
    ```bash
    AIRFLOW_UID=50000
    ```
4. Mặc định image của apache/airflow:3.0.6 không bao gồm Java Runtime. Mà ta lại dùng SparkSubmitOperator ở deploy mode là client để submit job cho Spark Cluster (ở đây là từ image apache:spark), nên yêu cầu Java có sẵn trong môi trường, đồng thời cài một số Python package cần thiết. Chính vì thế ta cần phải build lại custom Airflow image:
    ```bash
    docker compose build
    ```
5. Khởi động database:
    ```bash
    docker compose up airflow-init
    ```
6. Khởi động tất cả các service:
    ```bash
    docker compose up -d
    ```
7. Vào Airflow Web Server http://localhost:8082/, đăng nhập với login/password là airflow/airflow, sau đó chọn Admin -> Connections -> Add Connection, sau đó config như sau:
    ```bash
    Connection ID: spark_default
    Connection Type: Spark
    Host: spark-master
    Port: 7077
    ```
8. Thực hiện chạy DAG ngay trên Airflow Web Server

---

## 🔗 Giao diện quản trị

- Airflow: localhost:8082
login: airflow
pass: airflow

- pgAdmin (UI cho postgres): 
login: admin@admin.com
pass: admin
----------------------
Register servers:
hostname: postgres
username: postgres
password: postgres

- Kafka-UI (UI quản lí và theo dõi các brokers, topics, consumers): localhost:8080

- Spark Master (UI quản lí và theo dõi trạng thái của workers): localhost:8081