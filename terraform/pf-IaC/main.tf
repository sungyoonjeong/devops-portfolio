# =============================================================================
# devops-portfolio/terraform/pf-IaC/main.tf — 실 AWS에 EC2 1대 프로비저닝 (Ansible 연동 대상)
# D1~D5(LocalStack)와의 차이: provider에 우회 설정 없음, 진짜 AMI/키페어 사용,
# VPC 안 만들고 계정 기본 VPC 사용.
# =============================================================================

terraform {                   # Terraform 자체/프로바이더 요구사항 선언
  required_version = ">= 1.5" # 이 버전 이상의 terraform CLI 필요
  required_providers {
    aws = {                     # AWS 프로바이더 사용
      source  = "hashicorp/aws" # 레지스트리 출처
      version = "~> 5.0"        # 5.x 대 허용 (6.0 미만)
    }
  }
}

# ---- Provider: 실 AWS. region 한 줄이 전부 ----------------------------------
provider "aws" {
  region = "ap-northeast-2" # 서울 리전. 자격증명은 ~/.aws/credentials 를 자동으로 읽음
}                           # (LocalStack 때 쓰던 access_key="test"·skip_*·endpoints 전부 불필요)

# ---- 키페어: 내 WSL 공개키를 AWS에 등록 -------------------------------------
resource "aws_key_pair" "main" {
  key_name   = "pf-iac-key"                  # AWS 콘솔에 표시될 키 이름
  public_key = file("~/.ssh/id_ed25519.pub") # 로컬 공개키 파일을 읽어서 등록.
}                                            # 개인키는 절대 AWS로 안 감 — 공개키만 올리고
                                             # SSH 접속 때 로컬 개인키로 증명하는 구조

# ---- AMI 조회: Ubuntu 22.04 최신 이미지를 이름 패턴으로 찾음 ----------------
data "aws_ami" "ubuntu" {      # data = 만드는 게 아니라 "조회". 이미 존재하는 것을 읽어옴
  most_recent = true           # 패턴에 걸리는 것 중 가장 최신 1개 선택
  owners      = ["099720109477"] # Canonical(우분투 제작사)의 AWS 계정 ID — 위조 AMI 방지

  filter {
    name   = "name"                                                    # AMI 이름 기준 필터
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"] # jammy=22.04, *=날짜별 빌드
  }
}

# ---- 보안그룹: SSH(22)·HTTP(80) 인바운드 + 아웃바운드 전체 ------------------
resource "aws_security_group" "web" {
  name        = "pf-iac-web" # 그룹 이름 (기본 VPC 안에 생성됨)
  description = "SSH + HTTP" # 콘솔에서 보이는 설명

  ingress {                       # 인바운드 규칙 1: SSH
    from_port   = 22              # 포트 범위 시작
    to_port     = 22              # 포트 범위 끝 (22 하나면 시작=끝)
    protocol    = "tcp"           # SSH는 TCP
    cidr_blocks = ["0.0.0.0/0"]   # 전 세계 허용 — 실습용. 실무는 내IP/32
  }

  ingress {                       # 인바운드 규칙 2: HTTP (nginx 확인용)
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]   # 웹은 원래 전체 공개가 정상
  }

  egress {                        # 아웃바운드: 나가는 트래픽 전체 허용
    from_port   = 0               # 0 = 전체 포트
    to_port     = 0
    protocol    = "-1"            # -1 = 모든 프로토콜 (tcp/udp/icmp 전부)
    cidr_blocks = ["0.0.0.0/0"]   # apt 패키지 다운로드 등 외부 통신에 필요
  }
}

# ---- EC2 인스턴스 -----------------------------------------------------------
resource "aws_instance" "web" {
  ami                    = data.aws_ami.ubuntu.id        # 위에서 조회한 AMI의 ID 참조
  instance_type          = "t3.micro"                    # 프리티어 대상 타입
  key_name               = aws_key_pair.main.key_name    # 위 키페어 참조 → SSH 로그인용
  vpc_security_group_ids = [aws_security_group.web.id]   # SG 참조 (리스트 형태 주의).
                                                         # 참조 덕에 Terraform이 SG→EC2 순서 보장

  tags = { Name = "pf-iac-web" } # 콘솔 목록에서 식별할 이름표
}

# ---- Output: apply 끝나면 접속 주소를 바로 보여줌 ---------------------------
output "public_ip" {
  value = aws_instance.web.public_ip # ssh ubuntu@<이 값>, 브라우저 http://<이 값>
}
