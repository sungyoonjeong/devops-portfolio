# 네트워크 Project 1: Web Server
## 이석복 교수 강의 과제 — 완전 정리 및 구현 가이드

---

## 📋 프로젝트 개요

```
목적:
OS가 제공하는 소켓 API를 직접 사용해 웹 브라우저와 데이터를 주고받으며 HTTP 프로토콜의 동작 원리를 이해한다

핵심:
→ 웹 서버(Server)를 직접 구현
→ 클라이언트는 Chrome/Firefox 브라우저 그대로 사용
→ 통신: TCP 소켓
→ 테스트: 한 대의 PC에서 localhost로 접속

구성:
→ Part A: HTTP 요청 메시지를 콘솔에 출력
→ Part B: 요청 파일을 읽어서 HTTP 응답으로 전송
```

---

## 🌐 전체 동작 구조

```
[같은 컴퓨터 안]

┌──────────────────────────────────────────────────────┐
│                                                      │
│  프로세스 1: 웹 브라우저 (Chrome/Firefox)             │
│  → 주소창에 http://localhost:7777/pic.jpg 입력        │
│                                                      │
│              TCP 소켓 통신 (localhost)                │
│       ─────────────────────────────────►             │
│       ◄─────────────────────────────────             │
│                                                      │
│  프로세스 2: 내가 만든 웹 서버 (myserver.py)           │
│  → 포트 7777에서 대기                                 │
│                                                      │
└──────────────────────────────────────────────────────┘

핵심: 웹 브라우저와 서버가 같은 컴퓨터에서 실행되어도
      소켓을 통해 TCP 통신이 이루어짐
```

---

## 🔧 소켓 API 동작 순서

```
서버 소켓 API 순서:

socket()   → 소켓 생성
   │
bind()     → 특정 포트에 소켓 연결 (예: 7777)
   │
listen()   → 클라이언트 연결 대기 상태로 전환
   │
accept()   → 클라이언트 연결 수락 (연결될 때까지 블로킹)
   │
read()     → 클라이언트가 보낸 HTTP 요청 수신
   │
write()    → 클라이언트에게 HTTP 응답 전송
   │
close()    → 소켓 닫기

포트 설정:
→ 실제 웹 서버: 80번 포트 (HTTP)
→ 이 프로젝트: 임의의 포트 (7777, 9999 등)
→ 80번이 아닌 이유: 1023 이하 포트는 루트 권한 필요
```

---

## 📡 HTTP 요청 메시지 구조

```
브라우저가 서버에 보내는 실제 HTTP 요청:

GET /pic.jpg HTTP/1.1
Host: 192.168.1.131:7777
Connection: keep-alive
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36...
Accept-Encoding: gzip, deflate, sdch
Accept-Language: ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4

각 줄 의미:
┌─────────────────────────────────────────────────────────┐
│ GET /pic.jpg HTTP/1.1  │ 요청 라인 (Request Line)        │
│                        │ 메서드 + 경로 + HTTP 버전        │
├─────────────────────────────────────────────────────────┤
│ Host: 192.168.1.131    │ 서버 주소:포트                  │
│ Connection: keep-alive │ 지속 연결 요청                  │
│ Accept: ...            │ 받을 수 있는 파일 형식           │
│ User-Agent: ...        │ 브라우저 종류·버전               │
│ Accept-Encoding: ...   │ 압축 방식 (gzip, deflate)       │
│ Accept-Language: ...   │ 선호 언어                       │
└─────────────────────────────────────────────────────────┘

Part A 목표:
→ 이 메시지 전체를 서버 콘솔에 그대로 출력
→ 브라우저가 자동으로 생성하는 요청 형식을 직접 눈으로 확인
```

---

## ✅ Part A 구현 — HTTP 요청 콘솔 출력

### 목표
```
서버가 포트 7777에서 대기
브라우저가 접속하면 HTTP 요청 메시지를 콘솔에 출력
```
### 코드
## Part A: HTTP 요청 콘솔 출력

