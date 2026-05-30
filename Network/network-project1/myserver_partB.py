import socket
import sys
import os

MIME_TYPES = {
    '.html': 'text/html',
    '.htm':  'text/html',
    '.txt':  'text/plain',
    '.jpg':  'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png':  'image/png',
    '.gif':  'image/gif',
    '.mp3':  'audio/mpeg',
    '.mp4':  'video/mp4',
    '.pdf':  'application/pdf',
    '.css':  'text/css',
    '.js':   'application/javascript',
}

def get_mime_type(filename):
    _, ext = os.path.splitext(filename)
    return MIME_TYPES.get(ext.lower(), 'application/octet-stream')

def parse_http_request(request):
    try:
        first_line = request.split('\r\n')[0]
        parts = first_line.split(' ')
        if len(parts) >= 2:
            return parts[0], parts[1]
    except:
        pass
    return None, None

def send_response(client_socket, status_code, status_msg, content_type, body_bytes):
    header = f'HTTP/1.1 {status_code} {status_msg}\r\n'
    header += f'Content-Type: {content_type}\r\n'
    header += f'Content-Length: {len(body_bytes)}\r\n'
    header += 'Connection: close\r\n'
    header += '\r\n'
    client_socket.send(header.encode('utf-8'))
    client_socket.send(body_bytes)

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        if not request:
            return
        print('\n[받은 HTTP 요청]')
        print(request[:300])

        method, path = parse_http_request(request)
        if not method:
            return

        if path == '/':
            path = '/index.html'

        file_path = '.' + path
        file_path = os.path.normpath(file_path)
        print(f'[요청 파일] {file_path}')

        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                file_data = f.read()
            content_type = get_mime_type(file_path)
            send_response(client_socket, 200, 'OK', content_type, file_data)
            print(f'[응답] 200 OK | {content_type} | {len(file_data)} bytes')
        else:
            body = '<html><body><h1>404 Not Found</h1></body></html>'
            send_response(client_socket, 404, 'Not Found', 'text/html', body.encode('utf-8'))
            print(f'[응답] 404 Not Found | {file_path}')

    except Exception as e:
        print(f'[오류] {e}')
    finally:
        client_socket.close()

def run_server(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('', port))
    server_socket.listen(5)
    print(f'웹 서버 시작: http://localhost:{port}')
    print(f'현재 디렉토리: {os.getcwd()}')
    print('종료: Ctrl+C\n')
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f'\n[접속] {addr}')
            handle_client(client_socket)
    except KeyboardInterrupt:
        print('\n서버 종료')
    finally:
        server_socket.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('사용법: python3 myserver_partB.py <포트번호>')
        sys.exit(1)
    port = int(sys.argv[1])
    run_server(port)