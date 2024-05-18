import socket
import pickle
import mysql.connector
from datetime import datetime

def receive_running_processes(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            print("Waiting for connection...")
            conn, addr = s.accept()
            connect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            save_connection_info(addr[0], connect_time, None, 'connected')
            with conn:
                print(f"Connected by {addr}")
                try:
                    while True:
                        data = b''
                        while True:
                            recv_data = conn.recv(1024)
                            if not recv_data:
                                break
                            data += recv_data
                        if not data:
                            break
                        processes = pickle.loads(data)
                        save_to_database(processes)
                except (ConnectionResetError, EOFError):
                    pass
                disconnect_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                update_disconnection_info(addr[0], disconnect_time, 'disconnected')

seen_pids = set()
seen_usernames = set()

def save_to_database(processes):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abc@123/',
        database='agent'
    )
    cursor = connection.cursor()

    for process in processes:
        pid = process['pid']
        ppid = process['ppid']
        username = process['username']
        name = process['name']
        status = process['status']
        if not ((pid in seen_pids) and (username in seen_usernames)):
            seen_pids.add(pid)
            seen_usernames.add(username)
            sql = "INSERT INTO running_processes (pid, ppid, name, username, status) VALUES (%s, %s, %s, %s, %s)"
            values = (pid, ppid, name, username, status)
            cursor.execute(sql, values)
            connection.commit()

    connection.close()
    print("Data saved to MySQL database")

def save_connection_info(client_ip, connect_time, disconnect_time, status):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abc@123/',
        database='agent'
    )
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM connections WHERE client_ip = %s AND status = 'connected'", (client_ip,))
    result = cursor.fetchone()

    if result is None:
        sql = "INSERT INTO connections (client_ip, connect_time, disconnect_time, status) VALUES (%s, %s, %s, %s)"
        values = (client_ip, connect_time, disconnect_time, status)
        cursor.execute(sql, values)
        connection.commit()
        print(f"Connection info saved for {client_ip}")

    connection.close()

def update_disconnection_info(client_ip, disconnect_time, status):
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Abc@123/',
        database='agent'
    )
    cursor = connection.cursor()

    sql = "UPDATE connections SET disconnect_time = %s, status = %s WHERE client_ip = %s AND status = 'connected'"
    values = (disconnect_time, status, client_ip)
    cursor.execute(sql, values)
    connection.commit()
    print(f"Disconnection info updated for {client_ip}")

    connection.close()

if __name__ == "__main__":
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 12345
    receive_running_processes(SERVER_HOST, SERVER_PORT)