```python
# ============================================================
# myserver_partA.py
# 목적: 클라이언트(브라우저)가 보내는 HTTP 요청을 콘솔에 출력
# 실행: python3 myserver_partA.py 7777
# ============================================================

import socket   # 소켓 통신을 위한 파이썬 내장 라이브러리
import sys      # 커맨드라인 인자(포트번호) 받기 위한 라이브러리

def run_server(port):
    # ── 소켓 생성 ──────────────────────────────────────────
    # socket.AF_INET   = IPv4 주소 체계 사용 (인터넷 통신)
    # socket.SOCK_STREAM = TCP 사용 (신뢰성 있는 연결 지향 통신)
    # → 웹 서버는 파일을 손실 없이 전달해야 하므로 TCP 사용
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # ── 소켓 옵션 설정 ─────────────────────────────────────
    # SOL_SOCKET   = 소켓 레벨에서 옵션 설정
    # SO_REUSEADDR = 포트 재사용 허용
    # → 서버 껐다 켤 때 "Address already in use" 오류 방지
    # → 1 = 옵션 활성화
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ── 포트 바인딩 (bind) ─────────────────────────────────
    # '' = 모든 네트워크 인터페이스에서 수신 (0.0.0.0과 동일)
    # port = 클라이언트가 접속할 포트 번호 (예: 7777)
    # → 서버 소켓을 특정 포트에 연결하는 과정
    server_socket.bind(('', port))

    # ── 연결 대기 상태 전환 (listen) ───────────────────────
    # 인자 1 = 동시에 대기할 수 있는 최대 연결 요청 수 (대기 큐 크기)
    # → 이 상태부터 클라이언트가 연결 요청을 보낼 수 있음
    server_socket.listen(1)

    # 서버 시작 안내 메시지 출력
    print(f'서버 시작: 포트 {port}에서 대기 중...')
    print(f'브라우저에서 http://localhost:{port}/파일명 으로 접속하세요\n')

    # ── 무한 루프: 클라이언트 연속 처리 ───────────────────
    # 서버는 꺼지지 않고 계속 클라이언트를 기다려야 하므로 while True
    while True:

        # ── 연결 수락 (accept) ─────────────────────────────
        # 클라이언트가 연결할 때까지 이 줄에서 블로킹(대기)
        # client_socket = 이 클라이언트와 통신하는 전용 소켓
        # client_address = 클라이언트의 (IP주소, 포트번호) 튜플
        client_socket, client_address = server_socket.accept()

        # 연결된 클라이언트 정보 출력
        print(f'[연결됨] 클라이언트: {client_address}')
        print('=' * 60)

        # ── HTTP 요청 수신 (read/recv) ─────────────────────
        # recv(4096) = 소켓에서 최대 4096바이트 읽기
        # → 브라우저가 보낸 HTTP 요청 메시지 전체를 받음
        # decode('utf-8') = 바이트 → 문자열 변환
        # errors='ignore' = 디코딩 오류 무시 (이진 데이터 방지)
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')

        # ── HTTP 요청 콘솔 출력 (Part A 핵심) ──────────────
        # 브라우저가 자동 생성한 GET 요청, Host, User-Agent 등을 눈으로 확인
        print(request)
        print('=' * 60)

        # ── 소켓 닫기 (close) ──────────────────────────────
        # 클라이언트와의 연결 종료
        # → 다음 반복에서 새 클라이언트를 받을 준비
        client_socket.close()

# ── 프로그램 진입점 ────────────────────────────────────────
if __name__ == '__main__':

    # 커맨드라인 인자 개수 확인
    # sys.argv[0] = 파일명 (myserver_partA.py)
    # sys.argv[1] = 첫 번째 인자 (포트번호)
    # → 인자가 2개가 아니면 사용법 출력 후 종료
    if len(sys.argv) != 2:
        print('사용법: python3 myserver_partA.py <포트번호>')
        print('예시:   python3 myserver_partA.py 7777')
        sys.exit(1)  # 비정상 종료 (종료 코드 1)

    # 문자열로 받은 포트번호를 정수로 변환
    port = int(sys.argv[1])

    # 서버 실행
    run_server(port)
```

