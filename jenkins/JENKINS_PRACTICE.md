# Jenkins 실습 — 설치부터 PF2 파이프라인 그린까지

목표: Jenkins를 처음부터 설치하고, PF2용 Jenkinsfile을 작성해서 GitHub Actions와 동일한 lint→test→docker-build 3단계를 재현한다. 개념은 [JENKINS_STUDY.md](JENKINS_STUDY.md) 참조.

이번 회차는 GUI 자동화 도구(`win`)가 WSL↔Windows 연동 장애로 완전히 막혀서, 웹 브라우저 화면 대신 **Jenkins REST API와 CLI로 전 과정을 실제 실행하고 그 결과를 그대로 기록**했다. 화면 캡처는 없지만 모든 명령과 응답은 실제로 실행해서 검증한 것이다.

---

## 1. Jenkins 설치 — Docker 컨테이너로

```bash
$ docker volume create jenkins_home
$ docker run -d --name jenkins -p 8081:8080 -p 50000:50000 \
    -v jenkins_home:/var/jenkins_home \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -u root jenkins/jenkins:lts-jdk17
```

- `-v jenkins_home:/var/jenkins_home`: Job 설정·빌드 이력을 컨테이너 밖(named volume)에 보존 — 컨테이너를 지워도 데이터는 남는다.
- `-v /var/run/docker.sock:/var/run/docker.sock`: Jenkins 안에서 `docker` 명령을 쓸 수 있게 호스트의 Docker 소켓을 공유(Docker-outside-of-Docker, `JENKINS_STUDY.md` 5장 참조).
- 포트를 `8081:8080`으로 잡은 이유: 로컬 8080은 이미 ArgoCD `kubectl port-forward`가 쓰고 있어서 충돌 — 처음엔 8080으로 띄우려다 `address already in use` 에러를 보고 8081로 바꿨다.

컨테이너가 중간에 한 번 죽어서(세션 환경 재시작 추정, exit code 143=SIGTERM) `docker start jenkins`로 재기동한 적이 있다 — named volume 덕분에 재기동 후에도 상태(플러그인·Job)는 그대로 유지됐다.

---

## 2. 초기 설정 — 웹 위저드 대신 "Jenkins as Code"로 자동화

Jenkins를 처음 띄우면 브라우저로 초기 비밀번호를 입력하고 플러그인을 고르는 설정 마법사가 뜬다. 이번엔 브라우저를 못 써서, **Groovy 스크립트 콘솔(REST API)로 그 과정을 코드로 대체**했다 — 이 방식 자체가 실무에서 "여러 Jenkins 인스턴스를 매번 손으로 클릭하지 않고 동일하게 세팅"할 때 실제로 쓰는 패턴(Jenkins Configuration as Code)이라, 오히려 더 실무에 가까운 경험이 됐다.

```bash
$ docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
d80445aebe254c1ba6cd3a6b5e9b5da0
```

Jenkins의 스크립트 콘솔 API(`/scriptText`)는 CSRF 보호(crumb)가 걸려 있어, 먼저 crumb을 발급받고 그 값을 헤더에 실어 보내야 한다:

```bash
$ curl -s -c cookies.txt -u admin:<초기비번> 'http://localhost:8081/crumbIssuer/api/json'
{"crumb":"1a2571ca...","crumbRequestField":"Jenkins-Crumb"}

$ curl -s -b cookies.txt -u admin:<초기비번> -H "Jenkins-Crumb: 1a2571ca..." \
    -X POST http://localhost:8081/scriptText --data-urlencode "script=..."
```

이 콘솔로 실제 admin 계정 생성 + 보안 설정 + 설정 마법사 skip까지 한 번에 실행:

```groovy
import jenkins.model.*
import hudson.security.*
import jenkins.install.*

def instance = Jenkins.get()
def hudsonRealm = new HudsonPrivateSecurityRealm(false)
hudsonRealm.createAccount("admin", "devops2026!")
instance.setSecurityRealm(hudsonRealm)

def strategy = new FullControlOnceLoggedInAuthorizationStrategy()
strategy.setAllowAnonymousRead(false)
instance.setAuthorizationStrategy(strategy)

instance.setInstallState(InstallState.INITIAL_SETUP_COMPLETED)
instance.save()
```

결과: `SETUP_DONE` 출력, 이후 `admin`/`devops2026!`으로 정상 로그인 확인.

---

## 3. 플러그인 설치 — Pipeline·Git 기능 추가

설정 마법사를 건너뛰었기 때문에 플러그인이 하나도 없는 상태였다:

```bash
$ curl -s -u admin:devops2026! 'http://localhost:8081/pluginManager/api/json?depth=1' | python3 -c "..."
0 plugins installed
```

Job(Pipeline)을 만들려면 최소 `workflow-aggregator`(Pipeline 기능)와 `git`(Git 연동) 플러그인이 필요하다. Jenkins CLI로 설치:

