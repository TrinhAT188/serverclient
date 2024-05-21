import socket
import pickle
import psutil
import time


def get_running_processes():
    running_processes = []
    for process in psutil.process_iter(['pid', 'name', 'ppid', 'username', 'status']):
        # Bỏ qua các tiến trình hệ thống và các tiến trình không có tên người dùng
        if process.info['username'] is not None and not process.info['username'].endswith('SYSTEM'):
            running_processes.append({
                'pid': process.info['pid'],
                'name': process.info['name'],
                'ppid': process.info['ppid'],  # Thêm PID của tiến trình cha
                'username': process.info['username'],
                'status': process.info['status']
            })
    return running_processes


def send_running_processes(host, port):
    while True:  # Vòng lặp vô hạn để gửi thông tin định kỳ
        processes = get_running_processes()
        data = pickle.dumps(processes)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((host, port))
                s.sendall(data)
                print("Sent running processes to server")
            except Exception as e:
                print(f"Error: {e}")
                break
        time.sleep(8)  # Đợi 7 giây trước khi gửi lại


if __name__ == "__main__":
    SERVER_HOST = '172.16.1.98'
    SERVER_PORT = 12345
    send_running_processes(SERVER_HOST, SERVER_PORT)
