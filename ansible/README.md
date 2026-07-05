# Ansible 실습

Terraform으로 띄운 서버 안을 설정하는 구성 관리 도구 연습.
localhost를 대상으로 nginx 올리기부터 Role, Vault까지 돌려봤다.

이론 정리는 `ANSIBLE_STUDY.md`.

## 구성

- `hosts.ini` — 인벤토리 (localhost)
- `site.yml` — common + nginx role 실행 진입점
- `nginx.yml` — role로 나누기 전 단일 playbook
- `vault-test.yml` — vault 변수 복호화 확인
- `secret.yml` — ansible-vault로 암호화한 시크릿
- `roles/common` — git·htop·curl·vim 설치
- `roles/nginx` — nginx 설치·설정·기동 (handler로 재시작)

## 실행

```bash
ansible web -i hosts.ini -m ping
ansible-playbook -i hosts.ini site.yml -K
curl localhost
```

한 번 더 돌리면 `changed=0` — 멱등성.

Vault:
```bash
ansible-vault view secret.yml
ansible-playbook -i hosts.ini vault-test.yml --ask-vault-pass
```

## 메모

- 에이전트리스 — 관리대상엔 아무것도 안 깔고 SSH로만 붙는다.
- 핸들러(notify)는 설정이 바뀐 태스크가 있을 때만 돈다.
- `secret.yml`은 AES256 암호화라 커밋해도 열람 불가. 실행 때 `--ask-vault-pass`로 푼다.
- 다음: Terraform이 EC2 프로비저닝 → 그 서버를 Ansible로 설정 (D5).
