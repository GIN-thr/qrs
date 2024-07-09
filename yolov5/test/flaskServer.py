from flask import Flask, Response, jsonify
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

CORS(app)
# 数据库配置参数
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'wz22'
}


# 建立数据库连接
def create_db_connection():
    # global connection
    # if connection is not None and connection.is_connected():
    #     return connection
    try:
        connection = mysql.connector.connect(**db_config)
        print("MySQL Database connection successful")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None


@app.route('/api/statisticData')
def getStatisData():
    query = "SELECT sum(no_helmet_count) FROM detection_logs"
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    cursor.execute(query)
    data = cursor.fetchone()
    cursor.close()
    print(data)
    return jsonify(data)


@app.route('/api/tableData')
def getTableData():
    query = "SELECT MIN(timestamp) AS timestamp, no_helmet_count FROM detection_logs GROUP BY DATE_FORMAT(timestamp, '%Y-%m-%d %H:%i'), no_helmet_count ORDER BY timestamp DESC"
    connection = mysql.connector.connect(**db_config)

    cursor = connection.cursor()
    cursor.execute(query)
    data =  cursor.fetchall()
    cursor.close()
    return jsonify(data)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