### 실행 및 테스트

```bash
# 터미널 1: 서버 실행 (image-5 방식)
python3 myserver_partA.py 7777

# 터미널 2 (또는 브라우저): 클라이언트 요청
curl http://localhost:7777/pic.jpg

# 예상 서버 출력:
# [연결됨] 클라이언트: ('127.0.0.1', 54321) /클라이언트가 임의로 할달받아 연결한 포트번호(54321)
# ============================================================
# GET /pic.jpg HTTP/1.1
# Host: localhost:7777
# User-Agent: curl/7.81.0
# Accept: */*
#
# ============================================================
```

---

## ✅ Part B 구현 — 파일 전송 웹 서버

### 목표
```
Part A 기반으로:
1. HTTP 요청 파싱 → 요청 파일 경로 추출
2. 파일 읽기 → 없으면 404 응답
3. HTTP 응답 메시지 형식으로 전송 → 브라우저에 파일 표시

지원 파일 형식:
→ HTML, 텍스트, JPG, PNG, GIF, MP3, PDF 등
→ 단순 텍스트뿐 아니라 이미지·오디오도 전송 가능해야 함
```

### HTTP 응답 메시지 구조

```
서버가 클라이언트에게 보내는 응답:

HTTP/1.1 200 OK\r\n
Content-Type: image/jpeg\r\n
Content-Length: 12345\r\n
\r\n
[파일 바이너리 데이터]

구성:
① 상태 라인:  HTTP/1.1 200 OK
② 헤더:       Content-Type, Content-Length
③ 빈 줄:      \r\n  ← 헤더와 본문을 구분하는 필수 구분자
④ 본문:       실제 파일 데이터 (텍스트 or 바이너리)

주요 상태 코드:
200 OK           → 정상 응답
404 Not Found    → 파일 없음
400 Bad Request  → 잘못된 요청
```

### 코드
## Part B: 파일 전송 웹 서버

