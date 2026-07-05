# Ansible 완전 정리집 — Jeff Geerling 「Ansible 101」 Ep1~15 종합

> 정성윤 DevOps 학습 노트 · 2026-07-05 작성
> 참고 커리큘럼: Jeff Geerling, *Ansible 101* (YouTube, 15편, 『Ansible for DevOps』 기반)
> **이 문서 하나만 보고 Ansible을 처음부터 끝까지 학습할 수 있도록 만든 독립 교재다.** 강의 자막이 부실해도 이 문서로 대체·보완된다. 개념·문법·예제·실행결과·트러블슈팅·완전 예제·면접까지 전부 포함.

---

## 이 문서 사용법

- **위에서 아래로 누적되는 구조**다. 앞 개념이 뒤의 전제가 되므로 순서대로 읽는다.
- 각 절은 **개념(왜) → 문법·예제 → 실무·면접 포인트** 순서.
- ⭐ 표시는 면접 단골 / 반드시 이해할 것.
- 코드 블록은 전부 실제로 돌아가는 예제다. 그대로 쳐보며 확인.
- 처음 배우는 사람 기준으로 용어를 그때그때 풀어 설명한다. 모르는 단어가 나오면 그 자리에서 정의를 붙여둔다.
- 막히면 **부록 D(트러블슈팅)**, 전체 흐름을 한 번에 보려면 **부록 E(완전한 미니 프로젝트)**로.

### 강의 에피소드 ↔ 이 문서 대응 (대략)

```
Ep 1~2    →  Part 0~2   (소개·설치·인벤토리·Ad-hoc)
Ep 3~4    →  Part 3~6   (플레이북·변수·조건·반복·핸들러·템플릿)
Ep 5      →  Part 7     (Role·Ansible Galaxy)
Ep 6      →  Part 8     (테스트: Molecule·ansible-lint·CI)
Ep 7      →  Part 9     (Ansible Vault·시크릿)
Ep 8      →  Part 10    (동적 인벤토리·클라우드)
Ep 9      →  Part 11    (AWX / Ansible Tower)
Ep 10~15  →  Part 12~13 (실전 배포·롤링업데이트·Kubernetes·네트워크·Q&A)
```

---

# Part 0. Ansible이란 & 아키텍처

## 0.1 Ansible이 푸는 문제

서버가 1대면 SSH 붙어서 손으로 설정하면 된다. **10대, 100대가 되면** 사람이 못 한다. 게다가 "3번 서버만 nginx 버전이 다르다" 같은 **구성 드리프트(configuration drift)**가 생긴다. Ansible은 "서버들이 이런 상태여야 한다"를 코드로 적어두고, 그 상태를 **여러 대에 동일하게, 반복적으로** 맞춘다. 이것이 **구성 관리(Configuration Management)**이자 **IaC(Infrastructure as Code)**의 한 축이다.

- **Terraform** = 인프라를 *만든다* (서버·네트워크·DB를 프로비저닝). "무(無) → 서버 존재".
- **Ansible** = 만들어진 서버 *안을 설정한다* (패키지 설치·설정파일·서비스 기동). "빈 서버 → 서비스 구동 상태".
- 둘은 경쟁이 아니라 짝. 실무 흐름: **Terraform이 EC2 띄우고 → Ansible이 그 EC2를 설정**. (오늘 D5가 정확히 이 연동.)

## 0.2 ⭐ 핵심 특징 3가지 (면접 필수)

1. **에이전트리스(Agentless)** — 관리대상 서버에 Ansible 전용 데몬을 설치하지 않는다. **SSH(리눅스)/WinRM(윈도우)** 로 붙어서 파이썬으로 모듈을 실행하고 빠져나온다. Chef/Puppet(에이전트 상주형)과의 가장 큰 차이. 도입 장벽이 낮다.
2. **멱등성(Idempotency)** — 같은 플레이북을 몇 번 돌려도 결과가 같다. "설치해라(명령)"가 아니라 "설치된 상태여야 한다(선언)"를 기술하므로, 이미 그 상태면 아무것도 바꾸지 않는다(`changed=0`). Terraform의 desired-state와 같은 사상.
3. **선언형에 가까운 절차형** — YAML로 "원하는 상태"를 선언하지만, task는 위에서 아래로 **순서대로** 실행된다(절차적). 순수 선언형인 Terraform과 이 지점이 다르다.

## 0.3 아키텍처 & 용어

```
[제어 노드 Control Node]  ← Ansible 설치된 유일한 곳 (내 WSL/노트북/CI서버)
        │  SSH
        ├──────────► [관리대상 Managed Node] web1  (아무것도 설치 안 함)
        ├──────────► [관리대상 Managed Node] web2
        └──────────► [관리대상 Managed Node] db1
```

- **Control Node(제어 노드)**: Ansible을 실행하는 곳. 제어 노드는 리눅스/맥이어야 함(윈도우는 WSL로).
- **Managed Node(관리대상 노드)**: 설정을 받는 서버. 파이썬만 있으면 됨(요즘 리눅스 기본 탑재).
- **Inventory(인벤토리)**: 관리대상 목록(주소록).
- **Module(모듈)**: 실제 작업 단위(`apt`, `copy`, `service`…). 관리대상에서 실행되고 결과를 JSON으로 반환.
- **Task(태스크)**: 모듈 한 번 호출.
- **Play(플레이)**: "어떤 호스트에 어떤 태스크들을"의 묶음.
- **Playbook(플레이북)**: play들을 담은 YAML 파일.
- **Role(롤)**: 재사용 가능한 플레이북 구성요소(폴더 구조 표준).
- **Collection(컬렉션)**: 모듈·롤·플러그인을 묶어 배포하는 패키지 단위(Ansible 2.10+).

