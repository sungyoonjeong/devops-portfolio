# PF2 — Go + Docker 마이크로서비스 배포 자동화

> 작업 예정: 2026-06-21 ~ 06-22  
> 기술: `Go` `Docker` `Docker Compose` `Bash` `AWS ECR`

## 구성

```
PF2/
├── main.go              Go HTTP 서버 (/health, /metrics 엔드포인트)
├── Dockerfile           멀티스테이지 빌드 (builder → alpine)
├── docker-compose.yml   app + nginx 리버스프록시
├── nginx.conf
├── deploy.sh            빌드 → ECR 푸시 → 컨테이너 재시작 → 헬스체크
└── README.md
```

## 목표

- Go 서버를 Docker 이미지로 패키징 후 AWS ECR에 자동 푸시
- `deploy.sh` 한 줄로 배포 완료
- 면접 포인트: "왜 멀티스테이지 빌드를 썼나요?" → 최종 이미지 크기 최소화

<!-- 작업 시작 후 업데이트 예정 -->
