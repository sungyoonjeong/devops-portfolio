# =============================================================================
# d4/modules/ec2/main.tf  —  EC2 인스턴스 모듈 (D4 신규, 모든 조각의 종착점)
# 앞선 세 모듈의 산출물을 한 인스턴스에 연결한다:
#   subnet_id(vpc) + vpc_security_group_ids(security_groups) + iam_instance_profile(iam)
# =============================================================================

resource "aws_instance" "web" {
  ami                    = var.ami_id           # AMI (LocalStack 내장 ami-760aaa0f)
  instance_type          = var.instance_type    # 환경별 타입 (루트 locals 에서 계산)
  subnet_id              = var.subnet_id        # ★ vpc 모듈의 퍼블릭 서브넷
  vpc_security_group_ids = [var.web_sg_id]      # ★ security_groups 모듈의 web SG
  iam_instance_profile   = var.instance_profile # ★ iam 모듈의 인스턴스 프로파일

  # 부팅 시 실행 스크립트 (docker 설치 예시) — 개념서 11.4
  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
  EOF

  root_block_device {   # 루트 디스크 설정
    volume_size = 20    # 20GB
    volume_type = "gp3" # gp3 (최신 범용 SSD)
    encrypted   = true  # 디스크 암호화 (보안 베스트프랙티스)
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-web" })

  lifecycle {
    create_before_destroy = true # 교체 시 새것 먼저 만들고 기존 삭제 → 다운타임 최소화
  }
}