```python
# ============================================================
# myserver_partB.py
# 목적: HTTP 요청을 파싱해 실제 파일을 읽고 HTTP 응답으로 전송
# 실행: python3 myserver_partB.py 7777
# ============================================================

import socket   # 소켓 통신 라이브러리
import sys      # 커맨드라인 인자 처리
import os       # 파일 경로·존재 확인, 현재 디렉토리 확인

# ── MIME 타입 매핑 딕셔너리 ────────────────────────────────
# MIME 타입 = 브라우저에게 "이 파일이 어떤 종류인지" 알려주는 정보
# Content-Type 헤더에 포함됨
# → 브라우저가 이 값을 보고 화면에 표시할지, 다운로드할지 결정
# 강의 요구사항: HTML, JPG, MP3 등 다양한 파일 형식 지원
MIME_TYPES = {
    '.html': 'text/html',               # HTML 문서 → 브라우저가 렌더링
    '.htm':  'text/html',               # HTML 구버전 확장자
    '.txt':  'text/plain',              # 일반 텍스트 → 그대로 표시
    '.jpg':  'image/jpeg',              # JPEG 이미지 → 브라우저가 이미지로 표시
    '.jpeg': 'image/jpeg',              # JPEG 대체 확장자
    '.png':  'image/png',               # PNG 이미지
    '.gif':  'image/gif',               # GIF 이미지 (애니메이션 포함)
    '.mp3':  'audio/mpeg',              # MP3 오디오 → 브라우저 내장 플레이어
    '.mp4':  'video/mp4',               # MP4 동영상
    '.pdf':  'application/pdf',         # PDF 문서 → PDF 뷰어
    '.css':  'text/css',                # CSS 스타일시트
    '.js':   'application/javascript',  # 자바스크립트
}

def get_mime_type(filename):
    """
    파일명을 받아 해당 MIME 타입 문자열 반환
    예시: get_mime_type('./pic.jpg') → 'image/jpeg'
    """
    # os.path.splitext = 파일명과 확장자 분리
    # 예: './pic.jpg' → ('./', '.jpg')
    # _는 파일명 부분 (사용 안 함), ext는 확장자 부분
    _, ext = os.path.splitext(filename)

    # 확장자를 소문자로 변환 후 딕셔너리에서 검색
    # .get(key, default) = key 없으면 default 반환
    # 'application/octet-stream' = 알 수 없는 바이너리 파일 (다운로드 처리)
    return MIME_TYPES.get(ext.lower(), 'application/octet-stream')


def parse_http_request(request):
    """
    HTTP 요청 문자열에서 메서드와 파일 경로 추출 (파싱)

    입력: "GET /pic.jpg HTTP/1.1\r\nHost: localhost:7777\r\n..."
    출력: ('GET', '/pic.jpg')
    """
    try:
        # '\r\n'으로 줄 분리 후 첫 번째 줄만 사용
        # 첫 번째 줄 = "GET /pic.jpg HTTP/1.1" (요청 라인)
        first_line = request.split('\r\n')[0]

        # 공백으로 분리: ['GET', '/pic.jpg', 'HTTP/1.1']
        parts = first_line.split(' ')

        # 최소 2개 이상이어야 유효한 요청
        if len(parts) >= 2:
            method = parts[0]   # 'GET' (HTTP 메서드)
            path = parts[1]     # '/pic.jpg' (요청 파일 경로)
            return method, path

    except:
        # 파싱 실패 시 None 반환
        pass

    return None, None


def send_response(client_socket, status_code, status_msg,
                  content_type, body_bytes):
    """
    HTTP 응답 메시지를 조립해서 클라이언트 소켓에 전송 (write)

    HTTP 응답 구조:
    HTTP/1.1 200 OK\r\n          ← 상태 라인
    Content-Type: image/jpeg\r\n ← 헤더
    Content-Length: 12345\r\n    ← 헤더
    \r\n                         ← 헤더/본문 구분 빈 줄 (필수!)
    [파일 바이너리 데이터]        ← 본문
    """

    # ── 응답 헤더 조립 ──────────────────────────────────────
    # f-string으로 상태코드·메시지 삽입
    # \r\n = HTTP 헤더 줄 구분자 (반드시 \r\n 사용, \n만 쓰면 안 됨)
    header = f'HTTP/1.1 {status_code} {status_msg}\r\n'

    # Content-Type = 브라우저에게 파일 종류 알림
    header += f'Content-Type: {content_type}\r\n'

    # Content-Length = 본문 데이터의 바이트 수
    # → 브라우저가 데이터를 얼마나 읽어야 하는지 알기 위해 필요
    header += f'Content-Length: {len(body_bytes)}\r\n'

    # Connection: close = 응답 후 TCP 연결 종료
    header += 'Connection: close\r\n'

    # 헤더와 본문을 구분하는 빈 줄 (반드시 있어야 함)
    # 이 \r\n이 없으면 브라우저가 헤더와 본문을 구분 못 함
    header += '\r\n'

    # ── 헤더 전송 (write) ───────────────────────────────────
    # 헤더는 문자열이므로 UTF-8로 인코딩 후 전송
    client_socket.send(header.encode('utf-8'))

    # ── 본문(파일 데이터) 전송 (write) ─────────────────────
    # body_bytes = 이미 바이트 형태 (rb 모드로 읽었으므로)
    # 이미지·MP3 등 바이너리 파일도 그대로 전송 가능
    client_socket.send(body_bytes)


def handle_client(client_socket):
    """
    연결된 클라이언트 1명의 요청을 처리하는 함수
    read() → parse → 파일 읽기 → write() 순서로 처리
    """
    try:
        # ── HTTP 요청 수신 (read) ───────────────────────────
        # 소켓에서 최대 4096바이트 읽기
        # → 일반적인 HTTP 요청 헤더는 4096바이트 이내
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')

        # 빈 요청이면 처리하지 않고 종료
        if not request:
            return

        # 받은 요청 출력 (디버깅용, 처음 500자만)
        print('\n[받은 HTTP 요청]')
        print(request[:500])

        # ── 요청 파싱 (parsing) ─────────────────────────────
        # HTTP 요청 첫 줄에서 메서드와 경로 추출
        # method = 'GET', path = '/pic.jpg'
        method, path = parse_http_request(request)

        # 파싱 실패 시 종료
        if not method:
            return

        # ── 파일 경로 결정 ──────────────────────────────────
        # '/' 요청 시 index.html 반환 (기본 페이지)
        if path == '/':
            path = '/index.html'

        # path 앞에 '.' 붙여서 현재 디렉토리 기준 상대 경로로 변환
        # 예: '/pic.jpg' → './pic.jpg'
        file_path = '.' + path

        # os.path.normpath = 경로 정규화
        # '../' 같은 상위 디렉토리 접근 공격 방지
        # 예: './../../etc/passwd' → 'etc/passwd' (현재 디렉토리 밖 못 나감)
        file_path = os.path.normpath(file_path)

        print(f'[요청 파일] {file_path}')

        # ── 파일 존재 확인 후 응답 ──────────────────────────
        if os.path.exists(file_path) and os.path.isfile(file_path):
            # ── 파일 읽기 ────────────────────────────────────
            # 'rb' = 바이너리 읽기 모드
            # → 텍스트뿐 아니라 이미지·MP3 등 모든 파일 형식 읽기 가능
            # → 텍스트 모드('r')로 읽으면 이미지 파일이 깨짐
            with open(file_path, 'rb') as f:
                file_data = f.read()  # 파일 전체를 바이트로 읽기

            # 파일 확장자로 MIME 타입 결정
            content_type = get_mime_type(file_path)

            # ── 200 OK 응답 전송 (write) ─────────────────────
            send_response(
                client_socket,
                200,            # 상태 코드: 정상
                'OK',           # 상태 메시지
                content_type,   # Content-Type 헤더값
                file_data       # 실제 파일 데이터 (바이트)
            )

            print(f'[응답] 200 OK | {content_type} | {len(file_data)} bytes')

        else:
            # ── 404 Not Found 응답 ───────────────────────────
            # 파일이 없을 때 404 HTML 응답 생성
            body = '<html><body><h1>404 Not Found</h1></body></html>'

            # 문자열 → 바이트 변환 후 전송
            send_response(
                client_socket,
                404,                    # 상태 코드: 파일 없음
                'Not Found',            # 상태 메시지
                'text/html',            # HTML 형태로 응답
                body.encode('utf-8')    # 문자열을 바이트로 변환
            )

            print(f'[응답] 404 Not Found | {file_path}')

    except Exception as e:
        # 예외 발생 시 오류 출력 (서버는 계속 실행)
        print(f'[오류] {e}')

    finally:
        # ── 소켓 닫기 (close) ─────────────────────────────
        # try 성공·실패 관계없이 반드시 실행
        # → 소켓 자원을 반드시 해제해야 함
        # → 닫지 않으면 파일 디스크립터가 쌓여서 서버가 죽을 수 있음
        client_socket.close()


def run_server(port):
    """
    서버 메인 함수
    socket() → bind() → listen() → accept() 반복 수행
    """

    # ── TCP 소켓 생성 ────────────────────────────────────────
    # AF_INET = IPv4, SOCK_STREAM = TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 포트 재사용 옵션 (서버 재시작 시 오류 방지)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # ── 포트 바인딩 ──────────────────────────────────────────
    # 모든 인터페이스에서 지정된 포트로 수신
    server_socket.bind(('', port))

    # ── 연결 대기 ────────────────────────────────────────────
    # 5 = 최대 5개의 연결 요청을 대기 큐에 저장
    # → 동시에 여러 브라우저 탭에서 접속해도 처리 가능
    server_socket.listen(5)

    # 서버 시작 정보 출력
    print(f'웹 서버 시작: http://localhost:{port}')

    # os.getcwd() = 현재 작업 디렉토리 경로
    # → 이 디렉토리에 있는 파일을 서버가 제공함
    print(f'현재 디렉토리: {os.getcwd()}')
    print('종료: Ctrl+C\n')

    try:
        # ── 무한 루프: 클라이언트 계속 처리 ─────────────────
        while True:

            # ── 연결 수락 (accept) ───────────────────────────
            # 클라이언트가 연결할 때까지 블로킹 (대기)
            # → 연결되면 client_socket 반환 (클라이언트 전용 소켓)
            client_socket, addr = server_socket.accept()

            # 접속한 클라이언트 IP:포트 출력
            print(f'\n[접속] {addr}')

            # ── 요청 처리 ────────────────────────────────────
            # handle_client 함수로 위임
            # → read → parse → 파일 읽기 → write → close
            handle_client(client_socket)

    except KeyboardInterrupt:
        # Ctrl+C로 서버 종료 시 정상 종료 메시지
        print('\n서버 종료')

    finally:
        # 서버 소켓도 반드시 닫기
        server_socket.close()


# ── 프로그램 진입점 ──────────────────────────────────────────
if __name__ == '__main__':

    # 포트번호 인자 확인
    if len(sys.argv) != 2:
        print('사용법: python3 myserver_partB.py <포트번호>')
        print('예시:   python3 myserver_partB.py 7777')
        sys.exit(1)

    # 문자열 → 정수 변환
    port = int(sys.argv[1])

    # 서버 실행
    run_server(port)
```

