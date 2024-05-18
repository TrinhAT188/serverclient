import socket
import pickle
import psutil
import platform

def get_client_info():
    # Lấy thông tin về người dùng từ psutil
    users = psutil.users()
    user_info = []
    for user in users:
        username = user.name
        terminal = user.terminal
        host = user.host
        started = user.started
        user_info.append({
            'username': username,
            'terminal': terminal,
            'host': host,
            'started': started
        })
    print(user_info)

    # Lấy thông tin về hệ điều hành của client
    os_info = {
        'os': platform.system(),  # Hệ điều hành của client
        'version': platform.version()  # Phiên bản của hệ điều hành
    }
    print(os_info)
    # Kết hợp thông tin về người dùng và thông tin về hệ điều hành
    client_info = {
        'user_info': user_info,
        'os_info': os_info
    }
    return client_info

def send_client_info(host, port, client_info):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((host, port))
            data = pickle.dumps(client_info)
            s.sendall(data)
            print("Client info sent to server")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    SERVER_HOST = '192.168.1.100'  # Thay bằng địa chỉ IP của server
    SERVER_PORT = 12345
    client_info = get_client_info()
    send_client_info(SERVER_HOST, SERVER_PORT, client_info)