```bash
$ curl -s -o jenkins-cli.jar http://localhost:8081/jnlpJars/jenkins-cli.jar
$ docker cp jenkins-cli.jar jenkins:/tmp/jenkins-cli.jar
$ docker exec jenkins java -jar /tmp/jenkins-cli.jar -s http://localhost:8080/ \
    -auth admin:devops2026! install-plugin workflow-aggregator git pipeline-stage-view
```

처음엔 `CLI handshake failed with status code 403 ... Jenkins URL is not configured` 에러가 났다 — Jenkins 내부의 "Jenkins URL" 전역 설정이 비어있으면 CLI 핸드셰이크 자체가 거부된다. Groovy로 URL을 채워주고 재시도:

```groovy
def loc = jenkins.model.JenkinsLocationConfiguration.get()
loc.setUrl('http://localhost:8080/')
loc.save()
```

이후 플러그인 설치 정상 진행 → 의존 플러그인까지 총 59개 자동 설치(`SuccessButRequiresRestart`) → `docker restart jenkins`로 재기동 후 확인:

```bash
$ curl -s -u admin:devops2026! 'http://localhost:8081/pluginManager/api/json?depth=1' | python3 -c "..."
59 plugins active
workflow-aggregator OK
git OK
pipeline-stage-view OK
```

---

## 4. Jenkinsfile 작성

`jenkins/Jenkinsfile.pf2` — GitHub Actions(`pf2-ci.yml`)의 lint→test→docker-build 3단계를 그대로 재현(전체 코드는 [`Jenkinsfile.pf2`](Jenkinsfile.pf2), 구조 설명은 `JENKINS_STUDY.md` 3장):

```groovy
pipeline {
    agent any
    environment {
        IMAGE_NAME = "pf2"
    }
    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/sungyoonjeong/devops-portfolio.git'
            }
        }
        stage('Lint') {
            steps {
                dir('PortFolio/PF2') {
                    sh 'docker run --rm --volumes-from jenkins -w $PWD golang:1.22-alpine gofmt -l .'
                    sh 'docker run --rm --volumes-from jenkins -w $PWD golang:1.22-alpine go vet ./...'
                }
            }
        }
        stage('Test') {
            steps {
                dir('PortFolio/PF2') {
                    sh 'docker run --rm --volumes-from jenkins -w $PWD golang:1.22-alpine go test -v ./...'
                }
            }
        }
        stage('Docker Build') {
            steps {
                dir('PortFolio/PF2') {
                    sh 'docker build -t $IMAGE_NAME:$(echo $GIT_COMMIT | cut -c1-7) .'
                }
            }
        }
    }
    post {
        always {
            echo "빌드 번호 #${env.BUILD_NUMBER} 종료 - 결과: ${currentBuild.currentResult}"
        }
    }
}
```

Job 생성은 config XML을 REST API로 직접 등록(`POST /createItem`) — "Pipeline script from SCM" 방식으로, 위 파일을 GitHub 레포의 `jenkins/Jenkinsfile.pf2` 경로에서 읽어오도록 지정했다.

---

## 5. 실전 디버깅 — 그린 뜨기까지 만난 버그 2개

### 버그 1 — sh 스텝 안의 중첩 따옴표가 깨짐

**최초 버전**(`sh -c "..."`를 Groovy 삼중따옴표 문자열 안에 이스케이프해서 넣음):
```groovy
sh '''
    docker run --rm -v "$PWD":/app -w /app golang:1.22-alpine \
        sh -c "test -z \\"\\$(gofmt -l .)\\" && go vet ./..."
'''
```

**증상**:
```
+ docker run ... golang:1.22-alpine sh -c test -z "$(gofmt -l .)" && go vet ./..."
pattern ./...: directory prefix . does not contain main module or its selected dependencies
```

로그를 보면 `sh -c`의 인자가 `test`에서 끊겨버렸다 — 그 뒤(`-z "$(gofmt -l .)" && go vet ./..."`)가 컨테이너 **밖**(Jenkins 에이전트 셸)에서 실행되면서, 컨테이너 안이 아니라 Jenkins 워크스페이스 경로에서 `go vet`이 돌아 엉뚱한 에러가 났다.

**수정**: 중첩 따옴표 자체를 없애는 방향으로 재설계 — `sh -c "..."`로 감싸지 않고, `docker run` 한 줄 = `sh` 스텝 하나로 쪼갰다. CI/CD 실습(`cicd/CICD_PRACTICE.md`)에서 겪었던 "긴 텍스트/중첩 이스케이프는 최대한 피하고 단순한 형태로 쪼갠다"는 교훈을 여기서도 그대로 적용.

### 버그 2 — Docker-outside-of-Docker 경로 함정