## 0.4 설치 & 동작 원리

```bash
sudo apt install -y ansible        # 데비안/우분투
pip install ansible                 # 또는 파이썬 pip
ansible --version                   # 확인 (ansible-core 버전 + config 파일 경로 표시)
```

**동작 순서 (한 태스크가 실행되는 흐름):**
1. 제어 노드가 SSH로 관리대상에 접속.
2. 해당 모듈의 파이썬 코드를 임시 디렉터리에 복사.
3. 관리대상에서 파이썬으로 실행 → 결과(JSON) 반환.
4. 임시 파일 삭제 후 접속 종료.

이 구조라서 **관리대상에 에이전트가 필요 없다.** 단, 관리대상에 파이썬이 있어야 함.

## 0.5 SSH 연결 준비 (원격 서버를 관리할 때)

localhost 실습(`ansible_connection=local`)은 SSH가 필요 없지만, **진짜 원격 서버(EC2 등)를 관리하려면 SSH 접속이 먼저 뚫려 있어야** 한다. Ansible은 "이미 SSH로 붙을 수 있는" 서버를 전제로 한다.

**1) SSH 키 방식(권장) — 비밀번호 없이 접속:**
```bash
ssh-keygen -t ed25519                       # 키쌍 생성 (없으면)
ssh-copy-id ubuntu@10.0.0.11                 # 공개키를 서버에 등록 → 이후 비번 없이 접속
ssh ubuntu@10.0.0.11                         # 먼저 손으로 접속되는지 확인
```
EC2는 이미 `.pem` 키로 접속하므로 인벤토리에 `ansible_ssh_private_key_file=~/keys/key.pem`를 적으면 된다.

**2) 최초 접속 시 지문(fingerprint) 확인 문제:**
처음 접속하면 `Are you sure you want to continue connecting (yes/no)?`가 뜨는데, Ansible은 자동 실행이라 여기서 멈춘다. 두 해결책:
```bash
# 방법 A: 미리 손으로 한 번 ssh 접속해 known_hosts에 등록
# 방법 B: ansible.cfg 에서 지문 확인 끄기(실습 편의)
```
```ini
# ansible.cfg
[defaults]
host_key_checking = False
```
(프로덕션에선 켜두는 게 보안상 맞다. 실습 편의로만 끈다.)

**3) 연결 확인:**
```bash
ansible all -i hosts.ini -m ping
# SUCCESS + "ping": "pong" 이면 SSH·파이썬·인벤토리 모두 정상
# UNREACHABLE 이면 SSH 문제(키/보안그룹/IP), FAILED 면 파이썬/권한 문제
```

## 0.6 become — 권한 상승(sudo)

패키지 설치·서비스 제어·시스템 파일 수정은 **root 권한**이 필요하다. Ansible에서 sudo에 해당하는 것이 `become`이다.

```yaml
- hosts: web
  become: true            # 이 play의 모든 task를 sudo로 실행
  tasks:
    - apt: { name: nginx, state: present }
```
- 특정 task만: 그 task에 `become: true`.
- 다른 계정으로: `become_user: postgres`.
- **sudo에 비밀번호가 필요하면** 실행 시 `-K`(`--ask-become-pass`)로 물어보게 한다.
```bash
ansible-playbook -i hosts.ini site.yml -K     # BECOME password 입력
```
(EC2 우분투처럼 NOPASSWD sudo가 설정된 서버는 `-K` 없이도 된다.)

---

# Part 1. 인벤토리 (Inventory)

## 1.1 인벤토리란

Ansible이 관리할 호스트들의 **목록 + 그룹 + 변수**. 파일 하나(`hosts.ini`, `inventory.yml`)일 수도, 동적으로 생성될 수도 있다(Part 10).

## 1.2 정적 인벤토리 (INI 형식)

```ini
# hosts.ini
[web]
web1 ansible_host=10.0.0.11
web2 ansible_host=10.0.0.12

[db]
db1 ansible_host=10.0.0.21

[production:children]   # 그룹의 그룹 (web + db 를 묶음)
web
db

[web:vars]              # web 그룹 공통 변수
ansible_user=ubuntu
ansible_ssh_private_key_file=~/keys/prod.pem
```

- `[web]` = 그룹. `web1` = 호스트 별칭(alias). `ansible_host=` = 실제 IP/도메인.
- `[web:vars]` = 그룹 변수. `[production:children]` = 하위 그룹을 묶은 상위 그룹.
- **로컬 실습용** (오늘 D1~D3):
  ```ini
  [web]
  localhost ansible_connection=local
  ```
  `ansible_connection=local` = SSH 안 쓰고 제어 노드 자신에서 바로 실행.

## 1.3 YAML 형식 인벤토리 (동일 내용)

```yaml
all:
  children:
    web:
      hosts:
        web1: { ansible_host: 10.0.0.11 }
        web2: { ansible_host: 10.0.0.12 }
      vars:
        ansible_user: ubuntu
    db:
      hosts:
        db1: { ansible_host: 10.0.0.21 }
```

## 1.4 ⭐ 주요 연결 변수 (connection vars)

| 변수 | 의미 |
|------|------|
| `ansible_host` | 실제 IP/도메인 |
| `ansible_user` | SSH 접속 계정 |
| `ansible_ssh_private_key_file` | 개인키 경로 |
| `ansible_connection` | `ssh`(기본) / `local` / `docker` |
| `ansible_python_interpreter` | 관리대상 파이썬 경로(예: `/usr/bin/python3`) |
| `ansible_port` | SSH 포트(기본 22) |

## 1.5 인벤토리 확인 명령

```bash
ansible-inventory -i hosts.ini --list      # 전체 구조 JSON
ansible-inventory -i hosts.ini --graph     # 트리 형태로 그룹/호스트
ansible all -i hosts.ini --list-hosts      # 대상 호스트 목록
```

