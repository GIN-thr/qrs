import socket
if __name__ == "__main__":
    HOST = '127.0.0.1'
    PORT = 12345

    # 创建一个 TCP/IP 套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定服务器地址和端口
    server_socket.bind((HOST, PORT))

    # 开始监听连接
    server_socket.listen(1)

    print('等待客户端连接...')
    connection, client_address = server_socket.accept()

    print('客户端已连接:', client_address)

    # 接收数据并回传
    while True:
        data = connection.recv(1024)
        if not data:
            break
        message = data.decode()
        print("收到消息" + message)
        if message.startswith("opt"):
            parts = message.split(":")
            if len(parts) == 2:
                command, direction = parts[0], parts[1]
                if command == "opt":
                    response = f"收到操作指令: {direction}"
                    if direction == "right":
                        print("此处执行向右操作")

                    elif direction == "left":
                        print("此处执行向左操作")

                    else:
                        print("无效指令")
        connection.sendall(message.encode())
