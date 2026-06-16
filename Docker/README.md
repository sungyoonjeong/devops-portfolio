# Docker

> 따배도(따라하며 배우는 도커) 25강 학습 정리 + 실습 7개

## 커버 범위

| 강의 범위 | 주요 내용 |
|----------|----------|
| 1~5강 | 컨테이너 개념·아키텍처·이미지 레이어 구조 |
| 9~10강 | 볼륨·바인드 마운트 |
| 11~15강 | 네트워크 (bridge·host·none·overlay) |
| 16~20강 | Dockerfile 작성·빌드 최적화 |
| 21~25강 | Docker Compose·멀티컨테이너 앱 |

## 구조

```
Docker/
├── 개념/      강의 정리 .md (전체정리.md 포함)
└── practice/  실습 7개 (build·composetest·fortune·genid·hellojs·lab8·webserver)
```

## 실습 목록

- `build/` — 기본 이미지 빌드
- `composetest/` — Flask + Redis Compose 구성
- `fortune/` — 랜덤 메시지 웹서버
- `genid/` — 컨테이너 ID 생성기
- `hellojs/` — Node.js 앱 컨테이너화
- `lab8/` — 디스크 사용량 모니터링
- `webserver/` — Nginx 웹서버

## DevOps 연결

모든 포트폴리오 프로젝트(PF1~PF-K8s)의 기반 기술.