**실무 포인트**: 인벤토리는 보통 `production`, `staging` 파일로 **환경을 분리**한다. 같은 플레이북을 `-i production` / `-i staging`으로 갈아끼워 재사용.

---

# Part 2. Ad-hoc 명령 & 모듈

## 2.1 Ad-hoc이란

플레이북 파일 없이 **한 줄로 즉석에서** 실행하는 일회성 명령. 빠른 확인·긴급 작업에 쓴다(재사용·기록이 필요하면 플레이북으로).

```bash
ansible <패턴> -i <인벤토리> -m <모듈> -a "<인자>" [옵션]
```

- `<패턴>`: `all`, `web`, `web1`, `web*`, `web:db`(합집합), `web:!web2`(제외) 등.
- `-m`: 모듈명(생략 시 `command` 모듈).
- `-a`: 모듈에 넘길 인자.
- `--become` / `-b`: 권한 상승(sudo). `-K`: sudo 비번 물어보기(`--ask-become-pass`).

## 2.2 예제

```bash
ansible web -i hosts.ini -m ping                                  # 연결 확인 → pong
ansible web -i hosts.ini -m command -a "uptime"                   # 임의 명령
ansible web -i hosts.ini -m apt -a "name=htop state=present" -b -K  # 패키지 설치
ansible web -i hosts.ini -m service -a "name=nginx state=started" -b  # 서비스 기동
ansible web -i hosts.ini -m copy -a "src=./a.txt dest=/tmp/a.txt"   # 파일 복사
ansible web -i hosts.ini -m setup                                  # 모든 facts 수집(정보 덤프)
```

## 2.3 ⭐ 자주 쓰는 핵심 모듈

| 모듈 | 용도 |
|------|------|
| `ping` | 연결/파이썬 확인 |
| `command` / `shell` | 임의 명령 (shell은 파이프·리다이렉트 가능, command는 불가) |
| `apt` / `yum` / `dnf` / `package` | 패키지 관리 (`package`는 OS 무관 범용) |
| `service` / `systemd` | 서비스 기동/중지/재시작/enable |
| `copy` / `template` | 파일 배포 (template은 Jinja2 렌더링) |
| `file` | 파일/디렉터리 생성·권한·심볼릭링크 |
| `lineinfile` / `blockinfile` | 파일 특정 줄/블록 수정 |
| `user` / `group` | 계정·그룹 관리 |
| `git` | 저장소 클론/체크아웃 |
| `unarchive` | 압축 해제 |
| `get_url` | URL 다운로드 |
| `cron` | 크론잡 등록 |
| `debug` | 변수/메시지 출력(디버깅) |

**⭐ command vs shell**: `command`가 기본이자 권장(더 안전). `|`, `>`, `&&`, 환경변수(`$HOME`) 같은 셸 기능이 필요할 때만 `shell`. 둘 다 **멱등성이 없다**(매번 changed) — 가능하면 전용 모듈(apt/copy/service…)을 써라. 이게 실무 원칙.

---

# Part 3. 플레이북 (Playbook) 기초

## 3.1 플레이북 = Ad-hoc을 파일로

Ad-hoc 여러 개를 순서대로 **YAML 파일**에 담아 재사용·버전관리하는 것. 이게 Ansible의 본체.

```yaml
# site.yml
- name: 웹 서버 구성                 # play 이름
  hosts: web                          # 대상 그룹
  become: true                        # 전체 태스크 sudo로
  vars:
    http_port: 80
  tasks:
    - name: nginx 설치                # task (반드시 name 붙이는 습관)
      apt:
        name: nginx
        state: present
        update_cache: true

    - name: nginx 기동 + 부팅 시 자동시작
      service:
        name: nginx
        state: started
        enabled: true
```

실행:
```bash
ansible-playbook -i hosts.ini site.yml
ansible-playbook -i hosts.ini site.yml --check      # 드라이런(실제 변경 없이 예상만)
ansible-playbook -i hosts.ini site.yml --diff       # 파일 변경 내용 diff 표시
ansible-playbook -i hosts.ini site.yml -v           # 상세 로그(-vvv 까지)
```

## 3.2 ⭐ YAML 문법 주의점 (에러 최다 지점)

- **들여쓰기는 공백만**(탭 금지). 보통 2칸.
- `key: value` 는 콜론 뒤 **공백 필수**.
- 리스트는 `- `(하이픈+공백).
- 문자열에 `:`나 `{{ }}`가 들어가면 따옴표로 감쌀 것: `msg: "{{ var }} 입니다"`.
- 불리언은 `true/false`(권장) — `yes/no`도 되지만 통일할 것.

## 3.3 실행 결과 읽기 (PLAY RECAP)

```
web1 : ok=5  changed=2  unreachable=0  failed=0  skipped=1  rescued=0  ignored=0
```
- `ok` = 성공 태스크 수, `changed` = 실제 변경된 수, `failed` = 실패, `unreachable` = 접속 불가.
- ⭐ **두 번째 실행 시 `changed=0`**이 되어야 정상(멱등성). changed가 계속 뜨면 그 태스크는 멱등적이지 않게 짜인 것(주로 command/shell 남용).

---

# Part 4. 변수 (Variables) · Facts · Register

## 4.1 변수를 정의하는 곳 (우선순위 낮음→높음, 축약)

1. role `defaults/main.yml` (가장 약함, 덮어쓰기 쉬움)
2. 인벤토리 그룹/호스트 변수
3. 플레이북 `vars:` / `vars_files:`
4. role `vars/main.yml`
5. `-e` / `--extra-vars` (명령행, **가장 강함**)

⭐ 실무 원칙: **바뀔 여지가 있는 기본값은 `defaults`**, 절대 안 바뀌는 상수는 `vars`, 실행 시 주입은 `-e`.

