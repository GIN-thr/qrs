import socket
import network
import sensor
import time

class Device:
    def __init__(self, ssid, key, server_address):
        self.ssid = ssid
        self.key = key
        self.server_address = server_address
        self.wlan = None
        self.client_socket = None

    def connect_to_wifi(self):
        self.wlan = network.WINC()
        self.wlan.connect(self.ssid, key=self.key, security=self.wlan.WPA_PSK)
        while not self.wlan.isconnected():
            pass  # 等待直到连接成功
        print("WiFi连接成功！ IP信息:", self.wlan.ifconfig())

    def create_tcp_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.client_socket.settimeout(10)  # 设置socket超时时间

    def initialize_sensor(self):
        sensor.reset()
        sensor.set_framesize(sensor.VGA)  # 设置摄像头分辨率为VGA
        sensor.set_pixformat(sensor.RGB565)  # 设置图像格式为RGB565

    def capture_and_send(self):
        img_count = 0
        clock = time.clock()  # 创建一个时钟对象来跟踪FPS
        try:
            while True:
                clock.tick()  # 开始新的帧计时
                img = sensor.snapshot()  # 捕获图像
                img.compress(quality=90)  # 压缩图像
                img_bytes = img.bytearray()

                # 发送图像大小和图像数据
                img_size_bytes = len(img_bytes).to_bytes(4, 'big')
                self.client_socket.sendall(img_size_bytes)
                self.client_socket.sendall(img_bytes)

                # 尝试接收服务器的响应
                try:
                    confirmation = self.client_socket.recv(1024)
                    print("服务器确认:", confirmation.decode())
                except socket.timeout:
                    print("等待服务器确认超时，继续发送下一帧图像。")

                # 打印已发送的图像数量
                img_count += 1
                print("已发送图像数量:", img_count)

        finally:
            self.client_socket.close()  # 退出前确保关闭socket连接
            print("连接已关闭。")

    def run(self):
        self.connect_to_wifi()
        self.create_tcp_client()
        self.initialize_sensor()
        self.capture_and_send()

if __name__ == "__main__":
    device = Device(
        ssid='Redmi K60 Pro',
        key='23456789',
        server_address=('192.168.186.130', 8081)
    )
    device.run()
