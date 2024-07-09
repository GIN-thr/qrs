import socket

if __name__ == "__main__":
    # 定义服务器地址和端口
    SERVER_HOST = '127.0.0.1'
    SERVER_PORT = 12345

    # 创建一个 TCP/IP 套接字
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 连接到服务器
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        while True:
            message = input("Press Enter to send message...")

            # 发送消息给服务器
            # message = "opt:right"
            client_socket.sendall(message.encode())



    finally:
        # 关闭连接
        client_socket.close()

