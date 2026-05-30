/* ============================================================
   myserver_partB.c
   목적: HTTP 요청 파싱 → 파일 읽기 → HTTP 응답 전송
   컴파일: gcc -o myserver_partB myserver_partB.c
   실행:   ./myserver_partB 7777
   ============================================================ */

#include <stdio.h>       /* printf, fprintf, perror, snprintf */
#include <stdlib.h>      /* exit, atoi */
#include <string.h>      /* memset, strlen, strcmp, strcpy, strrchr */
#include <unistd.h>      /* read, write, close */
#include <sys/socket.h>  /* socket, bind, listen, accept */
#include <netinet/in.h>  /* sockaddr_in, htons, INADDR_ANY */
#include <sys/stat.h>    /* stat 구조체 - 파일 크기 확인에 사용 */
#include <fcntl.h>       /* open(), O_RDONLY - 파일 열기에 사용 */

#define BUFFER_SIZE   4096  /* HTTP 요청 수신 버퍼 크기 */
#define RESPONSE_SIZE 8192  /* HTTP 응답 헤더 버퍼 크기 */

/* ── MIME 타입 반환 함수 ─────────────────────────────────────
   파일명을 받아 Content-Type 문자열 반환
   브라우저가 이 값을 보고 파일을 어떻게 처리할지 결정 */
const char* get_mime_type(const char *filename) {

    /* strrchr() = 문자열에서 특정 문자의 마지막 위치 반환
       '.' 를 찾아 확장자 부분 포인터 얻기
       예: "./pic.jpg" → ".jpg" 위치의 포인터 반환 */
    const char *ext = strrchr(filename, '.');

    /* 확장자가 없으면 기본 바이너리 타입 반환 */
    if (!ext) return "application/octet-stream";

    /* strcmp() = 문자열 비교 (같으면 0 반환)
       각 확장자에 맞는 MIME 타입 반환 */
    if (strcmp(ext, ".html") == 0 || strcmp(ext, ".htm") == 0)
        return "text/html";        /* HTML → 브라우저가 렌더링 */

    if (strcmp(ext, ".txt") == 0)
        return "text/plain";       /* 텍스트 → 그대로 표시 */

    if (strcmp(ext, ".jpg") == 0 || strcmp(ext, ".jpeg") == 0)
        return "image/jpeg";       /* JPEG 이미지 */

    if (strcmp(ext, ".png") == 0)
        return "image/png";        /* PNG 이미지 */

    if (strcmp(ext, ".gif") == 0)
        return "image/gif";        /* GIF 이미지 */

    if (strcmp(ext, ".mp3") == 0)
        return "audio/mpeg";       /* MP3 오디오 */

    /* 알 수 없는 형식 → 브라우저가 다운로드로 처리 */
    return "application/octet-stream";
}

/* ── HTTP 요청 파싱 함수 ─────────────────────────────────────
   request = "GET /pic.jpg HTTP/1.1\r\nHost: ..."
   path에 "/pic.jpg" 추출해서 저장 */
void parse_request(const char *request, char *path) {

    /* sscanf() = 문자열에서 형식에 맞게 값 추출
       "GET %s HTTP" 패턴으로 %s 부분(파일 경로) 추출
       예: "GET /pic.jpg HTTP/1.1" → path = "/pic.jpg" */
    sscanf(request, "GET %s HTTP", path);
}

/* ── 클라이언트 요청 처리 함수 ───────────────────────────────
   read → parse → 파일 읽기 → write 순서로 처리 */
