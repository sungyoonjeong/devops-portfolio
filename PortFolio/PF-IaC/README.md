# PF-IaC — Terraform + Ansible AWS 인프라 자동화

> 완료: 2026-07-06
> 기술: `Terraform` `Ansible` `AWS EC2` `nginx` `Docker`

Terraform이 실 AWS에 서버를 만들고, Ansible이 그 서버 내부를 구성한다.
프로비저닝(Terraform)과 구성관리(Ansible)의 역할 분리를 실제 배포로 확인한 프로젝트.

**실습 전체 기록·코드: [terraform/pf-IaC/](../../terraform/pf-IaC/)** (스크린샷 증적 포함)

## 한 것

1. **Terraform** — EC2(Ubuntu 22.04, t3.micro) + 키페어 + 보안그룹(22/80), AMI는 data 소스로 최신 조회, 첫 실 AWS 배포
2. **수동 서버 구성 1회** — 자동화 전에 같은 작업을 손으로: apt nginx 설치, /etc/nginx 구조 분석(include·심볼릭 링크·server 블록), 설정을 일부러 깨고 `nginx -t` 에러 판독, reload 사이클
3. **Ansible 재구성** — nginx를 purge하고 같은 상태를 playbook으로 재현: nginx + index.html + charset 설정 + docker, 설정 변경 시에만 도는 reload 핸들러
4. **검증** — 퍼블릭 IP 페이지 확인, charset 헤더, 재실행 `changed=0`(멱등성), `terraform destroy`로 종료

## 관련 실습 폴더

- [terraform/](../../terraform/) — D1~D5: HCL 기초 → 모듈화 → 원격 state → Workspace → 3-tier 통합 (LocalStack)
- [ansible/](../../ansible/) — D1~D4: 인벤토리·Playbook·Role·Vault (localhost)
- 이 프로젝트가 위 두 트랙의 통합 결과물