---

## 🧪 테스트 방법

### C언어 파일
## 컴파일 및 실행

```bash
# Part A 컴파일
gcc -o myserver_partA myserver_partA.c

# Part A 실행
./myserver_partA 7777

# Part B 컴파일
gcc -o myserver_partB myserver_partB.c

# Part B 실행
./myserver_partB 7777
```

### 파이썬 파일
### 준비

```bash
# 프로젝트 폴더 생성
cd ~/devops-portfolio
mkdir -p network-project1
cd network-project1

# 테스트용 파일 생성
cat > index.html << 'HTML'
<html>
<body>
  <h1>My Web Server</h1>
  <img src="pic.jpg" alt="테스트 이미지">
  <p>직접 구현한 웹 서버입니다.</p>
</body>
</html>
HTML

echo "Hello, World! 텍스트 파일입니다." > test.txt

# 테스트용 이미지 다운로드
wget -O pic.jpg "https://picsum.photos/200/200"
```

### 서버 실행 및 테스트

```bash
# 터미널 1: 서버 실행
python3 myserver_partB.py 7777

# 터미널 2: curl로 테스트
# HTML 파일
curl http://localhost:7777/

# 텍스트 파일
curl http://localhost:7777/test.txt

# 이미지 파일 (바이너리)
curl -o received.jpg http://localhost:7777/pic.jpg

# 없는 파일 (404 테스트)
curl -v http://localhost:7777/nofile.html

# 헤더 포함 상세 보기
curl -v http://localhost:7777/index.html
```