## 4.2 변수 사용 (Jinja2)

```yaml
vars:
  app_name: myapp
  app_port: 8080
tasks:
  - name: 변수 출력
    debug:
      msg: "{{ app_name }} 가 {{ app_port }} 포트에서 실행"
```

`{{ }}` = 값 치환. `{% %}` = 로직(for/if). 변수 참조는 항상 `{{ }}`.

## 4.3 ⭐ Facts (자동 수집 시스템 정보)

플레이북 시작 시 `gather_facts`(기본 true)로 관리대상의 OS·IP·메모리·CPU 등을 자동 수집한다. `setup` 모듈이 그 일을 함.

```yaml
tasks:
  - debug: msg="OS 배포판 = {{ ansible_facts['distribution'] }}"
  - debug: msg="기본 IP = {{ ansible_default_ipv4.address }}"
  - debug: msg="CPU 코어 = {{ ansible_processor_vcpus }}"
```

자주 쓰는 fact: `ansible_distribution`, `ansible_distribution_version`, `ansible_hostname`, `ansible_default_ipv4.address`, `ansible_memtotal_mb`, `ansible_processor_vcpus`.

성능: facts 수집이 느리면 `gather_facts: false`로 끄거나 캐싱한다.

## 4.4 Register (태스크 결과를 변수로)

```yaml
tasks:
  - name: 디스크 확인
    command: df -h /
    register: disk_result           # 결과를 disk_result에 저장

  - name: 결과 출력
    debug:
      var: disk_result.stdout        # stdout / rc / changed 등 접근 가능
```

`register` + `when`(조건) 조합이 실무의 핵심 패턴: "무언가 확인 → 그 결과에 따라 분기".

---

# Part 5. 조건문 · 반복 · 핸들러 · 태그

## 5.1 조건문 (when)

```yaml
- name: 우분투에서만 apt 사용
  apt: { name: nginx, state: present }
  when: ansible_facts['distribution'] == "Ubuntu"

- name: 이전 태스크가 바뀌었을 때만
  command: /opt/reload.sh
  when: disk_result.changed
```

## 5.2 ⭐ 반복 (loop)

```yaml
- name: 패키지 여러 개 설치
  apt:
    name: "{{ item }}"
    state: present
  loop:
    - nginx
    - git
    - htop

# 딕셔너리 반복
- name: 사용자 여러 명 생성
  user:
    name: "{{ item.name }}"
    groups: "{{ item.group }}"
  loop:
    - { name: alice, group: dev }
    - { name: bob,   group: ops }
```
(구버전 `with_items`는 `loop`로 대체됨.)

## 5.3 ⭐ 핸들러 (Handlers) — 바뀔 때만 실행

**notify로 트리거되고, play 끝에 한 번만 실행**된다. "설정파일이 바뀌었을 때만 서비스 재시작"이 대표 용례.

```yaml
tasks:
  - name: nginx 설정 배포
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx          # 이 태스크가 changed 일 때만 핸들러 호출

handlers:
  - name: restart nginx            # notify의 이름과 일치해야 함
    service:
      name: nginx
      state: restarted
```

⭐ 왜 중요한가: 설정이 안 바뀌었으면 재시작도 안 한다 → 무의미한 서비스 재시작(다운타임) 방지 = 멱등성의 실전판. 여러 태스크가 같은 핸들러를 notify해도 **끝에 딱 한 번** 실행된다.

## 5.4 태그 (Tags)

```yaml
tasks:
  - name: nginx 설치
    apt: { name: nginx, state: present }
    tags: [nginx, install]
```
```bash
ansible-playbook site.yml --tags nginx          # nginx 태그만 실행
ansible-playbook site.yml --skip-tags install   # install 태그 제외
```
긴 플레이북에서 일부만 돌릴 때 유용.

## 5.5 블록 & 에러 처리 (block/rescue/always)

```yaml
tasks:
  - block:
      - command: /opt/risky.sh
    rescue:                          # 위에서 실패하면 실행 (try-catch의 catch)
      - debug: msg="실패 → 롤백 수행"
    always:                          # 성공/실패 무관 항상 실행 (finally)
      - debug: msg="정리 작업"
```

기타: `ignore_errors: true`(실패 무시), `failed_when`(실패 조건 커스텀), `changed_when`(changed 조건 커스텀).

---

# Part 6. 템플릿 (Jinja2)

## 6.1 template 모듈

`copy`는 파일을 그대로 복사, `template`은 **변수를 채워 렌더링 후** 복사. 설정파일 배포의 핵심.

```jinja
# templates/nginx.conf.j2
server {
    listen {{ http_port }};
    server_name {{ ansible_hostname }};
    root /var/www/{{ app_name }};
}
```
```yaml
- name: nginx 설정 렌더링
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/sites-available/default
  notify: restart nginx
```

## 6.2 Jinja2 문법 요약

```jinja
{{ variable }}                      # 값 치환
{{ var | default('없음') }}          # 필터: 기본값
{{ name | upper }}                  # 필터: 대문자
{% if env == 'prod' %} ... {% endif %}   # 조건
{% for host in groups['web'] %}
server {{ host }};
{% endfor %}                        # 반복 (예: LB upstream 목록 생성)
```

⭐ 자주 쓰는 필터: `default`, `upper/lower`, `join`, `length`, `to_json`, `to_nice_yaml`, `b64encode`. `groups['web']`로 인벤토리 그룹의 전 호스트를 순회하는 패턴(로드밸런서 설정 자동 생성)이 강력하다.

---

# Part 7. Role & Ansible Galaxy

## 7.1 ⭐ Role이란 & 왜

