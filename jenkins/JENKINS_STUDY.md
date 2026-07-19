# Jenkins 개념 정리

CI/CD D2 이월분 — GitHub Actions만 써봤다가 처음으로 Jenkins를 설치·구성해본다. Jenkins를 아예 처음 쓰는 사람 기준으로 0장부터 시작하고, GitHub Actions와 비교하면서 "왜 둘 다 알아야 하는지"까지 정리한다.

---

## 0. Jenkins가 뭔가

**Jenkins**는 2011년부터 있어온 오픈소스 자동화 서버다(전신은 2004년 Hudson). "CI/CD 도구"의 원조격이라고 보면 된다 — GitHub Actions·GitLab CI·CircleCI 같은 이후 도구들이 등장하기 훨씬 전부터 업계 표준이었고, 지금도 많은 회사(특히 온프레미스·엔터프라이즈 환경)가 쓴다.

### GitHub Actions와 근본적으로 다른 점 — "관리형" vs "직접 호스팅"

지금까지 써온 GitHub Actions는 **SaaS(관리형)**이다 — 워크플로 파일만 레포에 커밋해두면, 실행 서버(러너)는 GitHub가 알아서 띄우고 관리해준다. 서버 설치·업데이트·보안 패치를 신경 쓸 필요가 없다.

Jenkins는 **직접 호스팅(self-hosted)**이다 — Jenkins 서버 자체를 내가 설치하고, 띄워두고, 계속 운영해야 한다. 이번 실습에서도 실제로 그 설치 과정 자체를 거쳤다(`JENKINS_PRACTICE.md` 참조). 이게 왜 여전히 널리 쓰이냐면:
- **완전한 제어권**: 사내 폐쇄망(인터넷 격리 환경)에서도 돌릴 수 있다. GitHub Actions는 GitHub 서버에 의존하니 이런 환경에서 못 쓴다.
- **방대한 플러그인 생태계**: 20년 가까이 쌓인 플러그인이 1,800개 이상 — 어떤 도구(레거시 시스템 포함)와도 연동 가능한 경우가 많다.
- **비용 구조**: 서버 유지 비용은 들지만, GitHub Actions처럼 "빌드 시간만큼 과금"되는 구조가 아니라 내가 가진 인프라를 그대로 쓴다.

반대로 단점은 "서버 자체를 내가 계속 돌보고 패치해야 한다"는 운영 부담 — 이번 실습에서 Jenkins를 직접 설치해보면서 이 부담을 실제로 체감했다(플러그인 설치, 재시작, 초기 계정 설정 전부 수동/스크립트로 직접 해야 했음).

---

## 1. 아키텍처 — Controller와 Agent

| 구성 | 역할 |
|---|---|
| **Controller**(예전 이름 Master) | Jenkins의 두뇌 — 웹 UI 제공, Job 스케줄링, 빌드 결과 저장. `jenkins/jenkins` 이미지를 띄우면 이게 뜨는 것. |
| **Agent**(예전 이름 Slave/Node) | 실제로 빌드가 실행되는 곳. Controller가 "이 Job을 실행해라"고 지시를 내리면 Agent가 받아서 실행한다. |

간단한 구성(이번 실습처럼 Jenkins 1개만 띄운 경우)은 **Controller가 Agent 역할도 겸한다**("built-in node") — Job이 몇 개 안 되거나 학습 목적이면 이걸로 충분하다. 회사에서 빌드량이 많아지면 Agent를 여러 대(심지어 여러 OS)로 분산시켜서 부하를 나눈다 — 예를 들어 "iOS 빌드는 macOS Agent, 안드로이드는 Linux Agent"처럼 특성이 다른 빌드를 각각 다른 서버에 맡길 수 있다는 게 GitHub Actions 러너보다 유연한 지점이다.

---

## 2. Job의 종류 — Freestyle vs Pipeline

Jenkins에서 "무엇을 자동화할지"를 정의하는 단위가 **Job**이다. 크게 두 방식이 있다:

- **Freestyle Job**: 웹 UI에서 "이 단계, 그 다음 이 단계..."를 클릭으로 하나씩 추가하는 옛날 방식. 설정이 Jenkins 내부 XML로만 저장돼서 Git으로 버전관리가 안 된다 — GitHub Actions의 YAML과 정반대 철학.
- **Pipeline Job**: **Jenkinsfile**이라는 코드로 전체 흐름을 정의하는 방식(2016년 이후 표준). 이게 GitHub Actions의 `.yml` 워크플로 파일에 대응하는 개념이고, Git에 커밋해서 버전관리할 수 있다("Pipeline as Code"). 이번 실습에서는 당연히 이 방식을 썼다.

**"Pipeline script from SCM"**: Jenkinsfile을 Jenkins Job 설정에 직접 붙여넣는 대신, "이 Git 레포의 이 경로에 있는 Jenkinsfile을 읽어서 실행해라"고 지정하는 방식 — 이번 실습에서 쓴 방식이다. `jenkins/Jenkinsfile.pf2`를 레포에 커밋해두고 Job은 그 경로만 가리키게 했다. 이러면 Jenkinsfile을 고칠 때마다 Job 설정을 안 건드려도 되고, Jenkinsfile 자체도 PR 리뷰·히스토리 추적 대상이 된다.

---

## 3. Jenkinsfile 구조 — Declarative Pipeline