**증상**(버그 1을 고친 뒤에도 재발):
```
+ docker run --rm -v /var/jenkins_home/workspace/pf2-pipeline/PortFolio/PF2:/app -w /app golang:1.22-alpine go vet ./...
pattern ./...: directory prefix . does not contain main module or its selected dependencies
```
이번엔 명령 자체는 멀쩡한데 여전히 "모듈이 없다"고 나왔다. `gofmt -l .`은 에러 없이 조용히 "성공"했는데, 이것도 사실은 거짓 성공이었다(대상 디렉토리가 비어 있으면 gofmt은 그냥 아무 파일도 없다고 판단해 조용히 종료한다).

**원인**: `JENKINS_STUDY.md` 5장에서 정리한 Docker-outside-of-Docker 문제. Jenkins 컨테이너 안에서 `-v $PWD:/app`을 쓰면, 그 경로를 실제로 해석하는 건 **호스트의 Docker 데몬**인데 `$PWD`는 Jenkins **컨테이너 내부** 경로(`/var/jenkins_home/...`)라 호스트에는 그런 경로가 없다 — Docker가 에러 없이 빈 디렉토리를 새로 만들어 마운트해버린 것.

**수정**: 경로 기반 마운트(`-v host경로:/app`) 대신 **`--volumes-from jenkins`**로 Jenkins 컨테이너의 볼륨을 그대로 공유:
```groovy
sh 'docker run --rm --volumes-from jenkins -w $PWD golang:1.22-alpine go vet ./...'
```
`--volumes-from`은 경로를 다시 해석하지 않고 "이 컨테이너가 마운트한 볼륨을 그대로 가져다 써라"는 뜻이라, 양쪽 컨테이너에서 내부 경로가 완전히 일치한다.

---

## 6. 최종 검증 — 그린 확인

```bash
$ curl -s -u admin:devops2026! -X POST 'http://localhost:8081/job/pf2-pipeline/build'
# → 201 Created

$ curl -s -u admin:devops2026! 'http://localhost:8081/job/pf2-pipeline/lastBuild/api/json'
build # 3
result: SUCCESS
duration(ms): 49663
```

콘솔 로그로 각 단계가 실제로 통과했는지 확인:

```
+ docker run --rm --volumes-from jenkins -w .../PF2 golang:1.22-alpine gofmt -l .
+ docker run --rm --volumes-from jenkins -w .../PF2 golang:1.22-alpine go vet ./...
go: downloading github.com/prometheus/client_golang v1.20.5   # 이제 진짜로 go.mod를 찾아 의존성 해석
...
=== RUN   TestHealthHandler
--- PASS: TestHealthHandler (0.00s)
=== RUN   TestMetricsHandler
--- PASS: TestMetricsHandler (0.00s)
PASS
ok  	pf2	0.008s
+ docker build -t pf2:8de391d .
...
Finished: SUCCESS
```

빌드된 이미지도 실제로 호스트에 남아있는 것 확인:

```bash
$ docker images | grep pf2
pf2:8de391d   ba7e538d75c1   18.7MB
```

`8de391d`는 Jenkinsfile을 수정한 그 커밋의 짧은 해시 — GitHub Actions의 `deploy.sh`/`pf2-ci.yml`과 동일한 "커밋 해시 = 이미지 태그" 규칙이 Jenkins 파이프라인에서도 그대로 재현됐다(단, 이번엔 `git rev-parse` 대신 Jenkins가 checkout 시점에 자동으로 채워주는 `GIT_COMMIT` 환경변수를 셸에서 잘라 썼다).

---

## 7. GitHub Actions와 비교 — 실제로 만들어보고 느낀 차이

| | GitHub Actions(`pf2-ci.yml`) | Jenkins(`Jenkinsfile.pf2`) |
|---|---|---|
| 설치 | 불필요(GitHub가 관리) | 직접 설치 + 플러그인까지 수동 구성 |
| 첫 Job 만들기까지 | 워크플로 파일 커밋하면 끝 | 플러그인 설치 → 계정 설정 → Job 생성, 여러 단계 |
| 문법 | YAML | Groovy 기반 DSL(Declarative) |
| 컨테이너 안에서 컨테이너 쓰기 | 신경 쓸 필요 없음(러너가 매번 새 VM) | DooD 함정을 직접 알아야 함(오늘 겪은 것) |
| 커밋 해시 접근 | `git rev-parse --short HEAD` 직접 실행 | `env.GIT_COMMIT` 자동 제공(checkout이 채워줌) |
| 확장성 | GitHub Marketplace 액션 재사용 | 플러그인 생태계(더 오래되고 큼) |

결론적으로 두 도구는 **개념(순차 실행 job/stage, steps, 환경변수, 트리거)이 거의 1:1로 대응**돼서, GitHub Actions를 먼저 익혀둔 게 Jenkins를 처음 만져볼 때도 그대로 도움이 됐다 — "무엇을 배워야 하는지"보다 "이 회사는 어느 걸 쓰는지"가 실무에서 더 중요한 질문이라는 걸 체감했다.
