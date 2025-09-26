# OpenWeatherAPI Data Pipeline | Data Engineering Project

Tập trung vào việc học cách kết nối một số công nghệ DE phổ biến để làm việc với nhau trong Docker.  
Project **không** tập trung vào transform phức tạp hay tối ưu nâng cao như môi trường production.

---

## 📑 Mục lục
- [🎯 Giới thiệu](#-giới-thiệu)  
- [🧩 Kiến trúc hệ thống](#-kiến-trúc-hệ-thống)  
- [📈 Luồng dữ liệu](#-luồng-dữ-liệu)  
- [⚙️ Hướng dẫn cài đặt & chạy](#️-hướng-dẫn-cài-đặt--chạy)  
- [🔗 Giao diện quản trị](#-giao-diện-quản-trị)  

---

## 🎯 Giới thiệu

Bao gồm toàn bộ các bước từ **thu thập dữ liệu thời tiết thực tế được fetching từ OpenWeather API bởi Kafka**, đến **xử lý dữ liệu với Spark**, và cuối cùng là **lưu trữ kết quả vào PostgreSQL**.  

Tất cả luồng dữ liệu được **trigger theo lịch trình tự động bởi Airflow** → đây là một bài toán **batch processing** điển hình, nơi dữ liệu được xử lý theo từng lô định kỳ thay vì realtime.

Pipeline sử dụng một bộ công nghệ hiện đại bao gồm **Apache Airflow, Python, Apache Kafka, Apache Spark và PostgreSQL**.  
Toàn bộ hệ thống được **container hóa bằng Docker** để giúp việc triển khai trở nên dễ dàng, đồng nhất và có thể mở rộng.

---

## 🧩 Kiến trúc hệ thống

![Kiến trúc hệ thống](https://github.com/lehuy54/weather-data-pipeline/blob/main/Ki%E1%BA%BFn%20tr%C3%BAc%20h%E1%BB%87%20th%E1%BB%91ng.png)

- **Data source**: OpenWeatherAPI, lấy dữ liệu thời tiết từ 3 thành phố: Hải Phòng, Hà Nội, TP.HCM.  
- **Apache Airflow**: Orchestrator, điều phối pipeline (trigger Kafka fetch API, submit Spark job, ghi vào Postgres).  
- **Apache Kafka**: Message broker truyền dữ liệu. Sử dụng **KRaft mode** để tự quản lý metadata, loại bỏ phụ thuộc vào Zookeeper.  
- **Apache Spark**: Spark Cluster xử lý dữ liệu → Master node điều phối công việc, Worker node xử lý và ghi vào PostgreSQL.  
- **PostgreSQL**: Vừa quản lý metadata của Airflow, vừa lưu dữ liệu đã xử lý từ Spark.  

---

## 📈 Luồng dữ liệu

1. **Airflow** trigger DAG định kỳ → gọi Python script.  
2. Script gọi **OpenWeather API** → lấy dữ liệu 3 thành phố → gửi vào **Kafka topic `weather-data`**.  
3. **Spark job** (submit qua `SparkSubmitOperator`) đọc từ Kafka → xử lý dữ liệu:  
   - Chuẩn hóa schema  
   - Phân loại mức nhiệt độ (lạnh / mát / nóng)  
4. Spark ghi dữ liệu vào PostgreSQL bảng `weather_processed`.  
5. Có thể xem dữ liệu qua **pgAdmin UI** hoặc query trực tiếp.  

---

## ⚙️ Hướng dẫn cài đặt & chạy

1. Clone repository:
    ```bash
    git clone https://github.com/lehuy54/weather-data-pipeline.git
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

| Service          | URL                          | User / Login       | Password   | Ghi chú                            |
|------------------|------------------------------|--------------------|------------|------------------------------------|
| **Airflow**      | [localhost:8082](http://localhost:8082) | `airflow`         | `airflow` | Orchestrator, trigger DAGs         |
| **pgAdmin**      | [localhost:5050](http://localhost:5050) | `admin@admin.com` | `admin`   | UI cho PostgreSQL                  |
| **Kafka UI**     | [localhost:8080](http://localhost:8080) | -                  | -          | Quản lý brokers, topics, consumers |
| **Spark Master** | [localhost:8081](http://localhost:8081) | -                  | -          | Theo dõi trạng thái cluster        |

🔹 **Thông tin đăng nhập PostgreSQL để thêm server trong pgAdmin**:  
- hostname: `postgres`  
- username: `postgres`  
- password: `postgres`  