void handle_client(int client_fd) {

    char buffer[BUFFER_SIZE];    /* HTTP 요청 저장 버퍼 */
    char path[256];              /* 요청 파일 경로 저장 */
    char file_path[260];         /* 실제 파일 시스템 경로 */
    char header[RESPONSE_SIZE];  /* HTTP 응답 헤더 저장 */

    /* ── 1. HTTP 요청 수신 (read) ────────────────────────────
       버퍼 초기화 후 소켓에서 데이터 읽기
       브라우저가 보낸 HTTP 요청 메시지 전체 수신 */
    memset(buffer, 0, BUFFER_SIZE);
    read(client_fd, buffer, BUFFER_SIZE - 1);

    /* 받은 요청 출력 (처음 300자만 출력해서 터미널 넘침 방지) */
    printf("\n[받은 요청]\n%.300s\n", buffer);

    /* ── 2. HTTP 요청 파싱 ───────────────────────────────────
       요청 첫 줄 "GET /pic.jpg HTTP/1.1" 에서
       파일 경로 "/pic.jpg" 추출 */
    parse_request(buffer, path);

    /* '/' 요청 시 index.html로 처리 (기본 페이지) */
    if (strcmp(path, "/") == 0)
        strcpy(path, "/index.html");  /* path에 "/index.html" 복사 */

    /* 상대 경로로 변환: "/pic.jpg" → "./pic.jpg"
       snprintf() = 안전한 문자열 형식화 (버퍼 오버플로우 방지)
       현재 디렉토리 기준으로 파일 찾기 위해 '.' 앞에 붙임 */
    snprintf(file_path, sizeof(file_path), ".%s", path);

    printf("[요청 파일] %s\n", file_path);

    /* ── 3. 파일 열기 ────────────────────────────────────────
       open() = 파일 열기 함수 (C 표준 라이브러리)
       O_RDONLY = 읽기 전용으로 열기
       반환값: 파일 디스크립터 (양수) / 실패 시 -1
       → C에서는 fopen 대신 open 사용 (소켓과 동일한 I/O 모델) */
    int file_fd = open(file_path, O_RDONLY);

    if (file_fd >= 0) {
        /* 파일 열기 성공 → 200 OK 응답 */

        /* ── 파일 크기 확인 ──────────────────────────────────
           stat 구조체에 파일 정보 저장
           fstat() = 열린 파일(file_fd)의 정보를 file_stat에 저장
           file_stat.st_size = 파일 크기 (바이트) */
        struct stat file_stat;
        fstat(file_fd, &file_stat);
        long file_size = file_stat.st_size;  /* 파일 크기 저장 */

        /* 파일 확장자로 Content-Type 결정 */
        const char *mime = get_mime_type(file_path);

        /* ── 4. HTTP 응답 헤더 생성 ──────────────────────────
           snprintf로 헤더 문자열 조립
           \r\n = HTTP 헤더 줄 구분자 (반드시 \r\n)
           마지막 빈 줄 \r\n = 헤더와 본문 구분 (필수!)
           %s  = mime 타입 문자열
           %ld = 파일 크기 (long형 정수) */
        snprintf(header, sizeof(header),
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: %s\r\n"
            "Content-Length: %ld\r\n"
            "Connection: close\r\n"
            "\r\n",            /* 헤더/본문 구분 빈 줄 */
            mime, file_size);

        /* ── 5. 헤더 전송 (write) ────────────────────────────
           write() = 소켓에 데이터 쓰기
           client_fd    = 전송할 소켓
           header       = 전송할 데이터
           strlen(header) = 전송할 바이트 수 */
        write(client_fd, header, strlen(header));

        /* ── 6. 파일 데이터 전송 (read → write 반복) ─────────
           파일이 클 수 있으므로 BUFFER_SIZE씩 나눠서 전송
           read()로 파일에서 읽고 write()로 소켓에 씀
           bytes_read = 실제로 읽은 바이트 수
           → 0이 되면 파일 끝 (EOF) → 루프 종료 */
        char file_buf[BUFFER_SIZE];  /* 파일 읽기용 임시 버퍼 */
        int bytes_read;

        /* 파일에서 읽어서 소켓으로 전송 반복 */
        while ((bytes_read = read(file_fd, file_buf, BUFFER_SIZE)) > 0) {
            write(client_fd, file_buf, bytes_read);
        }

        printf("[응답] 200 OK | %s | %ld bytes\n", mime, file_size);

        /* 파일 디스크립터 닫기 (자원 해제) */
        close(file_fd);

    } else {
        /* 파일 열기 실패 → 404 Not Found 응답 */

        /* 404 응답 본문 HTML */
        const char *body = "<html><body><h1>404 Not Found</h1></body></html>";

        /* ── 404 응답 헤더 생성 ──────────────────────────────
           strlen(body) = body 문자열 길이 (Content-Length)
           %zu = size_t 타입 정수 출력 형식 */
        snprintf(header, sizeof(header),
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: %zu\r\n"
            "Connection: close\r\n"
            "\r\n",
            strlen(body));

        /* 헤더 전송 */
        write(client_fd, header, strlen(header));

        /* 본문(404 HTML) 전송 */
        write(client_fd, body, strlen(body));

        printf("[응답] 404 Not Found | %s\n", file_path);
    }
    /* client_fd는 handle_client 호출 후 main에서 close() */
}