플레이북이 길어지면 유지보수가 안 된다. Role은 **역할 단위로 tasks/handlers/templates/vars를 표준 폴더 구조로 분리**해 재사용·배포 가능하게 만든 것. "nginx role", "docker role"처럼 조립한다.

```bash
ansible-galaxy init roles/docker    # 표준 뼈대 생성
```
생성 구조:
```
roles/docker/
├── tasks/main.yml        # 실제 작업 (필수, 시작점)
├── handlers/main.yml     # 핸들러
├── templates/            # Jinja2 템플릿 (.j2)
├── files/                # 그대로 복사할 파일
├── vars/main.yml         # 변수 (우선순위 높음)
├── defaults/main.yml     # 기본 변수 (우선순위 낮음, 덮어쓰기용)
├── meta/main.yml         # 의존성·메타데이터
└── README.md
```

## 7.2 Role 사용

```yaml
# site.yml
- hosts: web
  become: true
  roles:
    - common          # roles/common
    - docker          # roles/docker
    - nginx

# 변수 넘기며 호출
- hosts: web
  roles:
    - role: nginx
      vars: { http_port: 8080 }
```

Ansible은 role 호출 시 `tasks/main.yml`, `handlers/main.yml`, `defaults/main.yml` 등을 자동으로 로드한다. `templates/`, `files/` 경로도 자동 인식(상대경로로 파일명만 써도 됨).

## 7.3 Ansible Galaxy (공유 저장소)

남이 만든 검증된 role/collection을 받아 쓴다(npm/pip 같은 것).

```bash
ansible-galaxy role install geerlingguy.nginx     # 유명한 Geerling의 role들
ansible-galaxy collection install community.docker
```
```yaml
# requirements.yml — 의존성 명시
roles:
  - name: geerlingguy.docker
collections:
  - name: community.general
```
```bash
ansible-galaxy install -r requirements.yml
```

⭐ 실무: 바퀴를 재발명하지 말 것. `geerlingguy.*` role들은 사실상 표준. 단, 프로덕션 투입 전 코드 검토는 필수.

---

# Part 8. 테스트 (Molecule · ansible-lint · CI)

## 8.1 왜 테스트하나

Role이 "정말 멱등적인지, 여러 OS에서 도는지"를 자동 검증. 인프라 코드도 코드다 → CI에 태운다.

## 8.2 ansible-lint (정적 분석)

```bash
pip install ansible-lint
ansible-lint site.yml       # 안티패턴·문법·베스트프랙티스 위반 탐지
```
`command` 남용, `name` 누락, 권한 문제 등을 잡아준다. (Terraform의 `checkov`와 같은 위치.)

## 8.3 ⭐ Molecule (role 통합 테스트)

Docker 컨테이너를 띄워 role을 실제 적용하고, **멱등성까지 자동 검증**하는 프레임워크.

```bash
pip install molecule molecule-plugins[docker]
cd roles/docker
molecule init scenario           # molecule/ 디렉터리 생성
molecule test                    # 전체 시나리오 실행
```
molecule test 단계: `create`(컨테이너 생성) → `converge`(role 적용) → **`idempotence`(다시 적용해 changed=0 확인)** → `verify`(검증) → `destroy`. idempotence 단계가 핵심 — 두 번째 적용에서 변경이 생기면 실패 처리.

## 8.4 CI 연동 (GitHub Actions)

```yaml
# .github/workflows/ci.yml (개념)
- run: pip install ansible ansible-lint molecule molecule-plugins[docker]
- run: ansible-lint
- run: molecule test
```
push마다 lint + molecule로 role 품질을 자동 게이트. (다음 주 CI/CD 학습과 직결.)

---

# Part 9. Ansible Vault (시크릿 관리)  ← 오늘 D4

## 9.1 왜

DB 비밀번호·API 키·TLS 키를 **평문으로 git에 올리면 안 된다**. Vault는 파일(또는 특정 변수)을 **AES256으로 암호화**해서, 암호화된 채로 저장·커밋하고 실행 시점에만 복호화한다.

## 9.2 ⭐ 핵심 명령

```bash
ansible-vault create secret.yml       # 새 암호화 파일 생성(편집기 열림)
ansible-vault edit secret.yml         # 암호화된 채로 편집
ansible-vault view secret.yml         # 복호화해서 보기만
ansible-vault encrypt vars/prod.yml   # 기존 평문 파일을 암호화
ansible-vault decrypt vars/prod.yml   # 다시 평문으로
ansible-vault rekey secret.yml        # 암호(키) 변경
```

실행 시 복호화:
```bash
ansible-playbook site.yml --ask-vault-pass                     # 실행 때 비번 입력
ansible-playbook site.yml --vault-password-file ~/.vault_pass  # 파일에서 비번 읽기(CI용)
```

## 9.3 변수 하나만 인라인 암호화

```bash
ansible-vault encrypt_string 'SuperSecret123' --name 'db_password'
# 출력된 !vault | ... 블록을 vars 파일에 그대로 붙여넣기
```

## 9.4 ⭐ Ansible Vault vs HashiCorp Vault (면접 단골)

| | **Ansible Vault** | **HashiCorp Vault** |
|--|-------------------|---------------------|
| 성격 | 파일/변수 **정적 암호화** | 시크릿 **동적 발급·중앙관리** 서버 |
| 저장 | 암호화 파일을 git에 커밋 | 중앙 서버가 발급, 짧은 TTL |
| 회수 | 수동 rekey | 자동 만료·회수(lease) |
| 연동 | Ansible 전용 | K8s Auth, DB 동적 크리덴셜, PKI 등 |

**면접 답변 한 문장**: *"정적인 값(설정파일 속 비번)은 Ansible Vault로 암호화해 커밋하고, 동적으로 발급·회수해야 하는 크리덴셜(DB·클라우드)은 HashiCorp Vault로 중앙관리하며 K8s Auth로 연동한다."* — 오늘 D4는 여기까지 아는 게 목표(HashiCorp Vault 실습은 아님).

