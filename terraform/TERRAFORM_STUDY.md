# Terraform 완전 정복 — 5일 커리큘럼

> 목표: AWS + LocalStack 기반 IaC 실습 → PF-IaC 포트폴리오 완성  
> 기간: 6/23(D1) ~ 6/27(D5)

> **이 문서를 처음 보는 사람을 위한 안내**  
> Terraform을 처음 배운다면 1장 → 2장 순서로 천천히 읽어라. 이 두 장이 "Terraform이 도대체 뭘 하는 물건인가"의 그림을 그려주는 개념서 파트다. 각 개념마다 **비유**를 먼저 붙여뒀으니, 코드보다 비유를 먼저 머리에 넣고 코드를 보면 훨씬 쉽다.  
> 3장(문법)부터는 사전처럼 필요할 때 찾아 쓰면 된다. 4~5장은 직접 손으로 따라 하는 실습이다.  
> ※ 코드에 나오는 AWS 용어(VPC·서브넷·CIDR·IGW·보안그룹·IAM 등)는 **바로 아래 "AWS 기본 용어 빠른 사전"**에 전부 풀어 뒀다. 모르는 용어가 나오면 그 사전부터 보면 된다 — 이 문서 하나로 막힘없이 읽히게 하는 게 목표다.

---

## 목차