int main(int argc, char *argv[]) {

    /* 커맨드라인 인자 확인 */
    if (argc != 2) {
        fprintf(stderr, "사용법: %s <포트번호>\n", argv[0]);
        exit(1);
    }

    /* 포트번호 문자열 → 정수 변환 */
    int port = atoi(argv[1]);

    /* 소켓 파일 디스크립터 변수 */
    int server_fd, client_fd;

    /* 서버·클라이언트 주소 구조체 */
    struct sockaddr_in server_addr, client_addr;

    /* accept()에 전달할 클라이언트 주소 구조체 크기 */
    socklen_t client_len = sizeof(client_addr);

    /* ── 1. TCP 소켓 생성 ────────────────────────────────────
       AF_INET = IPv4, SOCK_STREAM = TCP */
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket");
        exit(1);
    }

    /* 포트 재사용 옵션 (서버 재시작 시 오류 방지) */
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* ── 2. 서버 주소 구조체 초기화 및 설정 ─────────────────
       memset으로 0 초기화 후 필드 설정 */
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;          /* IPv4 */
    server_addr.sin_addr.s_addr = INADDR_ANY;  /* 모든 인터페이스 수신 */
    server_addr.sin_port = htons(port);         /* 포트 바이트 순서 변환 */

    /* ── 3. 바인딩 (bind) ────────────────────────────────────
       소켓을 특정 주소·포트에 연결 */
    if (bind(server_fd,
             (struct sockaddr*)&server_addr,
             sizeof(server_addr)) < 0) {
        perror("bind");
        exit(1);
    }

    /* ── 4. 연결 대기 (listen) ───────────────────────────────
       5 = 동시 대기 가능한 최대 연결 수 */
    if (listen(server_fd, 5) < 0) {
        perror("listen");
        exit(1);
    }

    printf("웹 서버 시작: http://localhost:%d\n", port);
    printf("종료: Ctrl+C\n\n");

    /* ── 5. 무한 루프: 클라이언트 계속 처리 ─────────────────
       서버는 계속 실행되며 클라이언트를 순서대로 처리 */
    while (1) {

        /* ── 6. 연결 수락 (accept) ───────────────────────────
           클라이언트가 연결할 때까지 블로킹
           반환 시 client_fd = 클라이언트 전용 소켓 */
        client_fd = accept(server_fd,
                          (struct sockaddr*)&client_addr,
                          &client_len);
        if (client_fd < 0) {
            perror("accept");
            continue;  /* 오류 시 다음 클라이언트 대기 */
        }

        printf("\n[접속]\n");

        /* ── 7. 요청 처리 ────────────────────────────────────
           read → parse → 파일 읽기 → write 수행 */
        handle_client(client_fd);

        /* ── 8. 클라이언트 소켓 닫기 (close) ────────────────
           handle_client 완료 후 반드시 소켓 닫기
           → 자원 해제, 클라이언트에게 연결 종료 신호 전달 */
        close(client_fd);
    }

    /* 서버 소켓 닫기 (무한루프로 실제 도달 안 함) */
    close(server_fd);
    return 0;
}