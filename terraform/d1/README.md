# Terraform D1 실습 — HCL 기초 + LocalStack S3

Terraform 의 가장 기본 흐름을 익힌다: **provider 설정 → 리소스 생성 →
리소스 간 참조 → output**. 실제 AWS 대신 LocalStack(로컬 모의 AWS)에 올린다.

## 학습 포인트
- `terraform { required_providers }` 와 `provider` 블록의 역할
- LocalStack 으로 향하게 하는 provider 설정(`endpoints`, `s3_use_path_style`)
- `resource` 블록 문법: `resource "타입" "로컬이름" { ... }`
- 한 리소스가 다른 리소스를 `aws_s3_bucket.practice.id` 로 참조 → **암묵적 의존성**
- `output` 으로 값 노출

> D1 은 값을 전부 하드코딩한다. 변수·로컬·모듈로 추상화하는 것은 D2(`../d2`)에서 배운다.

## 만들어지는 리소스
- S3 버킷 1개 (`terraform-practice-bucket`)
- 그 버킷의 버전 관리(versioning) 활성화

## 실행 (LocalStack 필요)
```bash
localstack start -d            # LocalStack 기동(별도 터미널)

cd terraform/d1
terraform init                 # 프로바이더 다운로드 + 초기화
terraform validate             # 문법/타입 검증
terraform plan                 # 생성 계획 미리보기
terraform apply -auto-approve  # 실제 생성

terraform output               # bucket_name, versioning_status 확인
awslocal s3 ls                 # LocalStack 에 버킷이 실제로 생겼는지 교차확인

terraform destroy -auto-approve  # 정리
```

## 직접 해볼 것
- 버킷 `tags` 에 한 줄 추가 후 `plan` 으로 "변경 1건"이 어떻게 보이는지 확인
- `versioning` 의 status 를 `Suspended` 로 바꿔 plan 차이 관찰