### 브라우저 테스트

```
Chrome/Firefox 주소창:
http://localhost:7777/
http://localhost:7777/index.html
http://localhost:7777/pic.jpg
http://localhost:7777/test.txt

index.html 안에 <img src="pic.jpg"> 가 있으면:
→ 브라우저가 HTML 받은 후 pic.jpg 추가 요청 자동 발생
→ 서버 콘솔에 2번의 요청이 연속으로 출력됨
→ 이것이 "연속적 요청 처리" (강의 요구사항)
```
---

## Python vs C 핵심 비교

```
Python                          C
─────────────────────────────────────────────────────
socket.socket()              →  socket()
.setsockopt()                →  setsockopt()
.bind()                      →  bind()
.listen()                    →  listen()
.accept()                    →  accept()
.recv()                      →  read()
.send()                      →  write()
.close()                     →  close()
open(f,'rb').read()          →  open() + read() 반복
os.path.exists()             →  open() 실패 여부로 판단
f-string                     →  snprintf()
```

---
---

## 🔄 연속 요청 처리 동작

```
강의 내용:
"index.html 안에 이미지가 있으면
 브라우저는 추가 요청을 서버에 자동으로 보낸다"

실제 동작:

브라우저 요청 1:
GET /index.html HTTP/1.1  →  서버가 index.html 전송
                              브라우저가 HTML 파싱
                              → <img src="pic.jpg"> 발견!

브라우저 요청 2 (자동):
GET /pic.jpg HTTP/1.1     →  서버가 pic.jpg 전송
                              브라우저에 이미지 표시

서버 콘솔 출력:
[접속] ('127.0.0.1', 54321)
[요청 파일] ./index.html
[응답] 200 OK | text/html | 150 bytes

[접속] ('127.0.0.1', 54322)
[요청 파일] ./pic.jpg
[응답] 200 OK | image/jpeg | 24576 bytes
```