0. [AWS 기본 용어 빠른 사전](#0-aws-기본-용어-빠른-사전) — 코드에 나오는 AWS 용어 총정리
1. [Terraform이란?](#1-terraform이란) — IaC 문제·내부 아키텍처·도구 비교
2. [핵심 개념](#2-핵심-개념) — Provider·Resource·State·Graph·실행 사이클
3. [HCL 문법 완전 정리](#3-hcl-문법-완전-정리)
4. [Terraform 워크플로우 명령어](#4-terraform-워크플로우-명령어)
5. [LocalStack 환경 설정](#5-localstack-환경-설정-d1)
6. [Variables · Outputs · Locals](#6-variables--outputs--locals-d2)
7. [Data Sources](#7-data-sources)
8. [Modules](#8-modules-d2)
9. [State 관리](#9-state-관리-d3)
10. [Workspace](#10-workspace-d3)
11. [AWS Provider 심화 패턴](#11-aws-provider-심화-패턴-d4)
12. [면접 Q&A](#12-면접-qa)
13. [일차별 자가 점검 (D1~D5)](#13-일차별-자가-점검-d1d5)
14. [베스트 프랙티스 & 안티패턴 & 보안](#14-베스트-프랙티스--안티패턴--보안)
15. [Terraform 치트시트](#15-terraform-치트시트-면접-전날실습-중-빠른-참조)
16. [용어집 (Glossary)](#16-용어집-glossary)

---

## 0. AWS 기본 용어 빠른 사전

> 이 문서의 Terraform 코드에 등장하는 AWS 용어를 한곳에 모았다. Terraform을 배우려면 결국 "무엇을" 만드는지(AWS 리소스)를 알아야 하므로, 먼저 이 그림을 머리에 넣고 가자. **비유 하나로 전체를 잡으면**: AWS에 인프라를 짓는 건 *땅 사서 건물 올리는 것*과 같다.

### 0.1 네트워크 — "땅과 도로"

```
용어               한 줄 정의                                  비유
─────────────────  ─────────────────────────────────────────  ────────────────────────
Region             AWS 데이터센터가 모인 지역(서울=ap-northeast-2) 도시
AZ (가용영역)       한 Region 안의 물리적으로 분리된 데이터센터    도시 안의 구(區)
                   (장애 대비로 여러 AZ에 분산 배치)
VPC                내 전용 가상 네트워크. 모든 리소스의 울타리     내가 분양받은 땅 전체
CIDR               IP 주소 범위 표기법 (10.0.0.0/16)             땅의 번지 체계
Subnet             VPC를 잘게 나눈 구역 (10.0.1.0/24)            땅 안의 구획(필지)
  - Public Subnet  인터넷과 직접 통하는 구역 (웹서버 배치)         대로변 상가 자리
  - Private Subnet 인터넷에서 직접 못 닿는 구역 (DB 배치)          건물 안쪽 금고방
IGW (인터넷 게이트웨이) VPC를 인터넷에 연결하는 출입구              땅의 정문
Route Table        "이 목적지는 이 길로" 라우팅 규칙표             도로 표지판
NAT Gateway        프라이빗 구역이 밖으로만 나가게 해주는 통로      안에서 밖으로만 여는 쪽문
                   (DB가 업데이트는 받되 외부 침입은 막음)
EIP                고정 공인 IP 주소                              안 바뀌는 대표 전화번호
```

**CIDR 빠르게 읽는 법** (자주 막히는 부분):
```
10.0.0.0/16  → 앞 16비트 고정 → 10.0.x.x 전부 → 약 6.5만 개 IP (VPC 크기로 흔함)
10.0.1.0/24  → 앞 24비트 고정 → 10.0.1.x 전부 → 256개 IP (Subnet 크기로 흔함)
0.0.0.0/0    → 0비트 고정 → "모든 IP" → 보통 "전 세계 어디서나"(인터넷)를 뜻함
숫자(/뒤)가 클수록 고정 비트가 많아 → 범위는 좁아진다.
```

### 0.2 컴퓨팅·스토리지 — "건물과 창고"

```
용어            한 줄 정의                                    비유
──────────────  ───────────────────────────────────────────  ────────────────────────
EC2             가상 서버 1대 (CPU·메모리를 빌려 쓰는 컴퓨터)   임대한 사무실 건물
instance_type   EC2의 사양 등급 (t3.micro=소형, t3.large=대형)  건물 평수·등급
AMI             EC2를 찍어내는 OS 이미지 틀 (Amazon Linux 등)   건물 설계 도면
EBS / root_block_device  EC2에 붙는 디스크(저장장치)            건물에 딸린 창고
S3              파일 저장소. 버킷(bucket) 단위로 담음            무한 용량 물품 보관함
  - bucket      S3의 최상위 저장 단위 (이름이 전 세계 유일해야)  보관함 한 칸
RDS             관리형 관계형 DB (MySQL·PostgreSQL 등)          관리인이 딸린 도서관
DynamoDB        관리형 NoSQL DB (Terraform state 락에도 쓰임)   빠른 색인 메모장
```

### 0.3 보안·접근 — "열쇠와 경비"

```
용어                 한 줄 정의                                  비유
───────────────────  ─────────────────────────────────────────  ──────────────────────
Security Group (SG)  리소스 단위 방화벽. 들어오고(ingress)         건물 입구 경비원
                     나가는(egress) 트래픽을 포트별로 허용/차단     (누구를 들일지 명단 관리)
IAM                  AWS 권한 관리 시스템(누가 무엇을 할 수 있나)   회사 출입·권한 체계
  - IAM Role         "역할". 사람이 아닌 서비스(EC2 등)가          임시 출입증
                     일시적으로 빌려 쓰는 권한 묶음
  - IAM Policy       권한 내용 자체 (S3 읽기 허용 등)             출입증에 적힌 허용 목록
  - AssumeRole       Role을 빌려 쓰는 행위                        출입증을 발급받음
  - Instance Profile EC2에 IAM Role을 붙이는 연결 고리            건물에 출입증을 비치
ALB / 로드밸런서      들어온 요청을 여러 서버에 분배                 손님을 빈 창구로 안내
```

### 0.4 자주 보는 식별자

```
ARN   AWS 리소스의 전 세계 유일 주소. 예: arn:aws:s3:::my-bucket
      → IAM 정책에서 "어떤 리소스에 권한을 줄지" 가리킬 때 씀. (도로명 전체 주소라고 보면 됨)
ID    리소스 생성 후 AWS가 부여하는 고유 번호. 예: vpc-0a1b2c3d, i-0f9e8d7c
      → Terraform에서 aws_vpc.main.id 처럼 참조하면 이 값이 들어감.
```

> **이 사전과 Terraform의 관계**: Terraform 코드의 `resource "aws_vpc"`, `resource "aws_subnet"`, `resource "aws_security_group"`... 은 전부 위 용어 하나하나를 코드로 만드는 것이다. 즉 **AWS 용어를 알아야 Terraform 코드가 "무엇을 만드는 문장인지"가 보인다.** 8장·11장 실습 코드를 볼 때 이 사전을 옆에 두고 대조하면 막힘이 없다.

---

## 1. Terraform이란?

HashiCorp가 만든 오픈소스 IaC(Infrastructure as Code) 도구.  
AWS, Azure, GCP, Kubernetes 등 4000개 이상의 Provider를 지원한다(공식 Registry 기준).  
한 줄 정의: **"원하는 인프라 상태를 코드로 선언하면, Terraform이 현재 상태와 비교해 그 차이만큼만 실제 인프라를 만들고·바꾸고·지워주는 도구."**

### 1.1 IaC가 실제로 푸는 문제

IaC는 단순히 "콘솔 대신 코드"가 아니다. 운영에서 반복적으로 사람을 괴롭히는 세 가지 고질병을 푼다.

```
① 스노우플레이크 서버 (Snowflake Server)
   손으로 설정한 서버는 눈송이처럼 전부 제각각이 됨.
   "이 서버는 왜 되고 저 서버는 왜 안 되지?" → 아무도 모름(설정 이력이 사람 머릿속에만 있음).
   IaC: 모든 서버가 동일 코드에서 나오므로 완전히 동일하게 재현됨.

② 구성 드리프트 (Configuration Drift)
   누군가 콘솔에서 급하게 보안그룹 포트 하나 열어둠 → 코드와 실제가 어긋남.
   다음 배포 때 터지거나, 보안 구멍이 방치됨.
   IaC: plan으로 "코드 vs 실제" 차이를 항상 감지 가능(드리프트 탐지).

③ 재현성·속도
   장애로 리전 전체가 날아가면 콘솔 클릭으로 수십 개 리소스를 다시? → 몇 시간~며칠.
   IaC: terraform apply 한 번 → 동일 인프라 수 분 내 재구성(재해 복구 DR).
```

### 1.2 AWS 콘솔 클릭 vs Terraform

```
구분            AWS 콘솔 클릭          Terraform
────────────    ───────────────────    ─────────────────────────────
재현성          불가능(매번 수작업)    코드 그대로 재실행 → 동일 결과
협업            화면 공유로 설명       git PR로 코드 리뷰 + 변경 이력
변경 전 확인    없음(누르면 즉시)      plan으로 사전 미리보기
환경 분리       dev/prod 일일이 반복   workspace/tfvars로 분리
변경 이력       CloudTrail 로그만      git blame으로 "누가·왜" 추적
삭제 안전성     의존성 수동 파악       의존성 역순으로 자동 삭제
```

### 1.3 선언형(Declarative) vs 명령형(Imperative)

```
명령형 (Bash 스크립트, 절차를 적음)
  "EC2 API 호출해 → 완료될 때까지 기다려 → 보안그룹 만들어 → 연결해 → 에러나면 재시도해"
  문제: 두 번째 실행하면? 이미 있는데 또 만들려다 에러. 멱등(idempotent)하지 않음.

선언형 (Terraform, 결과를 적음)
  "EC2 1대 + 보안그룹 1개가 이런 상태로 존재해야 해"
  → Terraform이 현재 상태를 조회하고, 부족하면 만들고, 이미 맞으면 아무것도 안 함.
  → 몇 번을 실행해도 결과가 같음(멱등성). 이게 IaC의 핵심 성질.
```

> **멱등성(Idempotency)**: 같은 연산을 여러 번 해도 결과가 한 번 한 것과 같은 성질. Terraform apply를 100번 돌려도 인프라는 코드가 선언한 상태 1개로 수렴한다. 명령형 스크립트가 흉내 내기 가장 어려운 부분이고, 선언형 도구의 존재 이유다.

### 1.4 Terraform 내부 아키텍처 — Core와 Provider

면접에서 "Terraform이 어떻게 AWS를 제어하나요?"라고 물으면 이 구조를 말할 수 있어야 한다.

**먼저 한 문장 비유:** Terraform은 "지시를 내리는 본사(Core)"와 "현장에서 AWS와 직접 일하는 통역 직원(Provider)"으로 나뉜다. 본사는 AWS 언어를 모르고 계획만 세우며, 실제 일 처리는 통역 직원이 한다. 아래 그림이 그 흐름이다.

```
┌─────────────────────────────────────────────────────────────┐
│                    당신이 작성한 코드                          │
│              main.tf · variables.tf · ...                     │
└───────────────────────────┬─────────────────────────────────┘
                            │ 읽음
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Terraform CORE (terraform 바이너리, Go)       │
│   - HCL 파싱 → 리소스 의존성 그래프(DAG) 구성                  │
│   - state(현재) vs config(원함) 비교 → 실행 계획 산출          │
│   - 그래프 순서대로 Provider에 "이거 만들어/지워" 명령         │
└───────────────────────────┬─────────────────────────────────┘
                            │ gRPC (로컬 프로세스 간 통신)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         PROVIDER 플러그인 (예: terraform-provider-aws)         │
│   - Core의 추상 명령을 실제 AWS API 호출로 번역                │
│   - "aws_instance 생성" → ec2:RunInstances API 호출           │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTPS (AWS SDK)
                            ▼
                    실제 AWS (또는 LocalStack)
```

> 그림 속 두 용어 풀이: **gRPC**는 한 컴퓨터 안에서 두 프로그램(Core ↔ Provider)이 빠르게 대화하는 통신 방식이라고만 알면 충분하다. **AWS SDK**는 Provider가 실제 AWS에 HTTPS로 API를 보낼 때 쓰는 도구다.

핵심 포인트 세 가지:
- **Core는 AWS를 모른다.** Core는 그래프 계산과 상태 조정만 담당하는 범용 엔진이다. AWS API 지식은 전부 Provider에 들어있다. 그래서 Azure로 옮기면 Provider만 갈아끼우면 된다.
- **Provider는 별도 프로세스다.** `terraform init` 시 다운로드되어 `.terraform/providers/`에 깔리고, 실행 시 Core가 이 플러그인을 gRPC로 띄워 통신한다. 그래서 `init` 없이는 아무것도 못 한다.
- **이 분리 덕에 4000개 Provider가 가능하다.** AWS·GCP·Cloudflare·Datadog·GitHub까지 전부 Provider 플러그인. Terraform 하나로 멀티클라우드를 단일 코드베이스에서 관리하는 근거가 여기 있다.

### 1.5 다른 도구와의 비교 (면접 단골)

```
도구              범주              언어        상태관리      특징
──────────────    ──────────────    ────────    ──────────    ─────────────────────────
Terraform         프로비저닝(IaC)   HCL(선언형) tfstate 직접  멀티클라우드, 사실상 표준
CloudFormation    프로비저닝(IaC)   YAML/JSON   AWS가 관리     AWS 전용, 깊은 통합
Pulumi            프로비저닝(IaC)   범용언어     자체 백엔드    TS/Python/Go로 작성
AWS CDK           프로비저닝(IaC)   범용언어     CFN으로 변환   CFN을 코드로 생성
Ansible           구성관리(CM)      YAML        무상태        서버 내부 설정·앱 배포에 강함
```

핵심 구분:
- **프로비저닝(Provisioning) vs 구성관리(Configuration Management)**: Terraform은 "인프라를 만드는" 쪽(VPC·EC2·RDS 생성). Ansible은 "만들어진 서버 안을 설정하는" 쪽(패키지 설치·파일 배포). **둘은 경쟁이 아니라 보완** — PF-IaC에서 Terraform으로 EC2를 띄우고 Ansible로 그 안에 Docker를 설치하는 조합이 정석이다.
- **Terraform vs CloudFormation**: CFN은 AWS 전용·상태를 AWS가 자동 관리(tfstate 걱정 없음)·신규 AWS 서비스 즉시 지원. Terraform은 멀티클라우드·HCL이 더 읽기 쉬움·생태계가 훨씬 큼. 실무에서는 멀티클라우드/큰 생태계 때문에 Terraform이 사실상 표준.

### 1.6 Terraform이 안 맞는 경우 (한계도 알아야 한다)

도구를 맹신하지 않는 태도가 면접에서 신뢰를 준다.

```
- 서버 내부의 세밀한 설정·앱 배포   → Ansible/Chef가 적합 (Terraform은 user_data 정도만)
- 컨테이너 오케스트레이션의 런타임   → K8s 자체 기능 (Terraform은 클러스터 생성까지)
- tfstate 관리 부담                  → 상태 파일 분실·충돌·민감정보 노출 리스크 상존
- 빠른 일회성 실험                   → 콘솔 클릭이 더 빠를 수 있음
- Provider가 신규 기능 미지원        → AWS 새 서비스는 CFN보다 늦게 반영되기도
```

---

## 2. 핵심 개념

### ① Provider — "AWS와 대화하는 통역사"

**비유:** 당신(Terraform)은 한국어로 "S3 버킷 하나 만들어줘"라고 말한다. 그런데 AWS는 자기들만의 API 언어(REST 호출)만 알아듣는다. 이 사이에서 통역해주는 직원이 **Provider**다. AWS 담당 통역사(`hashicorp/aws`), Azure 담당 통역사(`azurerm`)가 따로 있고, 상대가 바뀌면 통역사만 바꾸면 된다.

**정의:** Terraform Core와 클라우드 API 사이를 잇는 플러그인. Terraform 자체에는 AWS 지식이 없고, 그 지식은 전부 Provider에 들어있다. `terraform init`을 실행하면 이 통역사를 인터넷에서 내려받아 `.terraform/` 폴더에 둔다(그래서 init 없이는 아무것도 못 한다).

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"  # 어떤 통역사를 쓸지
      version = "~> 5.0"         # 버전 5.x 중 최신 (5.0 이상 6.0 미만)
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"      # 통역사에게 줄 기본 설정 (서울 리전)
}
```

### ② Resource — "만들고 싶은 것 한 줄 = 주문서 한 줄"

**비유:** 식당 주문서에 "김치찌개 1" 한 줄을 쓰는 것과 같다. `resource` 블록 하나 = 실제로 만들어질 인프라 한 덩어리(S3 버킷 하나, EC2 한 대). Terraform IaC의 가장 기본 단위이자, 당신이 코드에서 가장 많이 쓰게 될 블록이다.

```hcl
resource "aws_s3_bucket" "logs" {    # ← 이 줄에 이름이 두 개 등장한다
  bucket = "my-logs-bucket"          # 실제 AWS에 붙을 버킷 이름
}
```

이름이 두 개라 헷갈리는데, 역할이 완전히 다르다:
- 첫 번째 `"aws_s3_bucket"` = **리소스 타입**. "무엇을 만들지"를 Provider가 정해둔 종류 이름. 내 맘대로 못 바꾼다.
- 두 번째 `"logs"` = **내가 붙이는 별명**. 코드 안에서만 쓰는 식별자. 다른 곳에서 `aws_s3_bucket.logs.id`처럼 이 별명으로 이 리소스를 가리킨다. 실제 AWS에 보이는 이름(`bucket = ...`)과는 무관하다.

> 비유로: `"aws_s3_bucket"`은 "자동차"라는 차종, `"logs"`는 내가 내 차에 붙인 애칭("흰둥이"). 도로(AWS)에 등록되는 번호판은 또 다른 값(`bucket`).

### ③ State — "Terraform의 가계부(세이브 파일)"

**비유:** 게임의 세이브 파일을 떠올려라. Terraform은 자기가 뭘 만들었는지 기억하려고 `terraform.tfstate`라는 파일에 "나는 이 버킷을, 이 ID로, 이 설정으로 만들었다"를 전부 적어둔다. 이 파일이 없으면 Terraform은 기억상실에 걸려서, 이미 만든 걸 또 만들려 하거나 뭘 지워야 할지 모른다.

```
┌──────────────┐          ┌──────────────┐
│  코드(원함)  │  apply   │  실제 AWS   │
│  main.tf     │ ──────▶  │  리소스들   │
└──────────────┘          └──────────────┘
       ↑                         ↑
       │   terraform.tfstate     │
       └─────── (둘을 매핑) ─────┘
   "코드의 logs 별명" = "실제 AWS의 버킷 ID" 라는 연결표

plan 실행 = 코드(원함) 와 tfstate(현재 가진 것) 를 비교 → 차이만 변경
```

왜 중요한가: Terraform이 "새로 만들지 / 고칠지 / 지울지"를 판단하는 모든 근거가 이 파일이다. 그래서 ⑥ 실행 사이클을 이해하려면 State 개념이 먼저 잡혀야 한다. (이 파일엔 비밀번호 등 민감정보가 평문으로 들어가서 git에 올리면 안 된다 — 9장 참조.)

### ④ Plan / Apply 사이클 — "결제 전 영수증 미리보기"

**비유:** 온라인 쇼핑에서 '결제하기'를 누르기 전에 주문 요약 화면을 한 번 보여주는 것과 같다. `plan`이 그 미리보기 화면이고, `apply`가 실제 결제다. 미리보기를 안 보고 결제하면 엉뚱한 게 배송되듯, plan을 안 읽고 apply하면 운영 리소스가 날아갈 수 있다. **그래서 plan 출력을 읽는 습관이 Terraform 실력의 절반이다.**

```
코드 작성
    ↓
terraform plan    ← 무엇이 바뀔지 미리보기 (실제 AWS는 아직 안 건드림)
    ↓
terraform apply   ← 미리본 그대로 실제 적용
    ↓
terraform destroy ← 만든 것 전부 삭제 (실습 후 비용 방지)
```

> plan은 "구경만", apply는 "실행", destroy는 "되돌리기". 학습 단계에서는 `apply`로 만들어보고 반드시 `destroy`로 지우는 사이클을 반복하면 비용 걱정 없이 연습할 수 있다.

### ⑤ Dependency Graph (의존관계 자동 해결) — "순서는 Terraform이 알아서"

**비유:** 집을 지을 때 기초 → 벽 → 지붕 순서가 정해져 있듯, VPC가 있어야 그 안에 서브넷을 넣을 수 있다. 놀랍게도 이 순서를 당신이 지정할 필요가 없다. Terraform이 코드의 참조 관계를 읽고 "아, VPC가 먼저구나"를 스스로 알아낸다.

내부적으로 Terraform은 코드를 읽어 **방향성 비순환 그래프(DAG)** — 쉽게 말해 "A 다음 B, B 다음 C" 같은 화살표 지도 — 를 그리고, 그 순서대로 리소스를 처리한다. 서로 관계없는 리소스들은 동시에(병렬로, 기본 10개씩) 만들어 속도를 높인다.

> DAG = Directed(방향 있는) Acyclic(빙빙 도는 고리가 없는) Graph. "A→B→C는 되지만 A→B→A처럼 되돌아오는 순환은 안 된다"는 뜻. 만약 두 리소스가 서로를 참조하면(순환) Terraform은 에러를 낸다.

**암묵적 의존성 (Implicit) — 권장**

한 리소스가 다른 리소스의 속성을 참조하면, Terraform이 자동으로 "먼저 만들어야 함"을 추론한다.

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "pub" {
  vpc_id     = aws_vpc.main.id   # ← 이 참조 한 줄로 "vpc 먼저" 자동 추론
  cidr_block = "10.0.1.0/24"
}
# 삭제 시에는 역순: subnet 먼저 삭제 → vpc 삭제 (의존성 역방향)
```

**명시적 의존성 (Explicit) — depends_on**

코드상 참조는 없지만 실제로는 순서가 필요한 경우에만 사용한다. 예를 들어 IAM 정책이 적용되기 전에 EC2가 S3에 접근하면 권한 에러가 나는데, 이 순서는 속성 참조로 드러나지 않는다.

```hcl
resource "aws_instance" "app" {
  # ... iam_role을 코드에서 직접 참조하지 않지만,
  #     role 정책이 먼저 붙어야 부팅 스크립트가 S3에 접근 가능
  depends_on = [aws_iam_role_policy.s3_access]
}
```

> **원칙: depends_on은 최후의 수단.** 가능하면 속성 참조(암묵적)로 의존성을 표현하라. depends_on을 남발하면 그래프가 과도하게 직렬화되어 병렬성이 떨어지고, "왜 이 순서지?"를 코드만 봐선 알기 어려워진다. 정말 참조로 표현 불가능한 숨은 순서에만 쓴다.

**그래프 시각화:**
```bash
terraform graph | dot -Tpng > graph.png   # graphviz 필요. 의존 관계를 그림으로 확인
```

### ⑥ 실행 사이클 — Terraform이 plan에서 실제로 비교하는 것

Terraform 이해의 핵심. `terraform apply`는 마법이 아니라 **세 가지 정보를 비교하는 조정(reconciliation) 과정**이다.

```
세 개의 상태가 존재한다:

  ① Configuration (코드)     ← 내가 .tf에 "원한다"고 적은 상태(desired)
  ② State (tfstate)          ← Terraform이 "마지막에 이렇게 만들었다"고 기록한 상태
  ③ Real World (실제 AWS)    ← 지금 이 순간 AWS에 진짜로 존재하는 상태(actual)
```

`terraform plan`이 돌 때 내부적으로 일어나는 일:

```
1단계 REFRESH   : 실제 AWS를 조회해서(③) tfstate(②)를 최신화
                  → 이 과정에서 "드리프트"가 드러난다
                    (예: 누가 콘솔에서 포트를 열어둠 → state엔 없는데 실제엔 있음)

2단계 PLAN(diff): 갱신된 state(②, =실제) 와 코드(①, =원함)를 비교
                  → 차이를 계산해 실행 계획 생성:
                     + create   코드엔 있는데 실제엔 없음     → 만든다
                     ~ update   둘 다 있는데 속성이 다름        → 고친다(in-place)
                     - destroy  실제엔 있는데 코드엔 없음       → 지운다
                    -/+ replace 바꿀 수 없는 속성이 변경됨      → 지우고 새로 만든다

3단계 APPLY     : 위 계획을 그래프 순서대로 Provider에 실행시키고,
                  성공한 결과를 tfstate(②)에 다시 기록
```

핵심 통찰 두 가지:
- **plan은 "코드 vs 실제(state)"를 비교한다.** state가 실제와 어긋나 있으면(드리프트) plan 결과도 어긋난다. 그래서 refresh가 plan 앞에 항상 붙는다.
- **"코드에서 리소스를 지우면 = 실제에서 삭제"다.** 코드에서 블록을 주석 처리하거나 지우면, plan은 "코드엔 없네 → 실제 리소스 destroy"로 해석한다. 초보가 가장 많이 당하는 사고. 리소스를 코드에서만 빼고 실제는 남기고 싶으면 `terraform state rm`(state에서만 제거)을 써야 한다.

**드리프트(Drift) 탐지·처리:**
```bash
terraform plan -refresh-only   # 실제와 state 차이만 확인(코드와 비교 X)
terraform apply -refresh-only   # 드리프트를 state에 반영(코드는 안 건드림)
# 반대로, 콘솔에서 손댄 걸 코드 기준으로 되돌리려면 그냥 terraform apply
#   → 코드(원함)에 맞춰 실제를 강제로 복원 = IaC가 드리프트를 자가 치유하는 원리
```

---

## 3. HCL 문법 완전 정리

### 3.1 기본 타입

```hcl
# string
name = "my-resource"

# number
port = 8080

# bool
enabled = true

# list(string)
azs = ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"]

# map(string)
tags = {
  Env   = "dev"
  Owner = "jsy"
}

# object (혼합 타입)
config = {
  size    = "t3.micro"
  enabled = true
}
```

### 3.2 문자열 보간(Interpolation)

```hcl
# ${} 안에 표현식
bucket = "logs-${var.env}-${var.project}"
name   = "web-${count.index}"

# 멀티라인 (heredoc)
policy = <<-EOT
  {
    "Version": "2012-10-17",
    "Statement": []
  }
EOT
```

### 3.3 조건식과 for

```hcl
# 삼항 연산자
instance_type = var.env == "prod" ? "t3.large" : "t3.micro"

# for 표현식 → list 생성
cidr_blocks = [for i in range(3) : "10.0.${i}.0/24"]
# 결과: ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]

# for 표현식 → map 생성
upper_tags = { for k, v in var.tags : k => upper(v) }

# count: 같은 리소스 여러 개
resource "aws_s3_bucket" "buckets" {
  count  = 3
  bucket = "bucket-${count.index}"   # bucket-0, bucket-1, bucket-2
}

# for_each: map/set 기반 (이름으로 참조 가능 → count보다 권장)
resource "aws_s3_bucket" "env_buckets" {
  for_each = toset(["dev", "stg", "prod"])
  bucket   = "myapp-${each.key}"
}
```

### 3.4 참조 문법

```hcl
# 다른 resource 속성 참조
vpc_id    = aws_vpc.main.id
subnet_id = aws_subnet.public[0].id              # count 사용 시 인덱스
bucket    = aws_s3_bucket.env_buckets["dev"].id  # for_each 사용 시 키

# variable 참조
instance_type = var.instance_type

# local 참조
name = local.name_prefix

# data source 참조
ami = data.aws_ami.amazon_linux.id

# module output 참조
subnet_id = module.vpc.public_subnet_ids[0]
```

### 3.5 자주 쓰는 내장 함수

```hcl
# 문자열
lower("HELLO")              # "hello"
upper("hello")              # "HELLO"
format("%s-%s", "a", "b")  # "a-b"
join("-", ["a","b","c"])    # "a-b-c"
split(",", "a,b,c")         # ["a","b","c"]
replace("foo-bar","bar","baz") # "foo-baz"
trimspace("  hello  ")      # "hello"

# 컬렉션
length(["a","b","c"])       # 3
toset(["a","b","a"])        # {"a","b"} (중복 제거)
merge({a=1},{b=2})          # {a=1, b=2}
flatten([["a"],["b","c"]])  # ["a","b","c"]
concat(["a"],["b"])         # ["a","b"]
keys({a=1,b=2})             # ["a","b"]
values({a=1,b=2})           # [1,2]

# CIDR
cidrsubnet("10.0.0.0/16", 8, 0)  # "10.0.0.0/24"
cidrsubnet("10.0.0.0/16", 8, 1)  # "10.0.1.0/24"

# 인코딩
jsonencode({key = "val"})   # '{"key":"val"}'
base64encode("hello")

# 안전한 조회 / 기본값
lookup({a=1}, "b", 0)       # 0  (키 없으면 기본값)
try(var.maybe.value, "x")   # 에러 나면 "x" 반환(옵셔널 접근에 유용)
coalesce(null, "", "first") # "first"  (첫 번째 non-null/non-empty)
```

### 3.6 타입 제약 (Type Constraints)

변수 타입을 정밀하게 강제하면 잘못된 입력을 plan 단계에서 막을 수 있다.

```hcl
variable "subnet" {
  type = object({
    cidr   = string
    az     = string
    public = bool
    tags   = optional(map(string), {})   # optional: 생략 가능 + 기본값
  })
}

variable "instances" {
  # 객체들의 맵 — for_each와 함께 쓰는 실무 패턴
  type = map(object({
    instance_type = string
    disk_size     = number
  }))
  default = {
    web = { instance_type = "t3.micro", disk_size = 20 }
    db  = { instance_type = "t3.small", disk_size = 50 }
  }
}
```

> `any`도 가능하지만 타입 안전성을 잃으므로 최후의 수단. 가능한 한 구체 타입을 적는다.

### 3.7 조건부 리소스 생성 (count 트릭)

`count`에 0 또는 1을 넣어 "리소스를 만들지 말지"를 조건으로 제어한다.

```hcl
variable "create_nat" {
  type    = bool
  default = false
}

resource "aws_nat_gateway" "this" {
  count         = var.create_nat ? 1 : 0   # false면 0개 → 아예 안 만듦
  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public[0].id
}

# 참조 시 주의: count를 쓰면 리스트가 되므로 [0] 인덱스 필요
output "nat_ip" {
  value = var.create_nat ? aws_nat_gateway.this[0].public_ip : null
}
```

### 3.8 dynamic 블록 — 반복되는 중첩 블록 생성

Security Group의 ingress처럼 같은 중첩 블록을 여러 개 만들 때, 복붙 대신 데이터로 생성한다.

```hcl
variable "ingress_rules" {
  type = list(object({
    port        = number
    cidr_blocks = list(string)
  }))
  default = [
    { port = 80,  cidr_blocks = ["0.0.0.0/0"] },
    { port = 443, cidr_blocks = ["0.0.0.0/0"] },
    { port = 22,  cidr_blocks = ["10.0.0.0/16"] },
  ]
}

resource "aws_security_group" "web" {
  name = "web-sg"

  dynamic "ingress" {          # "ingress" 블록을 반복 생성
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = ingress.value.cidr_blocks
    }
  }
}
# 규칙을 추가/삭제하려면 변수 리스트만 수정 → 코드 본문은 그대로
```

### 3.9 Splat 표현식 & 중요한 표현식들

```hcl
# splat [*] : 리스트의 모든 요소에서 같은 속성 추출
aws_subnet.public[*].id          # [subnet-1, subnet-2, ...]
# = [for s in aws_subnet.public : s.id] 와 동일

# for_each 리소스에서 값만 모으기
values(aws_instance.app)[*].private_ip

# 조건 + for 필터링
[for s in var.subnets : s.cidr if s.public]   # public인 것만

# templatefile: 외부 템플릿 파일에 변수 주입 (user_data에 자주 씀)
user_data = templatefile("${path.module}/init.sh.tftpl", {
  app_port = var.app_port
  env      = var.env
})
```

### 3.10 메타인자 (Meta-arguments) 한눈에

**메타인자**는 리소스 타입과 무관하게 **거의 모든 resource/module 블록에 공통으로 쓸 수 있는 특수 인자**다. "이 리소스를 몇 개 만들지·언제 만들지·어떻게 교체할지"처럼 리소스 자체의 속성이 아니라 Terraform의 동작을 제어한다.

```
메타인자        역할                                         예시
─────────────   ──────────────────────────────────────────   ──────────────────────────
count           숫자만큼 복제 / 0이면 안 만듦                  count = 2  ·  count = var.on?1:0
for_each        map/set의 키마다 하나씩 (이름으로 식별)         for_each = toset(["a","b"])
depends_on      명시적 순서 강제 (참조로 안 드러날 때만)        depends_on = [aws_iam_role.r]
lifecycle       교체·삭제 동작 제어                            create_before_destroy = true
provider        멀티 리전 등에서 어떤 provider를 쓸지 지정       provider = aws.tokyo
```

> **count vs for_each 핵심 한 줄:** count는 "3번째"처럼 인덱스로 가리켜서, 중간 걸 지우면 뒤 인덱스가 밀려 엉뚱한 리소스가 재생성된다. for_each는 "dev라는 키"로 가리켜서 중간을 지워도 나머지가 안전하다. **리스트 원소가 추가·삭제될 수 있으면 for_each.**

---

## 4. Terraform 워크플로우 명령어

```bash
# 초기화 (provider 플러그인 다운로드)
terraform init

# 코드 자동 포맷팅 (커밋 전 항상 실행)
terraform fmt

# 문법 검사
terraform validate

# 변경사항 미리보기 (반드시 읽기!)
terraform plan

# 실제 적용
terraform apply
terraform apply -auto-approve    # 확인 프롬프트 생략

# 전체 삭제
terraform destroy
terraform destroy -auto-approve

# output 값 출력
terraform output
terraform output vpc_id

# state 관련
terraform show                               # state 전체 보기
terraform state list                         # 리소스 목록
terraform state show aws_s3_bucket.practice  # 특정 리소스 상세
terraform state mv old_name new_name         # 리소스 이름 변경 (코드 리팩토링 시)
terraform state rm aws_s3_bucket.old         # state에서만 제거 (실제 삭제 X)
terraform import aws_s3_bucket.b bucket-name # 기존 리소스를 state로 끌어오기
```

### plan 출력 읽는 법

```
+ 생성될 리소스
~ 수정될 리소스
- 삭제될 리소스
-/+ 삭제 후 재생성 (forces replacement ← 주의! 운영 중이면 다운타임)

예시:
# aws_s3_bucket.practice will be created
+ resource "aws_s3_bucket" "practice" {
    + bucket = "terraform-practice-bucket"
    + id     = (known after apply)          ← apply 후에 알 수 있는 값
  }

Plan: 1 to add, 0 to change, 0 to destroy.  ← 요약 줄 꼭 확인
```

### 실무 표준 흐름 — plan을 저장해서 apply

운영에서는 "검토한 그 계획"과 "실제 적용되는 계획"이 같아야 한다. plan을 파일로 저장하고 그 파일을 apply하면, 그 사이 코드/상태가 바뀌어도 저장된 계획만 적용된다.

```bash
terraform plan -out=tfplan      # 계획을 tfplan 파일로 저장
# (사람이 검토 / CI에서 승인)
terraform apply tfplan          # 저장된 계획 그대로 적용 (재계산 X, 프롬프트 X)
```

CI/CD 파이프라인 정석:
```
fmt -check → validate → plan -out=tfplan → (승인 게이트) → apply tfplan
```

### 알아두면 좋은 플래그

```bash
terraform plan -target=aws_instance.web   # 특정 리소스만 (응급용, 남용 금지)
terraform apply -replace=aws_instance.web  # 이 리소스만 강제 재생성(구 taint)
terraform plan -var-file=prod.tfvars       # 특정 변수 파일로
terraform fmt -check -recursive            # 포맷 안 맞으면 실패(CI 검사용)
terraform validate                         # 문법·참조 정합성 검사(클라우드 호출 X)
terraform output -json                     # output을 JSON으로(스크립트 연동)
terraform console                          # 표현식·함수 즉석 테스트 REPL
```

> `-target`과 `-replace`는 응급 처치다. 일상적으로 쓰면 "코드 = 인프라" 원칙이 깨진다. 평소엔 전체 plan/apply가 정석.

### 디버깅 — 뭔가 이상할 때

```bash
TF_LOG=DEBUG terraform apply        # 내부 동작·API 호출까지 상세 로그
TF_LOG=TRACE terraform plan         # 가장 자세한 단계 (provider 통신까지)
TF_LOG=DEBUG TF_LOG_PATH=tf.log terraform apply   # 로그를 파일로
terraform show                      # 현재 state를 사람이 읽기 좋게 출력
terraform state list                # 관리 중인 리소스 목록 (state 꼬임 진단)
terraform refresh                   # 실제와 state 동기화 (신버전은 apply -refresh-only 권장)
```
> 에러 메시지가 모호할 때 `TF_LOG=DEBUG`로 돌리면 "어느 API 호출에서 무슨 응답이 왔는지"가 보인다. LocalStack 미지원 기능 같은 문제를 찾을 때 특히 유용.

---

## 5. LocalStack 환경 설정 (D1)

### LocalStack 실행

```bash
# Docker로 실행 (포트폴리오에서는 이미 사용 경험 있음)
docker run --rm -d \
  -p 4566:4566 \
  --name localstack \
  localstack/localstack

# 실행 확인
curl http://localhost:4566/_localstack/health | python3 -m json.tool
```

### Provider 설정 — LocalStack용 핵심 설정

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true   # LocalStack 필수 — 없으면 DNS 에러 발생

  endpoints {
    s3       = "http://localhost:4566"
    ec2      = "http://localhost:4566"
    iam      = "http://localhost:4566"
    sts      = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
  }
}
# s3_use_path_style 이유:
# 기본(가상호스트): http://bucket-name.localhost:4566/ → DNS 못 찾아서 에러
# path-style 강제: http://localhost:4566/bucket-name  → LocalStack 정상 처리
```

### D1 실습: 첫 S3 버킷

```hcl
resource "aws_s3_bucket" "practice" {
  bucket = "terraform-practice-bucket"

  tags = {
    Name = "practice"
    Env  = "local"
  }
}

output "bucket_name" {
  description = "생성된 버킷 이름"
  value       = aws_s3_bucket.practice.bucket
}
```

```bash
terraform init      # 초기화
terraform fmt       # 포맷
terraform validate  # 검사
terraform plan      # 미리보기 (출력 읽기!)
terraform apply     # 적용

# 생성 확인
aws --endpoint-url=http://localhost:4566 s3 ls

terraform destroy   # 삭제 (사이클 완성)
```

### 5.1 terraform init이 실제로 한 일 (D1 복기)

`terraform init`을 친 순간 보이지 않는 곳에서 일어난 일:

```
1. main.tf의 required_providers 블록을 읽음 → "hashicorp/aws ~> 5.0 필요"
2. registry.terraform.io에서 5.0 제약을 만족하는 최신 버전(5.100.0) 선택
3. 그 Provider 바이너리(수백 MB)를 다운로드:
   .terraform/providers/registry.terraform.io/hashicorp/aws/5.100.0/linux_amd64/
4. .terraform.lock.hcl 생성 → 버전·해시 고정
```

**.terraform 디렉토리 구조 (실제):**
```
.terraform/
└── providers/
    └── registry.terraform.io/
        └── hashicorp/
            └── aws/
                └── 5.100.0/
                    └── linux_amd64/
                        └── terraform-provider-aws_v5.100.0_x5   ← Provider 실행 바이너리
```
→ 이래서 `.terraform/`은 절대 git에 안 올린다(용량 큼 + OS별 바이너리). 각자 `init`으로 받는다.

### 5.2 .terraform.lock.hcl — 버전 고정 파일

```hcl
provider "registry.terraform.io/hashicorp/aws" {
  version     = "5.100.0"        # 실제로 선택된 버전
  constraints = "~> 5.0"          # main.tf가 요구한 제약
  hashes = [ "h1:...", "zh:..." ] # 무결성 검증용 체크섬(공급망 보안)
}
```
- `~> 5.0`은 "5.x 중 최신"이라는 **범위**다. lock 파일은 그중 **실제로 고른 한 버전**(5.100.0)을 박제한다.
- 팀원이 `init`하면 lock의 5.100.0을 그대로 받음 → "내 PC에선 됐는데" 방지.
- `go.sum`·`package-lock.json`과 같은 역할. **반드시 git에 커밋**한다.
- 버전을 올리려면 `terraform init -upgrade`.

### 5.3 terraform.tfstate 들여다보기 (apply 후)

apply가 성공하면 Terraform이 만든 결과를 tfstate에 기록한다.

```json
{
  "version": 4,
  "resources": [{
    "type": "aws_s3_bucket",
    "name": "practice",
    "instances": [{
      "attributes": {
        "id": "terraform-practice-bucket",
        "bucket": "terraform-practice-bucket",
        "arn": "arn:aws:s3:::terraform-practice-bucket",
        "tags": { "Name": "practice", "Env": "local" }
      }
    }]
  }]
}
```
- `terraform.tfstate.backup`은 직전 상태의 백업이다. apply가 꼬였을 때 복구용.
- 다음 `plan` 때 Terraform은 이 tfstate를 읽고 "내가 이 버킷을 만들었지"를 기억한다. 그래서 또 apply해도 새로 안 만든다(멱등).

### 5.4 D1에서 직접 겪은 에러 — s3_use_path_style (심화)

증상: `terraform apply` 시 S3 버킷 생성에서 DNS 해석 실패 에러.

```
원인 (S3의 두 가지 URL 접근 방식):

  가상 호스트 스타일 (Virtual-hosted, AWS 기본):
    http://terraform-practice-bucket.localhost:4566/
    → 버킷명이 호스트명 앞에 붙음 → "버킷명.localhost"를 DNS가 못 찾음 → 실패

  경로 스타일 (Path-style):
    http://localhost:4566/terraform-practice-bucket
    → 버킷명이 경로에 들어감 → localhost만 찾으면 됨 → LocalStack 정상 처리

해결: provider 블록에 s3_use_path_style = true
  → AWS Provider가 경로 스타일로 요청을 보내도록 강제
```
> 실제 AWS에서는 가상 호스트 스타일이 표준이라 이 옵션이 필요 없다. **LocalStack·MinIO 같은 로컬 S3 호환 서비스에서만** 필요. 면접에서 "LocalStack 써봤다"고 하면 이 디테일을 물어볼 수 있으니 원리까지 말할 수 있게.

---

## 6. Variables · Outputs · Locals (D2)

이 셋은 코드를 "재사용 가능하게" 만드는 도구다. 한 문장 비유: **변수는 함수의 입력 매개변수, 출력은 함수의 return 값, local은 함수 안의 중간 계산 변수**다. 같은 코드를 dev/prod에서 값만 바꿔 돌리고 싶을 때 이걸 쓴다.

```
Input Variable  ← 외부에서 값을 받아옴 (dev/prod마다 다른 값)        "입력"
       ↓
   [ 리소스들 ]  ← 변수를 써서 인프라를 만듦
       ↓
Output Value    → 만든 결과 중 알려줄 값을 밖으로 내보냄 (VPC ID 등)  "출력"

Local Value     ↻ 코드 내부에서만 쓰는 중간 계산값 (이름 prefix 등)   "내부 메모"
```

### 6.1 Input Variables — 외부에서 주입받는 입력

하드코딩(`"10.0.0.0/16"`을 코드에 직접 박는 것)을 피하고, 값을 밖에서 받도록 구멍을 뚫어두는 것. 그러면 같은 코드로 dev는 작은 서버, prod는 큰 서버를 만들 수 있다. `variable` 블록의 주요 항목: `type`(타입), `default`(기본값, 없으면 필수 입력), `description`(설명), `validation`(잘못된 값 차단).

```hcl
# variables.tf
variable "env" {
  description = "배포 환경 (dev / stg / prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.env)
    error_message = "env는 dev, stg, prod 중 하나여야 합니다."
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_count" {
  type    = number
  default = 2
}

variable "enable_nat" {
  type    = bool
  default = false
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}
```

**값 입력 우선순위 (높을수록 우선)**

```
1. -var 플래그:          terraform apply -var="env=prod"
2. -var-file 지정:       terraform apply -var-file="prod.tfvars"
3. terraform.tfvars:     (자동 로드)
4. 환경변수:             TF_VAR_env=prod terraform apply
5. default 값:           variable 블록의 default
```

```hcl
# terraform.tfvars (자동 로드)
env          = "dev"
vpc_cidr     = "10.0.0.0/16"
subnet_count = 2

# prod.tfvars (수동 지정)
env          = "prod"
vpc_cidr     = "10.1.0.0/16"
subnet_count = 3
```

### 6.2 Output Values — 만든 결과를 밖으로 내보내기

apply가 끝나면 보통 "그래서 VPC ID가 뭔데? 서버 IP는?"이 궁금하다. output은 그걸 터미널에 찍어주고, 다른 모듈/스크립트가 가져다 쓸 수 있게 노출한다. 쓰는 이유 두 가지: ① 사람이 결과를 바로 확인 ② 모듈 간 값 전달(VPC 모듈이 만든 subnet ID를 EC2 모듈에 넘김).

```hcl
# outputs.tf
output "vpc_id" {
  description = "생성된 VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "퍼블릭 서브넷 ID 목록"
  value       = aws_subnet.public[*].id
}

output "db_password" {
  value     = var.db_password
  sensitive = true   # 민감값 보호: terraform output 화면에서 ***로 가려짐
}
```
```bash
terraform output                # 모든 output 출력
terraform output vpc_id         # 특정 값만
terraform output -json          # 스크립트가 파싱하기 좋은 JSON으로
```
> `sensitive = true`를 붙이면 콘솔 출력에서 가려지지만, **tfstate 파일 안에는 평문으로 남는다.** 진짜 비밀은 tfstate 자체를 보호(원격 backend 암호화)해야 한다 — 9장 참조.

### 6.3 Local Values — 코드 내부의 중간 계산 변수

같은 표현식이 여러 군데 반복될 때 한 곳에 묶어두는 것. 비유하면 함수 안에서 `name = first + last`를 한 번 계산해두고 여러 줄에서 재사용하는 지역 변수다. **variable과 차이**: variable은 밖에서 값을 받지만, local은 밖에서 못 바꾸는 내부 전용 값이다(보통 variable들을 조합해 만든다).

대표 용도는 **이름 prefix 통일**과 **공통 태그**다. 모든 리소스 이름을 `myapp-dev-...`로 맞추고, 모든 리소스에 같은 태그(누가 관리? 어느 환경?)를 붙이면 나중에 AWS 콘솔에서 찾고 비용 추적하기가 쉬워진다.

```hcl
# locals.tf
locals {
  name_prefix = "${var.project}-${var.env}"   # 예: "myapp-dev"

  common_tags = {
    Project   = var.project
    Env       = var.env
    ManagedBy = "terraform"   # "이건 손으로 만지지 말고 코드로 관리됨" 표시
  }
}

# 사용 예: merge로 공통 태그 + 개별 이름 태그를 합침
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags       = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
}
```

---

## 7. Data Sources — "만들지 않고 조회만"

**비유:** `resource`가 "새로 짓기"라면 `data`는 "이미 있는 걸 검색해서 참조하기"다. 예를 들어 EC2를 만들려면 OS 이미지(AMI) ID가 필요한데, 이 ID는 AWS가 OS를 업데이트할 때마다 바뀐다. 코드에 `ami-12345`처럼 박아두면 금방 낡는다. 대신 `data`로 "최신 Amazon Linux를 찾아줘"라고 조회하면 항상 최신 ID가 자동으로 들어온다.

**언제 쓰나:** ① 자주 바뀌는 값(최신 AMI) ② AWS가 정해주는 값(가용영역 목록) ③ 다른 팀/다른 코드가 이미 만든 리소스를 참조할 때. 형식은 `data "타입" "이름"`이고, 참조는 `data.타입.이름.속성`으로 한다(`resource`와 달리 앞에 `data.`가 붙는 게 차이).

```hcl
# 최신 Amazon Linux 2 AMI 자동 조회
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 사용 가능한 AZ 목록 조회
data "aws_availability_zones" "available" {
  state = "available"
}

# 기존 VPC 가져오기 (이미 만들어진 VPC를 코드에서 참조)
data "aws_vpc" "existing" {
  id = "vpc-0123456789abcdef0"
}

# 사용 예
resource "aws_instance" "web" {
  ami               = data.aws_ami.amazon_linux.id
  instance_type     = "t3.micro"
  availability_zone = data.aws_availability_zones.available.names[0]
}
```

---

## 8. Modules (D2)

### 8.1 모듈이란? — "인프라 부품을 함수처럼"

**비유:** 모듈은 **함수**다. "VPC + 서브넷 + IGW + 라우팅" 한 세트를 만드는 코드를 매번 복붙하는 대신, `vpc`라는 함수로 한 번 만들어두고 `module "vpc" { cidr = "10.0.0.0/16" }`처럼 호출만 한다. dev에서 한 번, prod에서 또 한 번 — 같은 부품을 값만 바꿔 찍어낸다.

기술적으로는 **`.tf` 파일들이 든 폴더 하나 = 모듈 하나**다. 사실 지금 D1에서 작업한 `terraform/` 폴더도 이미 모듈이다(루트 모듈). 거기서 다른 폴더를 호출하면 그게 자식 모듈이 된다.

```
용어            의미
─────────────   ─────────────────────────────────────────────
Root Module     terraform 명령을 실행하는 최상위 폴더 (호출하는 쪽)
Child Module    Root가 불러다 쓰는 하위 모듈 (modules/vpc 등, 호출당하는 쪽)
입력             module 블록에 넘기는 인자  = 함수의 매개변수
출력             모듈의 output             = 함수의 return 값
```

```
terraform/
├── main.tf          ← root module (호출하는 쪽). "vpc 함수 불러와"
├── variables.tf
├── outputs.tf
├── locals.tf
└── modules/
    ├── vpc/         ← VPC 모듈 (호출당하는 쪽, 함수 정의)
    │   ├── main.tf       리소스 본체
    │   ├── variables.tf  이 모듈이 받을 입력(매개변수)
    │   └── outputs.tf    이 모듈이 돌려줄 출력(return)
    └── ec2/         ← EC2 모듈
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

**왜 모듈로 나누나 (세 가지 이득):**
- **재사용**: VPC 구성을 dev/stg/prod에서 똑같이, 값만 바꿔 호출.
- **캡슐화**: VPC 내부 복잡함(서브넷·라우팅·IGW)을 숨기고, 쓰는 쪽은 `cidr`만 넘기면 됨.
- **유지보수**: 라우팅 규칙을 바꿔야 하면 모듈 한 곳만 고치면 모든 환경에 반영.

> **주의:** 모듈을 추가하거나 source를 바꾸면 `terraform init`을 다시 돌려야 한다(Terraform이 모듈을 찾아 연결하는 과정 필요). 안 하면 "Module not installed" 에러.

### 8.2 모듈 작성 (modules/vpc/)

```hcl
# modules/vpc/variables.tf
variable "cidr_block"    { type = string }
variable "env"           { type = string }
variable "subnet_count"  { type = number; default = 2 }

# modules/vpc/main.tf
data "aws_availability_zones" "az" { state = "available" }

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  tags = { Name = "${var.env}-vpc" }
}

resource "aws_subnet" "public" {
  count                   = var.subnet_count
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.az.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${var.env}-public-${count.index}" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id
  tags   = { Name = "${var.env}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public" {
  count          = var.subnet_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# modules/vpc/outputs.tf
output "vpc_id"            { value = aws_vpc.this.id }
output "public_subnet_ids" { value = aws_subnet.public[*].id }
```

### 8.3 모듈 호출 (root main.tf)

루트에서 모듈을 "함수 호출"한다. `source`로 어느 폴더인지 지정하고, 나머지는 그 모듈의 `variables.tf`가 요구하는 입력을 넘긴다. 모듈이 만든 결과는 `module.<모듈이름>.<output이름>`으로 꺼내 쓴다.

```hcl
module "vpc" {
  source       = "./modules/vpc"   # 로컬 폴더 경로 (또는 Registry 주소·git URL)
  cidr_block   = var.vpc_cidr       # ↓ 아래 3개가 vpc 모듈에 넘기는 "입력(인자)"
  env          = var.env
  subnet_count = var.subnet_count
}

# 모듈 output 참조: module.<모듈이름>.<output이름>
resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnet_ids[0]   # vpc 모듈이 돌려준 서브넷 ID 사용
}

output "vpc_id" {
  value = module.vpc.vpc_id   # 모듈 결과를 루트의 최종 output으로 다시 노출
}
```

**값이 흐르는 방향 (이게 모듈의 전부):**
```
루트의 var.vpc_cidr ──(입력)──▶ 모듈의 var.cidr_block
                                       ↓ (모듈이 리소스 생성)
루트의 module.vpc.vpc_id ◀──(출력)── 모듈의 output "vpc_id"
```

> `source`는 로컬 경로(`./modules/vpc`)뿐 아니라 공개 Registry(`terraform-aws-modules/vpc/aws`)나 git URL도 가능하다. 실무에서는 검증된 공식 모듈을 가져다 쓰는 경우도 많다(D4~D5에서 맛보기).

---

## 9. State 관리 (D3)

### 9.1 State 파일 구조

```
terraform.tfstate 파일 내용 (JSON):
{
  "version": 4,
  "resources": [
    {
      "type": "aws_s3_bucket",
      "name": "practice",
      "instances": [
        {
          "attributes": {
            "id": "terraform-practice-bucket",
            "bucket": "terraform-practice-bucket",
            ...
          }
        }
      ]
    }
  ]
}
```

### 9.2 Remote State — S3 Backend

팀 협업 시 로컬 tfstate 파일은 충돌 위험. S3에 저장.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "dev/vpc/terraform.tfstate"   # 환경/서비스/파일명
    region         = "ap-northeast-2"
    dynamodb_table = "terraform-state-lock"         # 동시 apply 방지 락
    encrypt        = true
  }
}
```

**LocalStack으로 Remote State 테스트:**

```hcl
terraform {
  backend "s3" {
    bucket                      = "tf-state-local"
    key                         = "dev/terraform.tfstate"
    region                      = "us-east-1"
    access_key                  = "test"
    secret_key                  = "test"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style            = true
    endpoint                    = "http://localhost:4566"
  }
}
```

```bash
# S3 버킷 먼저 생성 후 backend 설정
aws --endpoint-url=http://localhost:4566 s3 mb s3://tf-state-local
terraform init -reconfigure
```

### 9.3 State 명령어

```bash
terraform state list                                # 리소스 목록
terraform state show aws_vpc.main                   # 특정 리소스 상세 보기
terraform state mv aws_s3_bucket.old aws_s3_bucket.new  # 이름 변경 (코드 리팩토링 시)
terraform state rm aws_s3_bucket.practice           # state에서만 제거 (실제 리소스는 남음)
terraform import aws_s3_bucket.practice my-bucket  # 기존 리소스 → state 편입
```

### 9.4 State 충돌 시나리오와 Lock

```
팀원 A: terraform apply 실행 중...
팀원 B: 동시에 terraform apply 실행 → state 파일 덮어써 버림 → 인프라 불일치

해결: State Lock
  → apply 시작 시 락 획득(잠금)
  → 다른 사람이 apply하면 "락 잡혀있음" 감지 → 대기 또는 에러
  → 완료 후 락 해제

S3 backend의 락 방법:
  - (전통) 별도 DynamoDB 테이블에 락 레코드 기록 — dynamodb_table 설정
  - (최신) S3 자체 조건부 쓰기로 락 — use_lockfile = true (DynamoDB 불필요, 신버전)
```

> 락이 비정상 종료로 남아버리면(stale lock) `terraform force-unlock <LOCK_ID>`로 강제 해제. 단, 정말 아무도 apply 안 하는 걸 확인하고 써야 한다.

### 9.5 Backend 종류

State를 어디에 둘지 결정하는 게 backend다.

```
backend 종류    저장 위치              락 지원   용도
─────────────   ────────────────────   ───────   ─────────────────────────
local (기본)    로컬 terraform.tfstate  파일 락   혼자 학습·실습 (지금 D1~D3)
s3              AWS S3 + DynamoDB/락    O         AWS 환경 팀 협업 (가장 흔함)
gcs             Google Cloud Storage    O         GCP 환경
azurerm         Azure Blob Storage      O         Azure 환경
Terraform Cloud HashiCorp 관리형         O         원격 실행·정책·UI까지
```

> **D3 실습은 local → s3 backend 전환**이 핵심 학습 포인트. LocalStack S3를 backend로 써서 "원격 state"를 흉내 내본다(9.2 참조).

---

## 10. Workspace (D3)

**비유:** 하나의 게임(코드)으로 여러 개의 세이브 슬롯(dev/prod)을 두는 것. 코드는 그대로 두고, workspace를 전환하면 그 환경 전용 tfstate로 바뀐다. 그래서 dev에서 실험한 게 prod에 영향을 주지 않는다.

같은 코드로 dev / stg / prod 환경을 분리하는 방법. 각 workspace는 **독립된 tfstate**를 가진다(세이브 슬롯이 따로따로).

```bash
terraform workspace new dev      # 생성
terraform workspace new stg
terraform workspace new prod
terraform workspace list         # 목록 (현재 workspace에 * 표시)
terraform workspace select prod  # 전환
terraform workspace show         # 현재 workspace 확인
```

**코드에서 workspace 이름 참조:**

```hcl
locals {
  env = terraform.workspace   # "dev", "stg", "prod" 등

  instance_type = {
    dev  = "t3.micro"
    stg  = "t3.small"
    prod = "t3.large"
  }
}

resource "aws_s3_bucket" "app" {
  bucket = "myapp-${local.env}-data"
}

resource "aws_instance" "web" {
  instance_type = local.instance_type[local.env]
}
```

**State 파일 위치:**

```
로컬: terraform.tfstate.d/dev/terraform.tfstate
      terraform.tfstate.d/prod/terraform.tfstate
S3:   s3://bucket/dev/terraform.tfstate
      s3://bucket/prod/terraform.tfstate   (key 경로에 workspace 이름 포함)
```

> **현업 주의 — workspace의 한계:** 코드가 100% 같아야 할 때만 적합하다. dev/prod의 구성이 꽤 다르거나(계정 분리, 리소스 종류 차이) 실수로 prod에서 apply하는 사고를 막고 싶다면, workspace보다 **환경별 폴더 분리**(`environments/dev/`, `environments/prod/`)가 더 안전하다는 게 다수 의견이다. workspace는 "거의 같은 환경의 가벼운 분기"에, 폴더 분리는 "확실히 다른 환경"에 쓴다고 기억하면 된다.

---

## 11. AWS Provider 심화 패턴 (D4)

> 이 장의 코드에 나오는 AWS 용어가 헷갈리면 [0장 AWS 기본 용어 빠른 사전](#0-aws-기본-용어-빠른-사전)을 옆에 두고 보자. 여기서는 그 용어들을 실제 Terraform 코드로 조립한다.

### 11.1 전체 네트워크 (VPC + Subnet + IGW + Route Table)

**무엇을 짓는가 (땅 분양 → 도로 연결 그림):**
```
VPC (내 땅 전체, 10.0.0.0/16)
 ├─ Public Subnet  (대로변, 10.0.0.0/24) ─┐
 ├─ Public Subnet  (대로변, 10.0.1.0/24) ─┤
 │                                         ├─▶ Route Table(공용) ─▶ IGW ─▶ 인터넷
 ├─ Private Subnet (안쪽, 10.0.10.0/24)    │   "0.0.0.0/0은 IGW로 보내라"
 └─ Private Subnet (안쪽, 10.0.11.0/24)    │
   IGW = 땅의 정문(인터넷 출입구)          │
   Route Table = 도로 표지판               ┘
   → Public 서브넷만 표지판이 IGW를 가리켜서 인터넷과 통함. Private은 안 가리켜서 격리됨.
```

```hcl
data "aws_availability_zones" "az" { state = "available" }

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "${local.name_prefix}-vpc" }
}

# 퍼블릭 서브넷 (2개)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.az.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${local.name_prefix}-public-${count.index}" }
}

# 프라이빗 서브넷 (2개)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.az.names[count.index]
  tags = { Name = "${local.name_prefix}-private-${count.index}" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.name_prefix}-igw" }
}

# Route Table (퍼블릭용)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${local.name_prefix}-rt-public" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
```

### 11.2 Security Group

```hcl
resource "aws_security_group" "web" {
  name        = "${local.name_prefix}-web-sg"
  description = "Web server security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"   # 모든 프로토콜
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${local.name_prefix}-web-sg" }
}

# 서비스 간 SG 참조 (CIDR 대신 SG ID 사용 → 더 안전)
resource "aws_security_group" "rds" {
  name   = "${local.name_prefix}-rds-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]   # web SG에서만 허용
  }
}
```

### 11.3 IAM Role + Policy

```hcl
# EC2가 S3에 읽기 권한
resource "aws_iam_role" "ec2_role" {
  name = "${local.name_prefix}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "s3_read" {
  name = "s3-read-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::${aws_s3_bucket.app.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.app.bucket}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}
```

### 11.4 EC2 (완전한 예시)

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.env == "prod" ? "t3.large" : "t3.micro"
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
  EOF

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = merge(local.common_tags, { Name = "${local.name_prefix}-web" })

  lifecycle {
    create_before_destroy = true   # 교체 시 새 것 먼저 만들고 삭제
  }
}
```

### 11.5 PF-IaC 최종 폴더 구조 (D5 목표)

```
terraform/
├── main.tf              # provider + module 호출
├── variables.tf         # 모든 변수 선언
├── outputs.tf           # 최종 output
├── locals.tf            # 공통 태그·이름 prefix
├── terraform.tfvars     # dev 기본값
├── prod.tfvars          # prod 값
├── versions.tf          # required_providers (별도 파일로 분리하는 컨벤션)
└── modules/
    ├── vpc/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── ec2/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── security_groups/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### 11.6 lifecycle 메타인자 — 리소스 교체·삭제 제어

모든 리소스에 붙일 수 있는 특수 블록. 위험한 교체/삭제를 통제한다.

```hcl
resource "aws_instance" "web" {
  # ...
  lifecycle {
    create_before_destroy = true   # 교체 시 새것 먼저 생성 후 기존 삭제 → 다운타임 최소화
    prevent_destroy       = true   # 실수로 destroy되는 것을 차단(운영 DB·S3 등에)
    ignore_changes        = [tags] # 이 속성이 콘솔에서 바뀌어도 Terraform이 무시
  }
}
```
- `create_before_destroy`: 기본은 "삭제 후 생성"이라 잠깐 끊긴다. 이걸 켜면 순서가 뒤집혀 무중단에 가까워진다.
- `prevent_destroy`: 이게 켜진 리소스를 destroy하려 하면 plan이 **에러로 막는다**. 운영 데이터 보호 장치.
- `ignore_changes`: 오토스케일링이 인스턴스 수를 바꾸는 등 "Terraform 밖에서 정당하게 바뀌는" 속성을 드리프트로 취급하지 않게 한다.

### 11.7 Provisioner — 있지만 되도록 쓰지 마라

리소스 생성 후 SSH로 명령을 실행하는 기능(`remote-exec`, `local-exec`).

```hcl
resource "aws_instance" "web" {
  # ...
  provisioner "remote-exec" {
    inline = ["sudo apt update", "sudo apt install -y nginx"]
  }
}
```
> **HashiCorp 공식 입장도 "최후의 수단".** 이유: ① 선언형이 아니라 명령형이라 멱등성이 깨짐 ② 실패하면 리소스가 tainted 상태로 꼬임 ③ plan에 안 잡혀서 예측 불가. **서버 내부 설정은 Ansible(구성관리)에게 맡기는 게 정석** — PF-IaC가 Terraform+Ansible 조합인 이유. 단순 부팅 스크립트는 `user_data`로 충분하다.

### 11.8 자주 만나는 에러와 대응

```
에러                                    원인 / 대응
──────────────────────────────────────  ──────────────────────────────────────────
Error: ... already exists               state에 없는 리소스를 또 만들려 함
                                        → terraform import로 기존 리소스 편입

Error acquiring the state lock          이전 apply가 락을 남기고 죽음
                                        → 확인 후 terraform force-unlock <ID>

Provider produced inconsistent result   Provider/LocalStack 버그·미지원
                                        → 버전 확인, 해당 기능 LocalStack 지원 여부 확인

forces replacement (예상 못한 교체)      바꿀 수 없는 속성을 변경함(-/+)
                                        → plan 꼼꼼히 읽고, 의도면 진행/아니면 코드 수정

value depends on resource attributes    count/for_each에 apply 후에야 아는 값 사용
that cannot be determined until apply   → 정적인 값으로 분리하거나 -target으로 단계 적용

Error: Reference to undeclared variable  변수 선언 누락 / 오타
                                        → variables.tf에 variable 블록 확인
```

---

## 12. 면접 Q&A

> 외우는 게 아니라 **입으로 말할 수 있는지** 확인하는 용도. 각 답변을 보지 않고 30초~1분 안에 설명해볼 것.

---

### 기초 개념

**Q. Terraform이 뭔가요? 한 문장으로 설명해보세요.**

인프라를 코드(.tf 파일)로 선언하면 `terraform apply` 한 번으로 AWS 리소스를 자동 생성·변경·삭제해주는 IaC 도구입니다.

**Q. IaC를 써야 하는 이유는?**

AWS 콘솔 클릭으로 만든 인프라는 재현이 안 되고, 협업이 어렵고, 변경 이력이 없습니다. Terraform은 코드로 관리하므로 git으로 이력 추적, 코드 리뷰로 실수 방지, 동일 환경 반복 재현이 가능합니다. 특히 dev/stg/prod를 동일하게 유지하거나 장애 시 인프라를 빠르게 재구성할 때 강력합니다.

**Q. Terraform은 선언형이라고 하는데 무슨 뜻인가요?**

"EC2를 만들어라 → 완료 기다려라 → 보안그룹 연결해라" 처럼 순서와 절차를 명시하는 게 명령형입니다. Terraform은 "EC2와 보안그룹이 이런 상태여야 한다"고 결과만 선언하면, 현재 상태와 비교해서 필요한 작업을 알아서 실행합니다. 개발자가 순서나 에러 처리를 신경 쓸 필요가 없습니다.

**Q. Provider가 뭔가요?**

Terraform 자체는 AWS API를 모릅니다. `hashicorp/aws` Provider가 AWS API 호출법을 알고 있는 플러그인이고, `terraform init` 시 다운로드됩니다. Azure를 쓰려면 Provider만 바꾸면 됩니다.

**Q. resource 블록에서 인자가 두 개인데 각각 뭔가요?**

```hcl
resource "aws_s3_bucket" "practice" { ... }
```
첫 번째 `"aws_s3_bucket"`은 Provider가 정의한 리소스 타입이고, 두 번째 `"practice"`는 Terraform 코드 내부 식별자입니다. 다른 곳에서 `aws_s3_bucket.practice.id` 처럼 참조할 때 씁니다. AWS 리소스 이름과는 무관합니다.

---

### 워크플로우

**Q. terraform init이 하는 일은?**

Provider 플러그인을 다운로드해서 `.terraform/` 폴더에 저장하고, `.terraform.lock.hcl` 파일을 생성해 버전을 고정합니다. 코드를 처음 작성하거나 Provider를 변경할 때 실행합니다.

**Q. terraform plan과 apply 차이는?**

`plan`은 변경사항을 미리보기만 하고 실제 AWS 리소스는 건드리지 않습니다. `apply`는 plan을 실행해서 실제로 리소스를 생성·변경·삭제합니다. 운영 환경에서는 반드시 plan 결과를 팀이 검토한 후 apply하는 프로세스를 씁니다.

**Q. plan 출력에서 `(known after apply)`가 뭔가요?**

S3 버킷 ARN이나 EC2 인스턴스 ID처럼 실제로 리소스가 생성된 후에야 AWS가 알려주는 값입니다. plan 단계에서는 아직 리소스가 없으므로 알 수 없고, apply 완료 후 tfstate에 기록됩니다.

**Q. terraform destroy는 언제 쓰나요?**

관리되는 모든 리소스를 삭제합니다. 실습 환경 정리나 임시 인프라 제거에 씁니다. 운영 환경에서는 특정 리소스만 삭제하려면 `terraform destroy -target=리소스명`을 씁니다.

**Q. .terraform.lock.hcl은 왜 있나요?**

`init` 시 선택된 Provider 버전을 고정해두는 파일입니다. 팀원이 같은 버전을 쓰도록 보장하기 위해 git에 커밋합니다. `package-lock.json`이나 `go.sum`과 같은 역할입니다.

**Q. .gitignore에 .terraform/을 넣는 이유는?**

`.terraform/` 폴더는 Provider 바이너리(수백 MB)가 들어있어서 git에 올리면 안 됩니다. 각자 `terraform init`으로 다운로드하면 됩니다. `terraform.tfstate`는 민감한 리소스 정보(비밀번호, 키 등)가 평문으로 들어있어서 역시 git에 올리면 안 됩니다.

---

### State

**Q. Terraform State란 무엇인가요?**

Terraform이 실제 인프라와 코드 사이를 매핑하는 파일(`terraform.tfstate`)입니다. `plan` 시 코드(원하는 상태)와 state(현재 상태)를 비교해 차이만 변경합니다. State가 없으면 Terraform은 AWS에 이미 뭐가 있는지 알 수 없습니다.

**Q. tfstate 파일을 git에 올리면 안 되는 이유는?**

DB 비밀번호, API 키, 인증서 등 민감한 정보가 평문 JSON으로 저장됩니다. git에 올리면 이력에 영구적으로 남고, 팀원이 동시에 apply할 때 파일 충돌도 발생합니다.

**Q. Remote State를 왜 쓰나요?**

로컬 tfstate는 혼자 쓸 때는 괜찮지만 팀 환경에서는 두 사람이 동시에 apply하면 state 파일이 덮어써지는 충돌이 납니다. S3에 저장하고 DynamoDB로 락을 걸면, 한 사람이 apply 중일 때 다른 사람은 락이 해제될 때까지 대기합니다.

**Q. terraform import가 뭔가요?**

Terraform 없이 콘솔 클릭으로 이미 만들어진 리소스를 Terraform으로 관리하고 싶을 때, 그 리소스를 tfstate에 편입시키는 명령입니다. import 후 코드도 그에 맞게 작성해야 합니다.

---

### 구조·설계

**Q. Module을 왜 사용하나요?**

반복되는 인프라 패턴(VPC+서브넷+IGW 조합 등)을 재사용 가능한 단위로 캡슐화합니다. dev/stg/prod 각 환경에서 같은 모듈을 다른 변수로 호출해 일관성을 유지하고, 변경이 필요하면 모듈 내부만 수정하면 모든 환경에 반영됩니다.

**Q. count vs for_each 언제 각각 사용하나요?**

`count`는 숫자 기반이라 중간 요소가 삭제되면 인덱스가 밀려 이후 리소스가 재생성됩니다. `for_each`는 map/set 기반으로 각 리소스가 고유한 키로 식별돼 중간 삭제 시 다른 리소스에 영향이 없습니다. 실무에서는 `for_each` 권장합니다.

**Q. variable과 local의 차이는?**

`variable`은 외부에서 값을 주입받는 입력 인터페이스입니다 (tfvars, -var 플래그). `local`은 코드 내부에서만 쓰는 중간 계산값으로, 반복되는 표현식을 한 곳에서 관리할 때 씁니다. 외부에서 바꿀 수 없습니다.

**Q. data source가 resource와 다른 점은?**

`resource`는 Terraform이 직접 생성·관리하는 리소스입니다. `data`는 이미 존재하는 리소스를 읽어오기만 하고 생성하지 않습니다. 예를 들어 최신 Amazon Linux AMI ID를 하드코딩 대신 `data.aws_ami`로 자동 조회하면 항상 최신 버전을 씁니다.

**Q. Terraform과 CloudFormation 차이는?**

CloudFormation은 AWS 전용이고 YAML/JSON으로 작성합니다. Terraform은 HCL이 더 직관적이고, AWS + Kubernetes + 모니터링 인프라를 단일 코드베이스로 관리할 수 있습니다. 단, CloudFormation은 AWS 서비스와 더 깊이 통합되어 있고 State를 AWS가 자동으로 관리합니다.

---

### 실무 트러블슈팅

**Q. LocalStack에서 S3 생성 시 DNS 에러가 났는데 원인과 해결법은?**

S3의 기본 URL 방식은 가상 호스트 스타일(`http://버킷명.localhost:4566/`)인데, `버킷명.localhost`를 DNS가 찾지 못해서 에러가 납니다. Provider에 `s3_use_path_style = true`를 추가하면 `http://localhost:4566/버킷명` 형식으로 바뀌어 LocalStack이 정상 처리합니다.

**Q. terraform apply 했는데 이미 AWS에 같은 리소스가 있다면?**

State에 없는 리소스는 Terraform이 모르기 때문에 새로 만들려다가 "already exists" 에러가 납니다. `terraform import`로 기존 리소스를 state에 편입한 후 코드와 맞추면 됩니다.

**Q. plan에서 `-/+` 표시가 나왔는데 무슨 의미인가요?**

삭제 후 재생성(`forces replacement`)을 의미합니다. 수정이 아니라 리소스를 지우고 새로 만드는 것이므로 운영 중인 EC2라면 다운타임이 발생합니다. 이 경우 `create_before_destroy` lifecycle 설정으로 새 것을 먼저 만들고 기존 것을 삭제하는 방식으로 다운타임을 줄일 수 있습니다.

---

### 심화 — 내부 동작·아키텍처

**Q. Terraform이 어떻게 AWS를 제어하나요? 내부 구조를 설명해보세요.**

Terraform Core라는 엔진과 Provider 플러그인으로 나뉩니다. Core는 HCL을 파싱해 리소스 의존성 그래프를 만들고 state와 코드를 비교해 실행 계획을 세우는 범용 엔진이고, AWS API 지식은 전혀 없습니다. 실제 API 호출은 `terraform-provider-aws` Provider가 담당하며, Core가 gRPC로 이 플러그인과 통신합니다. 이 분리 덕분에 Provider만 바꾸면 Azure·GCP도 같은 방식으로 관리할 수 있습니다.

**Q. terraform plan은 정확히 무엇과 무엇을 비교하나요?**

코드(원하는 상태)와 state(현재 상태)를 비교합니다. plan은 먼저 refresh 단계에서 실제 클라우드를 조회해 state를 최신화하고, 그다음 갱신된 state와 코드의 차이를 계산해 create/update/destroy/replace 계획을 만듭니다. 즉 "코드 vs 실제(state에 반영된)"의 diff입니다.

**Q. 드리프트(drift)가 뭔가요? 어떻게 감지하나요?**

코드(또는 state)와 실제 인프라가 어긋난 상태입니다. 보통 누군가 콘솔에서 직접 리소스를 수정할 때 생깁니다. `terraform plan`을 돌리면 refresh 단계에서 실제를 조회하므로 차이가 드러나고, `terraform plan -refresh-only`로 드리프트만 따로 확인할 수도 있습니다. 코드 기준으로 되돌리려면 그냥 apply하면 실제가 코드 상태로 복원됩니다 — 이게 IaC의 자가 치유 성질입니다.

**Q. 코드에서 리소스 블록을 지우면 어떻게 되나요?**

다음 plan에서 "코드엔 없는데 state엔 있다 → destroy"로 해석되어 실제 리소스가 삭제됩니다. 코드에서만 제거하고 실제 리소스는 남기려면 `terraform state rm`으로 state에서만 빼야 합니다.

**Q. 멱등성(idempotency)이 IaC에서 왜 중요한가요?**

같은 apply를 여러 번 실행해도 결과가 한 번 실행한 것과 같아야, 자동화 파이프라인에서 안심하고 반복 실행할 수 있습니다. Bash 스크립트는 "이미 만들어진 걸 또 만들려다" 에러가 나기 쉽지만, Terraform은 현재 상태와 비교해 부족한 것만 처리하므로 몇 번을 돌려도 선언한 상태 하나로 수렴합니다.

---

### 심화 — 문법·설계

**Q. depends_on은 언제 쓰나요? 남용하면 안 되는 이유는?**

리소스 간 순서가 필요하지만 속성 참조로는 드러나지 않을 때만 씁니다(예: IAM 정책이 붙은 뒤에 EC2가 부팅돼야 할 때). 평소엔 `aws_subnet.x.vpc_id = aws_vpc.main.id`처럼 속성을 참조하면 Terraform이 순서를 자동 추론합니다(암묵적 의존성). depends_on을 남발하면 그래프가 과도하게 직렬화돼 병렬 생성이 줄고, 의존 이유가 코드에 안 드러나 유지보수가 어려워집니다.

**Q. dynamic 블록은 왜 쓰나요?**

Security Group의 ingress처럼 같은 중첩 블록을 여러 개 만들 때, 복붙 대신 리스트/맵을 순회해 생성합니다. 규칙을 추가·삭제할 때 변수 데이터만 바꾸면 되므로 코드 중복이 사라집니다.

**Q. 조건에 따라 리소스를 만들거나 안 만들려면?**

`count = var.flag ? 1 : 0` 패턴을 씁니다. false면 0개가 되어 리소스가 생성되지 않습니다. 단 count를 쓰면 리스트가 되므로 참조 시 `[0]` 인덱스가 필요합니다.

**Q. Provisioner를 쓰면 안 되는 이유는?**

remote-exec 같은 provisioner는 명령형이라 멱등성이 깨지고, 실패 시 리소스가 tainted로 꼬이며, plan에 안 잡혀 예측이 안 됩니다. 서버 내부 설정은 Ansible 같은 구성관리 도구에 맡기고, 간단한 초기화는 user_data를 쓰는 게 정석입니다. HashiCorp도 공식적으로 최후의 수단이라고 안내합니다.

**Q. lifecycle의 prevent_destroy와 ignore_changes는 각각 언제 쓰나요?**

`prevent_destroy`는 운영 DB나 S3처럼 실수로 삭제되면 치명적인 리소스에 걸어 destroy를 plan 단계에서 막습니다. `ignore_changes`는 오토스케일링이 인스턴스 수를 바꾸는 것처럼 Terraform 밖에서 정당하게 변하는 속성을, 드리프트로 취급하지 않고 무시하게 합니다.

---

## 13. 일차별 자가 점검 (D1~D5)

> 매일 실습 직후, 답을 보지 않고 **입으로** 답해본다. 막히면 괄호 안 섹션을 다시 읽는다. 솔루션을 봐야 답이 나오면 "이해 못 한 것"으로 친다(코딩테스트 복습 원칙과 동일).

### D1 — provider + S3 (5장)
```
Q1. terraform init / plan / apply / destroy를 각각 언제 실행하나요?       (4장)
Q2. resource "aws_s3_bucket" "practice"에서 "practice"의 역할은?          (2장 ②)
Q3. plan 출력에서 (known after apply)가 뜨는 이유는?                       (4장)
Q4. s3_use_path_style = true가 왜 필요한가요?                              (5.4)
Q5. .gitignore에 .terraform/ 과 tfstate를 넣는 이유는 각각 뭔가요?         (5.1, 9장)
Q6. .terraform.lock.hcl은 왜 git에 커밋하나요?                            (5.2)
Q7. Terraform이 docker-compose와 비슷한 점과 다른 점은?                    (1장)
```

### D2 — Variables · Outputs · Modules (6·8장)
```
Q1. variable 값 주입 방법 4가지와 우선순위는?                              (6.1)
Q2. variable과 local의 차이는? 각각 언제 쓰나요?                           (6.1, 6.3)
Q3. output을 쓰는 이유 2가지는? (사람 확인 말고 또 하나)                    (6.2)
Q4. 모듈을 "함수"에 비유하면 입력·출력·호출은 각각 무엇에 해당하나요?        (8.1)
Q5. module.vpc.public_subnet_ids[0] 이 문법을 풀어 설명해보세요.            (8.3)
Q6. 모듈을 추가한 뒤 반드시 다시 실행해야 하는 명령은? 왜?                   (8.1)
Q7. count와 for_each 중 무엇을 권장하고 왜인가요?                           (3.3, Q&A)
```

### D3 — State · Backend · Workspace (9·10장)
```
Q1. Terraform이 plan에서 비교하는 "세 가지 상태"는 무엇인가요?              (2장 ⑥)
Q2. 드리프트(drift)란? 어떻게 감지하고 어떻게 되돌리나요?                    (2장 ⑥, 9장)
Q3. tfstate를 git에 올리면 안 되는 이유 2가지는?                           (9장, Q&A)
Q4. Remote State(S3 backend)를 쓰는 이유는? 락은 왜 필요한가요?             (9.2, 9.4)
Q5. local backend와 s3 backend의 차이를 한 문장으로?                       (9.5)
Q6. workspace와 "환경별 폴더 분리"는 각각 언제 쓰나요?                       (10장)
Q7. 코드에서 리소스 블록을 지우면 실제 인프라는 어떻게 되나요?               (2장 ⑥)
```

### D4 — IAM · Security Group · 네트워크 (11장)
```
Q1. Public Subnet과 Private Subnet을 가르는 것은 무엇인가요? (라우팅 관점)   (11.1)
Q2. Security Group에서 ingress와 egress는 각각 무엇인가요?                  (11.2)
Q3. SG 규칙에서 CIDR 대신 다른 SG의 ID를 쓰면 뭐가 더 안전한가요?           (11.2)
Q4. IAM Role · Policy · Instance Profile의 관계를 설명해보세요.             (0.3, 11.3)
Q5. AssumeRole이 무엇이고 EC2는 왜 이걸 쓰나요?                            (0.3, 11.3)
Q6. lifecycle의 create_before_destroy / prevent_destroy는 각각 언제?       (11.6)
Q7. Provisioner를 쓰지 말라는 이유와, 대신 무엇을 쓰나요?                    (11.7)
```

### D5 — 통합·정리 (전체)
```
Q1. terraform/ 폴더를 main/variables/outputs/locals/versions로 나누는 이유는?  (11.5)
Q2. dev와 prod에서 같은 코드로 다른 크기 서버를 만들려면 어떻게 설계하나요?   (6장, 10장)
Q3. plan을 -out으로 저장해서 apply하는 게 왜 안전한가요?                     (4장)
Q4. CI/CD에서 terraform 단계를 순서대로 나열해보세요.                        (4장)
Q5. 이 프로젝트(PF-IaC)를 면접관에게 30초로 설명한다면?                       (README)
Q6. Terraform으로 EC2를 띄운 뒤 그 안에 Docker를 설치하려면? (도구 선택)      (1.5, 11.7)
```

> **통과 기준:** D1~D3는 막힘없이(IaC의 뼈대). D4~D5는 키워드라도 짚으면 합격 — 면접에서 더 깊이 들어오면 그때 11장·Q&A로 보강.

---

## 일차별 실습 체크포인트

```
D1 (6/23): provider + S3 버킷 → init/plan/apply/destroy 사이클 완성
D2 (6/24): variables.tf + outputs.tf + modules/vpc/ → VPC+Subnet IaC
D3 (6/25): S3 Remote State + DynamoDB Lock + Workspace → EC2 프로비저닝
D4 (6/26): IAM Role + Security Group + EC2 → 전체 인프라 모듈화
D5 (6/27): 위 모두 통합 + terraform/ 폴더 최종 정리 + README + 커밋
```

---

## 14. 베스트 프랙티스 & 안티패턴 & 보안

> 문서 곳곳에 흩어진 "이렇게 해야/하면 안 됨"을 한곳에 모았다. 면접에서 "Terraform 잘 쓰는 법?"을 물으면 여기서 골라 답하면 된다.

### 14.1 코드 작성 베스트 프랙티스

```
✅ 해야 할 것
─────────────────────────────────────────────────────────────────
파일 분리        main.tf / variables.tf / outputs.tf / locals.tf / versions.tf
                 → 사람이 읽기 쉽고, 변수·출력을 한눈에 파악
이름 일관성       locals의 name_prefix로 모든 리소스 이름을 myapp-dev-* 통일
공통 태그         common_tags(Project·Env·ManagedBy)를 merge로 전 리소스에
버전 고정         required_providers에 ~> 5.0, lock 파일 커밋 → 재현성
커밋 전 fmt       terraform fmt + validate를 습관화 (CI에도 -check로 강제)
변수 검증         validation 블록으로 잘못된 입력을 plan 전에 차단
plan 먼저 읽기    apply 전 plan의 +/~/-/-/+ 와 요약 줄을 반드시 확인
작은 모듈         모듈은 "하나의 일"만 (vpc 모듈은 네트워크만, ec2는 컴퓨팅만)
for_each 선호     리스트가 바뀌어도 안정적 → count보다 권장
```

### 14.2 안티패턴 (하면 안 되는 것)

```
❌ 안티패턴                          왜 나쁜가 / 대신
─────────────────────────────────   ────────────────────────────────────────
tfstate를 git에 커밋                 비밀번호 평문 노출 + 충돌 → 원격 backend로
.terraform/를 git에 커밋             수백 MB 바이너리 + OS 종속 → .gitignore
비밀번호를 코드에 하드코딩            git 이력에 영구 박제 → 변수 + 외부 시크릿
콘솔에서 직접 수정                    드리프트 발생 → 모든 변경은 코드로
-target 남용                         "코드=인프라" 원칙 붕괴 → 응급 시에만
거대한 단일 main.tf (수천 줄)         리뷰·재사용 불가 → 모듈로 분리
provisioner로 앱 설치                멱등성 깨짐 → Ansible/user_data
모든 걸 한 state에                   하나 깨지면 전체 위험 → 환경·서비스별 분리
```

### 14.3 보안 체크리스트 (면접 빈출 "IaC 보안은?")

```
1. tfstate 보호      원격 backend(S3) + 암호화(encrypt=true) + 접근 IAM 제한
                     → state엔 sensitive 값도 평문이므로 파일 자체를 지켜야 함
2. 시크릿 분리        DB 비번 등은 코드/tfvars 대신 환경변수·AWS Secrets Manager·Vault
3. 최소 권한          IAM Policy는 필요한 Action·Resource만 (와일드카드 * 남발 금지)
4. SG 최소 개방       0.0.0.0/0 인바운드는 80/443만, SSH(22)는 내 IP·SG 참조로 제한
5. 민감 출력 가림      output에 sensitive = true
6. 정적 분석          tfsec / checkov 로 보안 취약 설정 자동 검사 (CI에 추가)
7. 변경 검토          plan을 PR로 리뷰 후 apply (사람 승인 게이트)
```

> **PF-IaC 어필 포인트:** "tfstate는 S3 backend로 암호화 저장하고 접근을 IAM으로 제한했으며, DB 비밀번호는 코드에 두지 않고 Vault로 분리했습니다. CI에서 tfsec으로 보안 스캔도 돌립니다." — 이 한 마디가 보안 의식을 보여준다.

### 14.4 팀 협업 워크플로우 (실무 흐름)

```
1. 브랜치 생성 → 코드 수정
2. terraform fmt + validate (로컬)
3. PR 올림 → CI가 terraform plan 자동 실행 → 결과를 PR에 코멘트
4. 동료가 plan diff 리뷰 (무엇이 생성·변경·삭제되는지)
5. 승인 → main 머지 → CI가 terraform apply (또는 Atlantis/ArgoCD)
6. Remote backend의 lock이 동시 apply 충돌 방지
```

---

## 15. Terraform 치트시트 (면접 전날·실습 중 빠른 참조)

### 15.1 명령어 한 장 요약

```
init                  provider·모듈 다운로드 (처음/추가 시)
init -upgrade         provider 버전 올리기
fmt                   코드 정렬          fmt -check (CI 검사)
validate              문법·참조 검사 (클라우드 호출 X)
plan                  변경 미리보기      plan -out=tfplan (저장)
apply                 적용              apply tfplan (저장본 적용)
apply -auto-approve   확인 없이 적용 (실습·CI용)
destroy               전체 삭제
output / output -json 결과값 출력
state list/show       state 안 리소스 보기
state rm / mv         state에서 제거 / 이름변경 (실제 리소스는 유지)
import                기존 리소스를 state로 편입
apply -replace=A      리소스 A만 강제 재생성
console               표현식 즉석 테스트
graph | dot           의존성 그래프 시각화
```

### 15.2 자주 쓰는 코드 스니펫

```hcl
# provider + 버전 고정
terraform {
  required_providers { aws = { source = "hashicorp/aws", version = "~> 5.0" } }
}

# 변수 + 검증
variable "env" {
  type = string
  validation { condition = contains(["dev","prod"], var.env), error_message = "dev/prod만" }
}

# 조건부 생성 / 반복
count    = var.enable ? 1 : 0
for_each = toset(["dev","stg","prod"])

# 참조 치트
var.x                        # 변수
local.x                      # 로컬
aws_vpc.main.id              # 리소스 속성
data.aws_ami.al.id           # 데이터소스
module.vpc.vpc_id            # 모듈 출력
aws_subnet.pub[*].id         # splat (전체)
each.key / each.value        # for_each 안
count.index                  # count 안
```

### 15.3 plan 기호 / 흐름 요약

```
+ 생성   ~ 수정(in-place)   - 삭제   -/+ 재생성(다운타임 주의)

코드(원함) ─┐
            ├─ plan = 비교 → 차이 계산 → apply = 실행 → tfstate 기록
실제(state) ┘     (refresh로 실제를 먼저 반영)
```

---

## 16. 용어집 (Glossary)

> 헷갈리는 Terraform 용어를 한 줄로. AWS 용어는 [0장](#0-aws-기본-용어-빠른-사전) 참조.

```
용어                  한 줄 정의
────────────────────  ─────────────────────────────────────────────────────────
IaC                   인프라를 코드로 선언·관리하는 방식
선언형(Declarative)    "결과 상태"를 적으면 도구가 알아서 맞춤 (vs 명령형=절차)
멱등성(Idempotency)    몇 번 실행해도 결과가 같은 성질
Provider              클라우드 API와 통신하는 플러그인 (AWS 통역사)
Resource              실제로 만드는 인프라 한 단위 (resource 블록)
Data Source           기존 리소스를 조회만 (생성 X, data 블록)
State (tfstate)        Terraform이 만든 것을 기록한 파일 (세이브 파일)
Backend               state를 저장하는 위치 (local/s3/...)
Remote State          state를 S3 등 원격에 저장 (팀 협업)
Drift(드리프트)        코드와 실제 인프라가 어긋난 상태
Plan                  변경 미리보기 (코드 vs state 비교)
Apply                 plan을 실제로 실행
Refresh               실제 클라우드를 조회해 state 최신화
Module                재사용 가능한 .tf 폴더 묶음 (함수)
Root/Child Module     실행하는 최상위 / 불려가는 하위 모듈
Variable / Local      외부 입력 / 내부 계산값
Output                모듈·구성이 내보내는 결과값
Meta-argument         모든 리소스에 쓸 수 있는 특수 인자 (count·for_each·depends_on·lifecycle)
count / for_each       리소스 여러 개 생성 (숫자 기반 / 키 기반)
depends_on            명시적 의존 순서 지정
lifecycle             교체·삭제 동작 제어 (create_before_destroy 등)
DAG                   의존성 방향 그래프 (순환 불가)
Lock                  동시 apply를 막는 잠금 (state 보호)
Workspace             하나의 코드로 여러 환경 state 분리 (세이브 슬롯)
Provisioner           리소스 생성 후 명령 실행 (되도록 회피)
.tf / .tfvars          구성 코드 / 변수값 파일
.terraform.lock.hcl    provider 버전 고정 파일 (커밋함)
HCL                   Terraform 설정 언어 (HashiCorp Configuration Language)
```
