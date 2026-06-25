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
  # LocalStack(커뮤니티)은 EC2 를 모킹하므로 실제 존재하지 않는 가짜 AMI 도 허용한다.
  # 실제 AWS 라면 data.aws_ami 로 최신 AMI 를 동적 조회하는 게 정석.
  default = "ami-0c55b159cbfafe1f0"
}
