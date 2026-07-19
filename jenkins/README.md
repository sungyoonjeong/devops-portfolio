# Jenkins 실습

CI/CD 시리즈의 곁가지 — [`../cicd/`](../cicd/)에서 GitHub Actions로 만든 것과 똑같은 lint→test→docker-build 파이프라인을 Jenkins로도 만들어서 두 도구를 직접 비교했다. Jenkins는 이번이 처음이라 설치부터 시작.

이론은 `JENKINS_STUDY.md`(Jenkins가 뭔지부터, GitHub Actions와 비교), 실습 기록은 `JENKINS_PRACTICE.md`.

## 구성

- `JENKINS_STUDY.md` — Jenkins란 무엇인가, Controller/Agent, Freestyle vs Pipeline, Jenkinsfile 구조, 플러그인, Docker-outside-of-Docker 개념
- `JENKINS_PRACTICE.md` — Docker로 설치, Groovy 스크립트 콘솔로 초기설정(Jenkins as Code), 플러그인 설치, Job 생성, 실전 버그 2건(중첩 따옴표, DooD 경로 함정)과 해결, 최종 그린 확인
- `Jenkinsfile.pf2` — 실제로 돌린 파이프라인 정의(한 줄 주석 포함)

## 실행

```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword   # 최초 1회
# admin / devops2026! 로 로그인 (Groovy 스크립트로 직접 설정한 계정)
# http://localhost:8081
```

## 메모

- Jenkins를 컨테이너로 띄우고 그 안에서 또 `docker run`을 하면(Docker-outside-of-Docker), `-v 경로:/app`은 호스트 기준으로 잘못 해석된다 — `--volumes-from <컨테이너명>`을 써야 한다.
- `sh` 스텝 안에 `sh -c "..."`처럼 따옴표를 중첩시키지 말 것 — Groovy 이스케이프와 셸 이스케이프가 꼬인다. 명령을 여러 `sh` 스텝으로 쪼개는 게 안전하다.
- 이번 회차는 GUI 자동화 도구 장애로 웹 화면 스크린샷 없이 REST API·CLI로만 진행 — 모든 결과는 실제 실행·검증된 것.
- 다음: 이 3부작(CI/CD → ArgoCD → Observability)과 별개로, PF1에서 실제 운영 규모의 파이프라인에 재적용 검토.
