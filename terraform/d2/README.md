# Terraform D2 실습 — 변수 · 로컬 · 모듈 · VPC IaC

D1(LocalStack S3 단일 리소스)에서 한 단계 나아가, **재사용 가능한 VPC 모듈**을
변수·로컬·for_each로 구성하고 LocalStack 위에 올린다.

## 학습 포인트
- `variable` 타입 제약(`map(object({...}))`)과 `validation` 블록
- `locals`로 이름 접두사·공통 태그 한 곳에서 관리
- `module`로 VPC 한 세트를 캡슐화하고 루트에서 호출
- `for_each`로 서브넷 N개를 맵 기반 동적 생성
- 모듈 `output` → 루트 `output` pass-through

## 만들어지는 리소스
- VPC 1개 (`10.0.0.0/16`)
- 퍼블릭 서브넷 2개 (AZ a/b) + 인터넷 게이트웨이 + 퍼블릭 라우트 테이블
- 프라이빗 서브넷 2개 (AZ a/b, 외부 차단)

## 폴더 구조
```
d2/
├── main.tf            # provider(LocalStack) + 모듈 호출
├── variables.tf       # 루트 입력 변수
├── locals.tf          # name_prefix, 공통 태그
├── outputs.tf         # 루트 출력
├── terraform.tfvars   # 변수 실제 값
└── modules/vpc/       # 재사용 VPC 모듈
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## 실행 (LocalStack 필요)
```bash
# 1) LocalStack 기동 (별도 터미널)
localstack start -d            # 또는 docker run ... localstack/localstack

# 2) d2 폴더에서
cd terraform/d2
terraform init                 # 모듈·프로바이더 초기화
terraform validate             # 문법/타입 검증
terraform plan                 # 생성 계획 미리보기 (영수증)
terraform apply -auto-approve  # 실제 생성

# 3) 확인
terraform output               # vpc_id, 서브넷 ID, summary 출력
awslocal ec2 describe-vpcs     # LocalStack에 실제로 생겼는지 교차확인

# 4) 정리
terraform destroy -auto-approve
```

## 직접 해볼 것 (응용)
- `environment = "prod"`로 바꿔 이름 접두사가 어떻게 변하는지 plan으로 확인
- `public_subnets`에 `public-c` 한 줄 추가 → for_each가 서브넷만 1개 더 늘리는지 확인
- 프라이빗 서브넷용 라우트 테이블을 별도로 추가해보기
