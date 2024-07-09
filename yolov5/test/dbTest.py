import mysql.connector
from mysql.connector import Error

# 数据库配置参数
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wz22'
}
connection = None
# 建立数据库连接
def create_db_connection():
    global connection
    if connection is not None and connection.is_connected():
        return connection
    try:
        connection = mysql.connector.connect(**db_config)
        print("MySQL Database connection successful")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# 插入检测记录到数据库
def insert_detection_log(connection, no_helmet_count):
    try:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO detection_logs (timestamp, no_helmet_count) VALUES (NOW(), %s)",
            (no_helmet_count,)
        )
        connection.commit()
        cursor.close()
        print(f"Inserted detection log into database. Count: {no_helmet_count}")
    except Error as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    connection = create_db_connection()
    insert_detection_log(connection,1)