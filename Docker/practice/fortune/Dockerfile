# Base image 설정
FROM debian:latest

# 패키지 업데이트 및 install fortune
RUN apt-get update \
    && apt-get install -y fortune

# 스크립트 파일을 컨테이너 내부로 복사
COPY webpage.sh /webpage.sh

# 스크립트 파일 실행권한 부여
RUN chmod +x /webpage.sh

# 컨테이너 시작 시 스크립트가 자동 실행되도록 설정
CMD ["/webpage.sh"]