---

# Part 10. 동적 인벤토리 (Dynamic Inventory) · 클라우드

## 10.1 왜

클라우드는 서버가 **오토스케일로 수시로 뜨고 진다**. IP를 손으로 인벤토리에 적을 수 없다 → 클라우드 API로 **실시간 조회해서 인벤토리를 생성**한다.

## 10.2 AWS EC2 예시

```yaml
# inventory_aws_ec2.yml
plugin: amazon.aws.aws_ec2
regions:
  - ap-northeast-2
filters:
  tag:Environment: production
keyed_groups:
  - key: tags.Role         # tag:Role=web 이면 자동으로 web 그룹에
    prefix: role
```
```bash
ansible-galaxy collection install amazon.aws
ansible-inventory -i inventory_aws_ec2.yml --graph   # 실시간 EC2 조회
ansible-playbook -i inventory_aws_ec2.yml site.yml
```

⭐ 이게 **Terraform+Ansible 실무 연동의 완성형**: Terraform이 태그 붙여 EC2 생성 → 동적 인벤토리가 태그로 자동 그룹핑 → Ansible이 설정. (오늘 D5는 정적 인벤토리 버전, 이건 그 다음 단계.)

---

# Part 11. AWX / Ansible Tower (AAP)

## 11.1 무엇

CLI Ansible에 **웹 UI·권한관리·스케줄·API·로그**를 입힌 것. Tower(상용, 현 Ansible Automation Platform) / **AWX(그 오픈소스판)**.

## 11.2 왜 팀에서 쓰나

- **RBAC**: 누가 어떤 플레이북을 어떤 인벤토리에 돌릴 수 있는지 권한 분리.
- **크리덴셜 중앙관리**: SSH키·Vault 비번을 UI에 안전 보관.
- **스케줄·API·웹훅**: 정기 실행, 외부 트리거(CI/CD에서 호출).
- **감사 로그**: 누가 언제 무엇을 실행했는지 기록.

개인 학습 단계에선 개념만: "CLI Ansible을 조직이 통제·자동화하려면 AWX/Tower를 얹는다." 보통 **K8s 위에 Operator로 배포**한다.

---

# Part 12. 실전 패턴 (배포 · 무중단)

## 12.1 롤링 업데이트 (serial)

```yaml
- hosts: web
  serial: 2            # 한 번에 2대씩만 (전체 다운타임 방지)
  tasks:
    - name: 앱 배포
      ...
    - name: 헬스체크
      uri: { url: "http://localhost/health", status_code: 200 }
```
`serial: "25%"`처럼 비율도 가능. LB에서 빼기 → 배포 → 헬스체크 → LB에 넣기 순으로 무중단 배포를 구성한다.

## 12.2 delegate_to / run_once

```yaml
- name: 로드밸런서에서 이 서버 제거
  command: /opt/lb_remove.sh {{ inventory_hostname }}
  delegate_to: lb1               # 이 태스크는 lb1에서 실행

- name: DB 마이그레이션(한 번만)
  command: /opt/migrate.sh
  run_once: true                 # 그룹 전체에서 딱 한 번
```

## 12.3 대표 실전 플레이북 흐름 (LAMP/앱 배포)

1. `common` role: 공통 패키지·시간대·보안(방화벽·SSH 하드닝).
2. `db` role: PostgreSQL 설치·설정·유저 생성(비번은 Vault).
3. `app` role: 코드 배포(git)·의존성·서비스 등록.
4. `web` role: nginx 리버스프록시·TLS·업스트림(템플릿으로 자동 생성).
5. 배포 시 `serial`로 롤링 + `uri` 헬스체크.

---

# Part 13. Ansible + 클라우드/컨테이너/네트워크 (강의 후반)

## 13.1 Ansible for Kubernetes

- `kubernetes.core` 컬렉션의 `k8s` 모듈로 매니페스트를 선언적으로 적용(`kubectl apply`의 Ansible판).
- **AWX/AAP 자체가 K8s 위에서 구동**되는 경우가 많음.
- Terraform으로 EKS 생성 → Ansible로 클러스터 애드온/앱 배포 조합.

## 13.2 Ansible for Networking

- Cisco/Juniper 등 네트워크 장비를 `ios_*`, `nxos_*` 모듈로 설정 관리(에이전트리스라 장비 친화적).
- ⭐ 본인 CCNP 배경과 직결 — "네트워크 자동화" 서사로 면접 차별화 포인트.

## 13.3 Windows 관리

- 관리대상이 윈도우면 SSH 대신 **WinRM**, 모듈은 `win_*` 계열.

---

# 부록 A. 베스트 프랙티스 ⭐

1. **모든 task에 `name`을 붙여라** — 로그 가독성·디버깅.
2. **command/shell을 남용하지 마라** — 전용 모듈(apt/copy/service)이 멱등적이고 안전.
3. **role로 구조화** — 플레이북 하나에 다 넣지 말 것.
4. **변수는 defaults에 기본값, 환경별은 group_vars/host_vars**.
5. **시크릿은 반드시 Vault** — 평문 커밋 금지.
6. **`--check`(드라이런)·`--diff`로 먼저 확인** 후 실제 적용.
7. **ansible-lint + molecule를 CI에** — 인프라 코드도 테스트.
8. **멱등성 검증**: 두 번 돌려 `changed=0` 확인을 습관화.
9. **환경 분리**: `inventory/production`, `inventory/staging` 파일 분리.
10. **버전 고정**: `requirements.yml`로 role/collection 버전 관리.

## group_vars / host_vars 구조 (실무 표준 레이아웃)