---

## 📊 HTTP 전체 통신 흐름

```
브라우저                              myserver.py
   │                                       │
   │  [1] TCP 연결 (3-Way Handshake)       │
   │  SYN ────────────────────────────────►│ listen()
   │  ◄──────────────────────────── SYN+ACK│
   │  ACK ────────────────────────────────►│ accept() 반환
   │                                       │
   │  [2] HTTP 요청 전송                   │
   │  GET /pic.jpg HTTP/1.1 ──────────────►│ read()
   │  Host: localhost:7777                 │ → 파싱
   │  ...헤더...                           │ → 파일 읽기
   │                                       │
   │  [3] HTTP 응답 수신                   │
   │  ◄──────────────── HTTP/1.1 200 OK    │ write()
   │  ◄──────────────── Content-Type: ...  │
   │  ◄──────────────── [이미지 데이터]    │
   │                                       │
   │  [4] TCP 연결 종료                    │
   │  FIN ────────────────────────────────►│ close()
   │  ◄──────────────────────────── FIN+ACK│
   │                                       │
브라우저에 이미지 표시
```

---

## 🔑 핵심 개념 정리

```
TCP vs UDP 선택 (강의 내용):
→ 웹 서버 프로젝트 = TCP 사용
→ 이유: 신뢰성 보장 필요
   → 파일(이미지·HTML)이 손실 없이 전달되어야 함
→ UDP는 스트리밍·DNS 등 손실 허용 가능한 경우에 사용

소켓의 역할 (강의 내용):
→ 소켓 = 프로세스가 네트워크와 통신하는 "문(door)"
→ 응용 계층(HTTP)이 전송 계층(TCP)에 접근하는 인터페이스
→ 개발자는 소켓 API만 사용하면 됨 (TCP 내부 구현 몰라도 됨)

포트 번호:
→ 0~1023: Well-known (80=HTTP, 443=HTTPS, 22=SSH)
→ 1024~: 일반 사용자 사용 가능
→ 이 프로젝트: 7777 or 9999 등 임의 포트 사용

Content-Type의 중요성:
→ 브라우저가 응답 데이터를 어떻게 처리할지 결정
→ image/jpeg → 이미지로 표시
→ text/html  → HTML 렌더링
→ 없으면 브라우저가 다운로드로 처리
```

---