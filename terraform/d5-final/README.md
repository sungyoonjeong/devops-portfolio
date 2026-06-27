# D5 — 통합 최종본 (d5-final)

D1~D4에서 단계별로 쌓은 모듈을 **하나의 스택**으로 합치고, D3의 원격 backend와
새 **RDS 모듈**까지 더한 통합본. "실무 IaC 폴더 구조의 뼈대"를 완성하는 게 D5의 목표다.

> 학습 여정 전체 맥락: 상위 [`../README.md`](../README.md) / 개념: [`../TERRAFORM_STUDY.md`](../TERRAFORM_STUDY.md)

## 무엇이 통합되었나

```
출처    →  d5-final 에서의 역할
─────────────────────────────────────────────────────────
d3      →  backend.tf : 원격 state(S3) + DynamoDB 락
d2/d4   →  modules/vpc : VPC·서브넷·IGW·RT (for_each)
d4      →  modules/security_groups : web SG(공개) + rds SG(web 출처만)
d4      →  modules/iam : Role→Policy→Instance Profile (키리스)
d4      →  modules/ec2 : 퍼블릭 서브넷 + web SG + IAM 프로파일
신규    →  modules/rds : 프라이빗 서브넷 + rds SG 의 PostgreSQL  ← D5 추가
```

전체 구조는 **2계층**: 외부 공개 웹(EC2, 퍼블릭 서브넷) ↔ 비공개 DB(RDS, 프라이빗 서브넷),
그 사이를 보안그룹이 "web에서 온 5432만" 통과시킨다.

## 폴더 구조

```
d5-final/
├── backend.tf        # 원격 state(S3+DynamoDB 락) + terraform/provider 요구사항
├── providers.tf      # AWS Provider(LocalStack 대상, rds 엔드포인트 포함)
├── main.tf           # S3 + 5개 모듈 합성 (핵심)
├── variables.tf      # 루트 입력 변수 (+ RDS 변수)
├── locals.tf         # name_prefix · 환경별 instance_type/db_class · common_tags
├── outputs.tf        # 각 모듈 출력 최종 노출 (+ db_endpoint)
├── terraform.tfvars  # dev 기본값
└── modules/
    ├── vpc/  security_groups/  iam/  ec2/   # d4 재사용
    └── rds/                                 # D5 신규
```

## 모듈 합성 흐름 (의존성 자동 추론)

```
                aws_s3_bucket.app ──ARN──► module.iam
module.vpc ──vpc_id──► module.security_groups
   │  └─public_subnet_ids[0]──┐         │
   │                          ├──► module.ec2 ◄─web_sg_id/instance_profile
   └─private_subnet_ids───────┐
                              └──► module.rds ◄─rds_sg_id
```
루트에서 한 모듈의 `output`을 다음 모듈의 `input`으로 넘기면, Terraform이 참조 관계로
생성 순서(vpc → sg → iam/ec2/rds)를 **자동 추론**한다. 명시적 `depends_on` 불필요.

## 실행법

```bash
localstack start -d                       # LocalStack 기동

# (최초 1회) 원격 state 저장소 만들기 — d3 의 bootstrap 재사용
cd ../d3/bootstrap && terraform init && terraform apply -auto-approve

cd ../../d5-final
terraform init                            # 원격 backend(S3) 초기화
terraform validate
terraform plan
terraform apply -auto-approve
terraform output summary                  # 전체 구성 한 줄 확인
terraform destroy -auto-approve

# 오프라인 문법 검증만:  terraform init -backend=false && terraform validate
```

검증 상태: `terraform validate` = **Success**, `terraform fmt -recursive` 적용 완료.

> **RDS 주의**: RDS는 LocalStack 무료판에서 제한적이다(Pro 기능). `validate`/`plan`까지는
> 문제없고, 실제 `apply`로 DB 인스턴스를 띄우려면 LocalStack Pro 또는 실제 AWS가 필요하다.

## IaC 보안 스캔 (checkov 실측)

PF2의 Trivy(이미지 스캔)와 짝이 되는 **IaC 정적 분석**. 실제로 돌린 결과:

```bash
checkov -d . --framework terraform --compact
# → Passed: 43,  Failed: 29,  Skipped: 0
```

29건의 Failed를 그대로 "고쳐야 할 버그"로 보면 안 된다. 성격별로 나누면:

**(A) 의도된 설계 — 이 구조에서는 정상**
- `CKV_AWS_130` 퍼블릭 서브넷이 공인 IP를 자동 부여 → **퍼블릭 서브넷의 존재 이유**가 그것.
- `CKV_AWS_260` web SG가 0.0.0.0/0에서 80/443 인바운드 허용 → **공개 웹 서버**라 의도된 개방.
  (대신 rds SG는 CIDR이 아니라 web SG 참조로 닫아 둠 — 닫을 곳은 닫았다는 근거.)

**(B) 프로덕션 하드닝 — PF-IaC(8월)에서 적용 예정**
- 관측/로깅: `CKV2_AWS_11`(VPC flow log), `CKV_AWS_129/CKV2_AWS_30`(RDS 로그/쿼리로그),
  `CKV_AWS_118`(RDS enhanced monitoring), `CKV_AWS_126`(EC2 detailed monitoring).
- 백업/내구성: `CKV_AWS_21`(S3 버저닝), `CKV_AWS_144`(S3 교차리전 복제),
  `CKV2_AWS_60`(스냅샷 태그 복사), `CKV_AWS_226`(RDS 자동 마이너 업그레이드).
- 암호화 강화: `CKV_AWS_145`(S3를 KMS 키로) — 지금은 기본 암호화만.

**(C) 실제로 반영할 만한 개선 — 우선순위 높음**
- `CKV2_AWS_6` S3 **퍼블릭 액세스 차단 블록** 추가 (실수 노출 방지, 비용 0).
- `CKV_AWS_79` EC2 **IMDSv2 강제** (`metadata_options { http_tokens = "required" }`) — SSRF 방어.
- `CKV_AWS_293` RDS **삭제 보호**, `CKV_AWS_157` prod **Multi-AZ**(이미 prod 분기 있음),
  `CKV_AWS_161` RDS **IAM 인증** — 비밀번호 의존도를 낮춤(Vault 연동과 함께).

즉 checkov 결과는 "29개 실패"가 아니라 **"43개 통과 + 의도 2 + 이월 다수 + 즉시개선 3"** 로
읽는 게 맞다. 이 분류 자체가 면접에서 "IaC 보안을 어떻게 다루나"에 대한 답이 된다.

## D5에서 손에 익히는 것 (D1~D4 복습 겸)

- 흩어진 모듈을 **한 스택으로 합성**하는 감각 — 무엇이 무엇의 출력을 먹는지.
- 원격 backend가 **여러 스택(d3/d5-final)을 같은 버킷의 다른 key로** 공존시키는 방식.
- 정적 스캔 결과를 **맹목적으로 다 고치지 않고 우선순위로 triage** 하는 실무 판단.