```groovy
pipeline {
    agent any              // 어디서 실행할지

    environment {           // GitHub Actions의 env: 에 대응
        IMAGE_NAME = "pf2"
    }

    stages {                 // GitHub Actions의 jobs: 에 대응 — 순서대로 실행되는 큰 덩어리
        stage('Checkout') {
            steps { ... }     // GitHub Actions의 steps: 에 대응 — 그 안의 세부 명령
        }
        stage('Lint') {
            steps { ... }
        }
    }

    post {                   // GitHub Actions엔 없는 개념 - 성공/실패와 무관하게 항상(또는 조건부) 실행
        always { ... }
    }
}
```

**Declarative vs Scripted**: 위 예시처럼 `pipeline { ... }`로 시작하는 정형화된 문법이 **Declarative**(2016년 이후 권장 방식, 이번에 쓴 것) — GitHub Actions YAML과 발상이 비슷해서 익히기 쉽다. 반면 **Scripted**는 순수 Groovy 코드로 자유롭게 작성하는 옛날 방식(`node { stage(...) { ... } }`) — 유연하지만 문법이 자유로운 만큼 남이 읽기 어렵고 검증이 힘들다. 실무에서는 특별한 이유가 없으면 Declarative를 쓴다.

### GitHub Actions와 구조 대응표

| GitHub Actions | Jenkins Declarative Pipeline |
|---|---|
| workflow(`.yml` 파일 하나) | Jenkinsfile 하나 |
| `jobs:` 아래 각 job | `stages:` 아래 각 `stage()` |
| `steps:` | `steps { }` |
| `runs-on:` | `agent` |
| `env:` | `environment { }` |
| `needs:`로 순서 강제 | stage는 기본적으로 **순차 실행**(병렬은 `parallel` 블록으로 명시) |
| `if:` 조건 | `when { }` 블록 |
| (없음) | `post { }` — 항상/조건부 후처리 |

가장 큰 실행 모델 차이: GitHub Actions는 `needs`를 안 걸면 job이 **기본 병렬**이지만, Jenkins의 `stage`들은 **기본 순차**다(병렬로 하려면 오히려 명시적으로 `parallel`을 써야 함). 이번 Jenkinsfile의 Checkout→Lint→Test→Docker Build도 당연히 순서대로 돈다.

---

## 4. 플러그인 — Jenkins의 핵심 확장 방식

Jenkins 코어 자체는 기능이 거의 없다 — Git 연동도, Pipeline 문법도 전부 **플러그인**으로 추가된다. 이번 실습에서 아무 플러그인도 없는 상태로 시작해서(`0 plugins installed`), Pipeline 기능(`workflow-aggregator`)과 Git 연동(`git`)을 직접 설치해야 Job조차 못 만드는 상태를 실제로 겪었다 — GitHub Actions는 이런 "기본 기능조차 플러그인으로 깔아야 하는" 개념이 아예 없다(모든 기능이 처음부터 내장). 이 차이가 "관리형 vs 직접 호스팅"의 체감상 가장 큰 차이다.

---

## 5. Jenkins를 컨테이너로 띄울 때 생기는 특수한 함정 — Docker-outside-of-Docker

Jenkins 자체를 Docker 컨테이너로 띄우고, 그 안에서 "빌드할 때 또 Docker 컨테이너를 띄워야 하는" 상황(이번처럼 golang 컨테이너로 lint·test 하는 경우)이 되면 특이한 문제가 생긴다.

Jenkins 컨테이너에 호스트의 `/var/run/docker.sock`을 마운트해서 Jenkins 안에서 `docker` 명령을 쓸 수 있게 하는 방식을 **Docker-outside-of-Docker(DooD)**라 부른다(Docker 안에 진짜 Docker 데몬을 새로 설치하는 "Docker-in-Docker(DinD)"와 대비되는 개념). DooD의 함정: Jenkins 컨테이너 안에서 `docker run -v $PWD:/app ...`을 실행하면, `docker` 명령 자체는 **호스트의 Docker 데몬**에게 그대로 전달된다 — 그런데 `$PWD`는 "Jenkins 컨테이너 내부 경로"인데, 이 경로를 해석하는 건 호스트 데몬이라서 **호스트 파일시스템 기준으로** 그 경로를 찾는다. 그런 경로가 호스트에 없으면 Docker는 에러 없이 그냥 빈 디렉토리를 새로 만들어서 마운트해버린다 — "파일이 하나도 없다"는 이상한 결과가 조용히 나오는 이유다(실제로 이번 실습에서 정확히 이 문제를 겪었다, `JENKINS_PRACTICE.md` 참조).

**해결책**: 경로로 마운트하지 않고 `--volumes-from <컨테이너이름>`을 쓴다 — 이러면 Jenkins 컨테이너가 이미 갖고 있는 볼륨을 그대로 "참조로" 공유해서, 컨테이너 내부 경로가 양쪽에서 완전히 똑같아진다. 실무에서 Jenkins를 컨테이너로 운영할 때 흔히 마주치는 실전 지식이다.

---

## 6. 배운 것 — 언제 뭘 쓰나

- 이 포트폴리오처럼 GitHub에 코드가 있고 완전 관리형으로 충분하면 **GitHub Actions**가 설정도 적고 유지보수 부담이 없어 유리하다.
- 사내 폐쇄망, 레거시 시스템 연동, 세밀한 인프라 제어가 필요하면 **Jenkins**가 여전히 유효하다 — 특히 이미 Jenkins가 깔려 있는 회사(많다)에 입사하면 바로 읽고 고칠 수 있어야 한다.
- 두 도구의 개념(job/stage/step, 순차·병렬 실행, 트리거 조건)은 사실상 대응이 되므로, 하나를 제대로 알면 다른 하나는 "문법만 다른 같은 개념"으로 빠르게 익힐 수 있다는 걸 이번에 직접 확인했다.
