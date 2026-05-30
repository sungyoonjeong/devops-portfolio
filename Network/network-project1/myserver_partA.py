import socket
import sys

def run_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(1)
    print(f'서버 시작: 포트 {port}에서 대기 중...')

    while True:
        client_socket, client_address = server_socket.accept()
        print(f'\n[연결됨] {client_address}')
        print('=' * 60)
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        print(request)
        print('=' * 60)
        client_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('사용법: python3 myserver_partA.py <포트번호>')
        sys.exit(1)
    port = int(sys.argv[1])
    run_server(port)