```
inventory/
├── production/
│   ├── hosts.ini
│   ├── group_vars/
│   │   ├── all.yml          # 전 호스트 공통
│   │   └── web.yml          # web 그룹 변수
│   └── host_vars/
│       └── web1.yml         # web1 개별 변수
├── staging/...
roles/
site.yml
requirements.yml
ansible.cfg
```

## ansible.cfg (자주 쓰는 설정)

```ini
[defaults]
inventory = ./inventory/production/hosts.ini
host_key_checking = False      # 최초 SSH 지문 확인 스킵(실습 편의)
roles_path = ./roles
remote_user = ubuntu
[privilege_escalation]
become = True
```

---

# 부록 B. 명령어 치트시트

```bash
# Ad-hoc
ansible all -i inv -m ping
ansible web -i inv -m apt -a "name=nginx state=present" -b -K
ansible web -i inv -m setup                        # facts 덤프

# 플레이북
ansible-playbook -i inv site.yml
ansible-playbook -i inv site.yml --check --diff     # 드라이런 + 변경내용
ansible-playbook -i inv site.yml --tags nginx       # 태그 일부만
ansible-playbook -i inv site.yml -e "http_port=8080"  # 변수 주입
ansible-playbook -i inv site.yml --limit web1        # 특정 호스트만

# 인벤토리
ansible-inventory -i inv --graph
ansible-inventory -i inv --list

# Role / Galaxy
ansible-galaxy init roles/myrole
ansible-galaxy install -r requirements.yml

# Vault
ansible-vault create/edit/view/encrypt/decrypt/rekey <file>
ansible-playbook site.yml --ask-vault-pass

# 테스트
ansible-lint
molecule test
```

---

# 부록 C. 면접 예상 Q&A ⭐

**Q. Ansible이 뭐고 왜 쓰나?**
A. 에이전트리스 구성관리·자동화 도구. SSH로 붙어 멱등적으로 여러 서버를 동일 상태로 맞춘다. 수작업 대비 재현성·확장성·구성드리프트 방지.

**Q. 멱등성이 뭔가?**
A. 같은 플레이북을 몇 번 돌려도 결과가 같은 성질. "명령"이 아니라 "원하는 상태"를 선언하므로, 이미 그 상태면 변경하지 않는다(changed=0). command/shell은 멱등성이 없어 지양한다.

**Q. Ansible vs Terraform?**
A. Terraform은 인프라를 *만들고*(프로비저닝), Ansible은 만들어진 서버 *안을 설정*한다. 실무에선 Terraform으로 EC2 생성 → 태그 → 동적 인벤토리 → Ansible로 설정, 이렇게 짝으로 쓴다.

**Q. Chef/Puppet과 차이?**
A. Chef/Puppet은 에이전트 상주형(pull), Ansible은 에이전트리스(push, SSH). 도입이 가볍고 학습곡선이 완만하다.

**Q. 핸들러는 언제 쓰나?**
A. "설정이 바뀌었을 때만" 서비스를 재시작할 때. notify로 트리거되고 play 끝에 한 번만 실행 → 불필요한 재시작(다운타임) 방지.

**Q. 시크릿 관리는?**
A. 정적 값은 Ansible Vault로 AES256 암호화해 커밋, 동적 크리덴셜은 HashiCorp Vault로 중앙관리·K8s Auth 연동.

**Q. Role을 쓰는 이유?**
A. 재사용·구조화. tasks/handlers/templates/vars/defaults 표준 구조로 역할 단위 분리 → 조립식 구성, Galaxy로 공유.

**Q. 동적 인벤토리?**
A. 클라우드에서 오토스케일로 IP가 수시로 바뀌므로, 클라우드 API로 실시간 조회해 인벤토리를 생성한다(aws_ec2 플러그인, 태그 기반 그룹핑).

---

# 오늘(7/5) D1~D4 실습 체크포인트 매핑

```
D1  Part 0~2   구조·인벤토리·Ad-hoc·멱등성
    완료기준: ping pong ✅ / apt 재실행 changed=0 눈으로 확인

D2  Part 3~6   Playbook·변수·핸들러·템플릿
    완료기준: nginx.yml 실행 → curl로 페이지 확인 / 재실행 시 handler 안 뜸

D3  Part 7     Role·ansible-galaxy
    완료기준: ansible-galaxy init 로 만든 docker role을 site.yml에서 실행

D4  Part 9     Ansible Vault
    완료기준: vault로 파일 암호화→view 복호화 / 정적 vs 동적 한 문장 설명

커밋  이 폴더(ansible/) 정리 + README + git commit
```

---

# 부록 D. 트러블슈팅 — 자주 나는 에러 & 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `UNREACHABLE ... Failed to connect` | SSH 문제(키·보안그룹·IP·포트) | 먼저 `ssh user@host` 손으로 접속되는지 확인. EC2면 보안그룹 22번·본인IP 허용 |
| `Are you sure you want to continue connecting` 에서 멈춤 | known_hosts 미등록 | `host_key_checking = False` 또는 미리 손 ssh |
| `Missing sudo password` | become 비번 필요 | `-K` 붙이기 (`--ask-become-pass`) |
| `/usr/bin/python: not found` | 관리대상에 파이썬 없음/경로 다름 | 인벤토리에 `ansible_python_interpreter=/usr/bin/python3` |
| `changed`가 매번 뜸(멱등성 깨짐) | command/shell 남용 | 전용 모듈(apt/copy/service)로 교체하거나 `changed_when` 지정 |
| `apt` 설치 실패 `Could not get lock` | 캐시/락 문제 | `update_cache: true` 추가, 또는 잠시 후 재시도 |
| YAML `could not find expected ':'` | 들여쓰기(탭)·콜론 뒤 공백 누락 | 공백 2칸 통일, `key: value` 공백 확인 |
| `{{ var }}` 가 문자 그대로 출력 | 따옴표/이스케이프 문제 | 값 전체를 `"{{ var }}"`로 감싸기 |
| 변수가 예상과 다른 값 | 변수 우선순위 | `-e`가 최강. `ansible-playbook ... -e "var=값"`로 확인, `--extra-vars` 우선 |

