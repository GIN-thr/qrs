import io
import socket
import cv2
import numpy as np
import torch
import time
import os
import json
import websockets
import asyncio
import mysql.connector
from mysql.connector import Error
import pickle
import base64
from PIL import Image
from models.experimental import attempt_load
from ultralytics.utils.ops import scale_coords
from utils.general import non_max_suppression
from utils.torch_utils import select_device
from utils.plots import plot_one_box
import paho.mqtt.publish as publish

def load_model():
    model_path = r'C:\Users\11566\Desktop\yolov5-7.0\yolov5-7.0\runs\train\exp\weights\best.pt'  # 模型路径
    device = select_device('cuda:0')  # GPU使用'cuda:0'
    # 加载YOLOv5模型
    model = attempt_load(model_path)  # 加载模型
    model.to(device)  # 将模型转移
    names = model.module.names if hasattr(model, 'module') else model.names  # 获取类别名称
    return model, device, names


model, device, names = load_model()

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
def insert_detection_log(connection,no_helmet_count):
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

async def process_images(model, device, names, img, connected_clients):
    save_dir = r'C:\Users\11566\Desktop\test'  # 图像保存路径
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    base_url = 'http://localhost:8081/'  # 服务器URL，确保按需调整
    image_urls = []  # 初始化图像URL列表
    no_helmet_count = 0
    start_time = time.time()
    no_helmet_centers = []
    center_distance_threshold = 50  # 用于判定两个中心点是否足够远，视为不同人

    try:
        print("开始检测图像")
        img_tensor = torch.from_numpy(img).to(device).float() / 255.0  # 将图像转换为模型输入格式
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)  # 调整维度以匹配模型输入
        pred = model(img_tensor, augment=False, visualize=False)[0]  # 进行预测
        pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)  # 应用NMS
        for i, det in enumerate(pred):  # 遍历检测结果
            if len(det):
                det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], img.shape).round()
                detected_this_frame = []
                for *xyxy, conf, cls in det:
                    if names[int(cls)] == 'without helmet':
                        xyxy = [x.cpu().numpy() for x in xyxy]
                        center_x = (xyxy[0] + xyxy[2]) / 2
                        center_y = (xyxy[1] + xyxy[3]) / 2
                        current_center = np.array([center_x, center_y])

                        if all(np.linalg.norm(current_center - np.array(center), ord=2) > center_distance_threshold for
                               center in no_helmet_centers):
                            no_helmet_count += 1
                            no_helmet_centers.append(current_center)
                            detected_this_frame.append(True)  # 标记为这一帧中的新检测
                        else:
                            detected_this_frame.append(False)  # 不是新检测
                    else:
                        detected_this_frame.append(False)  # 不是未戴头盔的人

                    label = f'{names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, img, label=label, color=(255, 0, 0), line_thickness=3)

        # if no_helmet_count > 0:  # 有新的未戴头盔人员检测
        #     timestamp = time.strftime("%Y%m%d-%H%M%S")
        #     img_name = f"no_helmet_{timestamp}.jpg"
        #     img_path = os.path.join(save_dir, img_name)
        #     cv2.imwrite(img_path, img)  # 保存图像
        #     img_url = f"{base_url}{img_name}"
        #     image_urls.append({'url': img_url})

        # elapsed_time = time.time() - start_time
        # print(f"过去 {int(elapsed_time // 60)} 分 {elapsed_time % 60:.1f} 秒内，共有 {no_helmet_count} 人未戴头盔。")
        # 插入数据库
                if any(detected_this_frame):
                    print("触发检测")
                    insert_detection_log(create_db_connection(), no_helmet_count)
                    # 如果需要，将图像信息发送或处理
                    # 此处可以添加将 image_urls 发送到客户端的代码
                    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                    jpeg_img = io.BytesIO()
                    pil_img.save(jpeg_img, format='JPEG')
                    jpeg_img_bytes = jpeg_img.getvalue()
                    base64_img = base64.b64encode(jpeg_img_bytes).decode('utf-8')
                    for connect in connected_clients:
                        if not connect.websocket.closed:
                            await connect.websocket.send("detected" + base64_img)

    except Exception as e:
        print(f"发生错误: {e}")

ws_list = set()


class WebSocketConnection:
    def __init__(self, websocket, path):
        self.websocket = websocket
        self.path = path


async def start_websocket_server():
    async with websockets.serve(handle_websocket, "localhost", 8765):
        print("WebSocket server started and listening on ws://localhost:8765")
        await asyncio.Future()  # 防止函数退出，使其持续运行

mqtt_server = "118.24.230.64"
mqtt_topic = "servo/control"
mqtt_port = 1883

async def handle_websocket(websocket, path):
    connection = WebSocketConnection(websocket, path)
    ws_list.add(connection)
    print(f"New websocket connection established from {path}")
    try:
        async for message in websocket:
            if message.startswith("opt"):
                parts = message.split(":")
                if len(parts) == 2:
                    command, direction = parts[0], parts[1]
                    if command == "opt":
                        response = f"收到操作指令: {direction}"
                        if direction == "right":
                            print("此处执行向右操作")
                            publish.single(mqtt_topic, "opt:right", hostname=mqtt_server, port=mqtt_port)
                        elif direction == "left":
                            print("此处执行向左操作")
                            publish.single(mqtt_topic, "opt:left", hostname=mqtt_server, port=mqtt_port)
                        else:
                            print("无效指令")
                    await websocket.send(response)
    except websockets.exceptions.ConnectionClosedError:
        pass
    finally:
        print(websocket)
        for conn in ws_list:
            if conn.websocket == websocket:
                ws_list.remove(conn)
                break


async def handle_socket_client(reader, writer, connected_clients):
    while True:
        # 从客户端读取数据
        # 从客户端读取图像大小信息
        img_size_bytes = await reader.readexactly(4)
        img_size = int.from_bytes(img_size_bytes, 'big')

        # 从客户端读取完整的图像数据
        img_data = await reader.readexactly(img_size)
        # frame = pickle.loads(img_data)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        await process_images(model, device, names, img, connected_clients)
        # success, encoded_image = cv2.imencode('.jpg', frame)
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB));
        jpeg_img = io.BytesIO()
        pil_img.save(jpeg_img, format='JPEG')
        jpeg_img_bytes = jpeg_img.getvalue()
        base64_img = base64.b64encode(jpeg_img_bytes).decode('utf-8')
        for connect in connected_clients:
            if not connect.websocket.closed:
                await connect.websocket.send("frame" + base64_img)


async def start_socket_server(socket_port, connected_clients):
    async def handle_connection(reader, writer):
        await handle_socket_client(reader, writer, connected_clients)

    server = await asyncio.start_server(handle_connection, '0.0.0.0', socket_port)
    print(f"Socket服务正在运行, 监听端口 {socket_port}")
    async with server:
        await server.serve_forever()


async def main():
    # model, device, names = load_model()
    # server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_socket.bind(('0.0.0.0', 8081))
    # server_socket.listen(1)
    # print('正在监听所有网络接口，端口8081...')

    websocket_port = 8765
    socket_port = 8081
    websocket_server_task = start_websocket_server()
    socket_server_task = asyncio.create_task(start_socket_server(socket_port, ws_list))
    await asyncio.gather(websocket_server_task, socket_server_task)


if __name__ == "__main__":
    asyncio.run(main())