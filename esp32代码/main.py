import network
import time
from machine import Pin, PWM
from umqtt.simple import MQTTClient

# Wi-Fi设置
WIFI_SSID = 'Redmi K60 Pro'
WIFI_PASSWORD = '23456789'

# 初始化PWM对象，选择ESP32-C3上的一个支持PWM的引脚
servo_pin = Pin(9)  # 使用GPIO9
pwm_servo = PWM(servo_pin, freq=50)  # 设置SG90舵机的PWM频率为50Hz

# 设置舵机旋转
def servo_angle(angle):
    # 设置脉冲宽度
    if angle == 'left':
        duty_cycle = 2000 / 20000  # 逆时针旋转
    elif angle == 'right':
        duty_cycle = 1000 / 20000  # 顺时针旋转
    duty = int(duty_cycle * 65535)
    pwm_servo.duty_u16(duty)
    time.sleep(0.15)  # 旋转0.15秒
    pwm_servo.duty_u16(int((1500 / 20000) * 65535))  # 停止

# 连接到Wi-Fi
def connect_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('正在连接网络...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            pass
    print('网络配置:', wlan.ifconfig())

# MQTT设置
MQTT_BROKER = "118.24.230.64"
MQTT_PORT = 1883
MQTT_TOPIC = "servo/control"

# 创建回调函数来处理收到的消息
def on_message(topic, msg):
    message = msg.decode()

    if message == "opt:right":
        print("接收到向右的指令，向右旋转0.15秒")
        servo_angle('right')
    elif message == "opt:left":
        print("接收到向左的指令，向左旋转0.15秒")
        servo_angle('left')
    else:
        print("错误的指令")

# 订阅MQTT主题
def mqtt_subscribe():
    client = MQTTClient("device", MQTT_BROKER, MQTT_PORT)
    client.set_callback(on_message)
    client.connect()
    client.subscribe(MQTT_TOPIC)
    print("已连接到MQTT代理并订阅了主题: {}".format(MQTT_TOPIC))

    try:
        while True:
            client.wait_msg()
    finally:
        client.disconnect()

# 主程序
def main():
    connect_wifi(WIFI_SSID, WIFI_PASSWORD)
    mqtt_subscribe()

if __name__ == "__main__":
    main()

