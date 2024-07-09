import network
import usocket as socket
import sensor
import image
import time
ssid ='Redmi K60 Pro'
key = '23456789'
wlan = network.WINC()
wlan.connect(ssid, key=key, security=wlan.WPA_PSK)
while not wlan.isconnected():
	pass
print("WiFi连接成功！ IP信息:", wlan.ifconfig())
server_address = ('192.168.202.130', 8081)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)
client_socket.settimeout(10)
sensor.reset()
sensor.set_framesize(sensor.VGA)
sensor.set_pixformat(sensor.RGB565)
img_count = 0
frame_count = 0
clock = time.clock()
try:
	while True:
		clock.tick()
		img = sensor.snapshot()
		img.compress(quality=90)
		img_bytes = img.bytearray()
		img_size_bytes = len(img_bytes).to_bytes(4, 'big')
		client_socket.sendall(img_size_bytes)
		client_socket.sendall(img_bytes)
		img_count += 1
		print("已发送图像数量:", img_count)
		frame_count += 1
		if frame_count >= 20:
			print("Processed 20 frames. FPS: {:.2f}".format(clock.fps()))
			frame_count = 0
finally:
	client_socket.close()
	print("连接已关闭。")