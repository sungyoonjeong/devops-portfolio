# =============================================================================
# d3/variables.tf  —  루트 입력 변수 선언
# =============================================================================

variable "aws_region" {
  description = "리소스를 만들 AWS 리전"
  type        = string
  default     = "us-east-1" # LocalStack 기본 리전
}

variable "project" {
  description = "이름 접두사로 쓸 프로젝트명"
  type        = string
  default     = "portfolio"
}

variable "ami_id" {
  description = "EC2 인스턴스에 쓸 AMI ID"
  type        = string
  # LocalStack 은 아무 AMI 나 받지 않고, 자체 내장한 "모의 AMI 목록"의 ID 만 허용한다.
  # ami-760aaa0f = LocalStack 기본 Amazon Linux AMI (awslocal ec2 describe-images 로 확인 가능).
  # 실제 AWS 라면 이렇게 하드코딩하지 말고 data.aws_ami 로 최신 AMI 를 동적 조회하는 게 정석.
  default = "ami-760aaa0f"
}
