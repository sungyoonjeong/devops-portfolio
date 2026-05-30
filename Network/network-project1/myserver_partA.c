/* ============================================================
   myserver_partA.c
   목적: 클라이언트(브라우저)가 보내는 HTTP 요청을 콘솔에 출력
   컴파일: gcc -o myserver_partA myserver_partA.c
   실행:   ./myserver_partA 7777
   ============================================================ */

#include <stdio.h>       /* printf, fprintf, perror 함수 사용 */
#include <stdlib.h>      /* exit(), atoi() 함수 사용 */
#include <string.h>      /* memset(), strlen() 함수 사용 */
#include <unistd.h>      /* read(), write(), close() 함수 사용 (Unix I/O) */
#include <sys/socket.h>  /* socket(), bind(), listen(), accept() 함수 사용 */
#include <netinet/in.h>  /* sockaddr_in 구조체, htons(), INADDR_ANY 사용 */

#define BUFFER_SIZE 4096  /* HTTP 요청을 받을 버퍼 크기 (4KB) */

int main(int argc, char *argv[]) {

    /* ── 커맨드라인 인자 확인 ─────────────────────────────────
       argc = 인자 개수 (프로그램명 포함)
       argv[0] = "./myserver_partA" (프로그램명)
       argv[1] = "7777" (포트번호)
       → 인자가 정확히 2개(프로그램명+포트)가 아니면 종료 */
    if (argc != 2) {
        fprintf(stderr, "사용법: %s <포트번호>\n", argv[0]);
        exit(1);  /* 비정상 종료 (종료 코드 1) */
    }

    /* atoi() = 문자열 → 정수 변환
       "7777" → 7777 */
    int port = atoi(argv[1]);

    /* ── 변수 선언 ───────────────────────────────────────────
       server_fd = 서버 소켓 파일 디스크립터 (번호)
       client_fd = 클라이언트 연결 소켓 파일 디스크립터 */
    int server_fd, client_fd;

    /* sockaddr_in = 인터넷 소켓 주소 구조체
       server_addr = 서버 주소 (IP + 포트)
       client_addr = 연결된 클라이언트 주소 */
    struct sockaddr_in server_addr, client_addr;

    /* accept() 호출 시 client_addr 구조체 크기 전달용 */
    socklen_t client_len = sizeof(client_addr);

    /* HTTP 요청을 저장할 문자 배열 (버퍼) */
    char buffer[BUFFER_SIZE];

    /* ── 1. 소켓 생성 (socket) ───────────────────────────────
       AF_INET     = IPv4 주소 체계 사용
       SOCK_STREAM = TCP 사용 (신뢰성 있는 연결 지향)
       0           = 프로토콜 자동 선택 (TCP면 0)
       반환값: 소켓 파일 디스크립터 (양수) / 실패 시 -1 */
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        perror("socket 생성 실패");  /* 오류 메시지 출력 */
        exit(1);
    }

    /* ── 포트 재사용 옵션 설정 ───────────────────────────────
       SOL_SOCKET   = 소켓 레벨에서 옵션 적용
       SO_REUSEADDR = 동일 포트 재사용 허용
       → 서버 종료 후 바로 재시작해도 "Address already in use" 방지 */
    int opt = 1;
    setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    /* ── 2. 서버 주소 구조체 초기화 ─────────────────────────
       memset = 구조체 메모리를 0으로 초기화 (쓰레기 값 방지) */
    memset(&server_addr, 0, sizeof(server_addr));

    /* sin_family = 주소 체계 (AF_INET = IPv4) */
    server_addr.sin_family = AF_INET;

    /* INADDR_ANY = 0.0.0.0 = 모든 네트워크 인터페이스에서 수신
       → 어떤 IP로 접속해도 받을 수 있음 */
    server_addr.sin_addr.s_addr = INADDR_ANY;

    /* htons() = Host TO Network Short
       → CPU의 바이트 순서를 네트워크 바이트 순서(빅엔디안)로 변환
       → 인텔 CPU는 리틀엔디안, 네트워크는 빅엔디안이므로 반드시 변환 */
    server_addr.sin_port = htons(port);

    /* ── 3. 바인딩 (bind) ────────────────────────────────────
       소켓(server_fd)과 주소(server_addr)를 연결
       → 이 소켓이 port번 포트를 담당하겠다고 OS에 등록 */
    if (bind(server_fd,
             (struct sockaddr*)&server_addr,  /* 주소 구조체 포인터 */
             sizeof(server_addr)) < 0) {      /* 구조체 크기 */
        perror("bind 실패");
        exit(1);
    }

    /* ── 4. 연결 대기 상태 (listen) ─────────────────────────
       5 = 동시에 대기할 수 있는 최대 연결 요청 수 (backlog)
       → 이 상태부터 클라이언트가 연결 요청 가능 */
    if (listen(server_fd, 5) < 0) {
        perror("listen 실패");
        exit(1);
    }

    printf("서버 시작: 포트 %d에서 대기 중...\n", port);

    /* ── 5. 무한 루프: 클라이언트 계속 처리 ─────────────────
       서버는 꺼지지 않고 계속 클라이언트를 기다려야 함 */
    while (1) {

        /* ── 6. 연결 수락 (accept) ───────────────────────────
           클라이언트가 연결할 때까지 이 줄에서 블로킹(대기)
           연결되면 client_fd(클라이언트 전용 소켓) 반환
           client_addr에 클라이언트 IP·포트 저장 */
        client_fd = accept(server_fd,
                          (struct sockaddr*)&client_addr,
                          &client_len);
        if (client_fd < 0) {
            perror("accept 실패");
            continue;  /* 오류 시 다음 클라이언트 대기로 넘어감 */
        }

        printf("\n[연결됨]\n");
        printf("============================================================\n");

        /* ── 7. HTTP 요청 수신 (read) ────────────────────────
           memset으로 버퍼 초기화 (이전 데이터 제거)
           0 = 모든 바이트를 0으로 초기화 */
        memset(buffer, 0, BUFFER_SIZE);

        /* read() = 소켓에서 데이터 읽기
           client_fd     = 읽을 소켓
           buffer        = 데이터를 저장할 버퍼
           BUFFER_SIZE-1 = 최대 읽을 바이트 수 (-1은 null 종료 문자용)
           → 브라우저가 보낸 HTTP 요청 메시지 전체 수신 */
        read(client_fd, buffer, BUFFER_SIZE - 1);

        /* ── 8. HTTP 요청 콘솔 출력 (Part A 핵심) ───────────
           %s = 문자열로 출력
           → GET /파일경로 HTTP/1.1
             Host: ...
             User-Agent: ... 등 확인 */
        printf("%s\n", buffer);
        printf("============================================================\n");

        /* ── 9. 소켓 닫기 (close) ────────────────────────────
           클라이언트 소켓 자원 해제
           → 닫지 않으면 파일 디스크립터가 고갈됨 */
        close(client_fd);
    }

    /* 서버 소켓 닫기 (실제로는 무한루프로 여기 도달 안 함) */
    close(server_fd);
    return 0;
}
