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

## 드릴 — site.yml + roles 무참조 재작성 (2패스)

원본을 안 보고 `site.yml`, `roles/common/tasks`, `roles/nginx/tasks`, `roles/nginx/handlers`를 기억만으로 다시 썼다. 구조(어떤 모듈을 쓰는지, 태스크 순서, handler 연결)는 전부 맞았고, 세부 값 몇 개를 놓쳤다 — 그 부분만 기록.

**맞은 것**: `apt` 모듈로 패키지 설치, `service` 모듈로 기동, `copy` 모듈 + `notify`로 파일 배포 후 핸들러 트리거, handler가 별도 파일(`handlers/main.yml`)에 분리돼 있다는 구조까지 전부 정확히 재현됨.

**놓친 것**:
| 항목 | 내가 쓴 것 | 원본 | 왜 차이났는지 |
|---|---|---|---|
| nginx 배포 파일 경로 | `copy: src: index.html, dest: /var/www/html/index.html` | `copy: content: "...", dest: /var/www/html/index.nginx-debian.html` | 원본은 파일을 따로 안 두고 `content:`로 내용을 바로 인라인했고, 경로도 Debian nginx 기본 welcome 파일(`index.nginx-debian.html`)을 직접 덮어쓰는 방식이었다 — 새 파일을 추가하는 게 아니라 기존 파일을 교체하는 접근이라는 걸 놓침. |
| handler 이름·동작 | `reload nginx` / `state: reloaded` | `restart nginx` / `state: restarted` | reload(설정만 다시 읽음)와 restart(프로세스 재시작)를 헷갈림 — 정적 파일 하나 바꾸는 거라 reload로도 충분할 것 같은데 원본은 restart를 씀. 재확인 필요한 부분. |
| YAML 시작 마커 `---` | 항상 붙임 | 없음 | 없어도 단일 문서면 동작에 지장 없음(문법상 선택) — 습관적으로 붙였는데 이 프로젝트 컨벤션은 생략 쪽. |

**결론**: 모듈 선택·태스크 흐름 같은 "설계"는 체화됐고, 파일 경로·handler 동작 같은 "구체적 값"은 재확인이 필요한 수준 — 다음 복습 때 이 표의 3줄만 다시 보면 됨.