**디버깅 3종 세트:**
```bash
ansible-playbook site.yml --check --diff     # 실제 변경 없이 예상 + 파일 diff
ansible-playbook site.yml -vvv               # 상세 로그(어디서 왜 실패했는지)
```
```yaml
- debug: var=some_variable                   # 플레이북 중간에 변수 값 찍어보기
```

---

# 부록 E. 완전한 미니 프로젝트 (처음부터 끝까지)

아래를 그대로 따라 하면 **인벤토리 → 플레이북 → 롤 → 템플릿 → 핸들러 → Vault**가 한 번에 도는 완결 예제가 된다. 이 폴더(`ansible/`)에 그대로 만들면 오늘 D1~D4 산출물이 된다.

## 디렉터리 구조

```
ansible/
├── ansible.cfg
├── hosts.ini
├── site.yml
├── group_vars/
│   └── web.yml
└── roles/
    ├── nginx/
    │   ├── tasks/main.yml
    │   ├── handlers/main.yml
    │   └── templates/index.html.j2
    └── docker/
        └── tasks/main.yml
```

## 1) ansible.cfg
```ini
[defaults]
inventory = ./hosts.ini
host_key_checking = False
roles_path = ./roles
```

## 2) hosts.ini (로컬 실습)
```ini
[web]
localhost ansible_connection=local
```

## 3) group_vars/web.yml (web 그룹 공통 변수)
```yaml
http_port: 80
site_title: "Hello Ansible from {{ inventory_hostname }}"
```

## 4) roles/nginx/tasks/main.yml
```yaml
- name: nginx 설치
  apt:
    name: nginx
    state: present
    update_cache: true

- name: 홈페이지 배포(템플릿 렌더링)
  template:
    src: index.html.j2
    dest: /var/www/html/index.nginx-debian.html
  notify: restart nginx

- name: nginx 기동 + 부팅 자동시작
  service:
    name: nginx
    state: started
    enabled: true
```

## 5) roles/nginx/handlers/main.yml
```yaml
- name: restart nginx
  service:
    name: nginx
    state: restarted
```

## 6) roles/nginx/templates/index.html.j2
```jinja
<html>
  <body>
    <h1>{{ site_title }}</h1>
    <p>포트: {{ http_port }} / OS: {{ ansible_facts['distribution'] }}</p>
  </body>
</html>
```

## 7) roles/docker/tasks/main.yml
```yaml
- name: 사전 패키지
  apt:
    name: [ca-certificates, curl, gnupg]
    state: present
    update_cache: true

- name: docker.io 설치(실습용 간단 버전)
  apt:
    name: docker.io
    state: present

- name: docker 서비스 기동
  service:
    name: docker
    state: started
    enabled: true
```

## 8) site.yml (전체를 조립)
```yaml
- name: 웹 서버 전체 구성
  hosts: web
  become: true
  roles:
    - nginx
    - docker
```

## 9) 실행 & 검증
```bash
cd ansible
ansible-playbook site.yml -K                 # 전체 실행 (sudo 비번 물으면 입력)
curl localhost                               # <h1>Hello Ansible ...</h1> 나오면 성공
ansible-playbook site.yml -K                 # 다시 실행 → changed=0 (멱등성 확인)
```

## 10) Vault 붙이기 (D4)
```bash
ansible-vault create group_vars/secret.yml   # db_password: "s3cr3t" 입력·저장
ansible-vault view group_vars/secret.yml     # 복호화해서 확인
# 실행 시:
ansible-playbook site.yml -K --ask-vault-pass
```

이 10단계를 끝내면 D1(인벤토리·멱등성)·D2(플레이북·템플릿·핸들러)·D3(롤)·D4(Vault)가 **하나의 프로젝트 안에서 전부 커버**된다. 그대로 커밋하면 오늘 목표 완료.

---

# 부록 F. 용어 사전 (빠른 참조)

- **제어 노드**: Ansible이 설치돼 명령을 내리는 곳(내 WSL).
- **관리대상 노드**: 설정을 받는 서버.
- **인벤토리**: 관리대상 목록·그룹·변수 파일.
- **모듈**: 실제 작업 단위(apt, copy, service…). 멱등적으로 설계됨.
- **태스크**: 모듈 한 번 호출.
- **플레이**: "어떤 호스트에 어떤 태스크들"의 묶음.
- **플레이북**: play들을 담은 YAML.
- **롤**: 재사용 가능한 플레이북 구성요소(표준 폴더 구조).
- **핸들러**: notify로 호출되어 play 끝에 한 번 실행되는 태스크(주로 재시작).
- **facts**: 관리대상에서 자동 수집한 시스템 정보.
- **register**: 태스크 결과를 변수로 저장.
- **become**: 권한 상승(sudo).
- **멱등성**: 몇 번 실행해도 같은 결과.
- **Vault**: 시크릿 암호화 기능.
- **Galaxy**: role/collection 공유 저장소.
- **컬렉션**: 모듈·롤·플러그인 배포 단위.
- **AWX/Tower**: Ansible에 웹UI·RBAC·스케줄을 입힌 플랫폼.

---

> 이 문서는 자립형 교재다. 강의를 못 듣거나 자막이 부실해도 **이것만으로 D1~D4 학습과 실습이 완결**된다. 부록 E를 따라 실제로 손으로 돌려보는 것이 가장 빠른 습득 경로.
