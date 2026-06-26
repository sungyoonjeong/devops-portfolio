# =============================================================================
# d4/modules/iam/main.tf  —  EC2 용 IAM Role + Policy + Instance Profile (D4 신규)
# 흐름(개념서 11.3): Role(역할 정의) → Policy(권한 내용) → Instance Profile(EC2 부착 고리).
# 이렇게 하면 EC2 안에 액세스키를 박지 않고도 S3 를 읽을 수 있다(키리스, 더 안전).
# =============================================================================

# ---- ① IAM Role: "EC2 서비스가 이 역할을 맡을 수 있다"(신뢰 정책) -----------
resource "aws_iam_role" "ec2_role" {
  name = "${var.name_prefix}-ec2-role"

  assume_role_policy = jsonencode({ # 누가 이 역할을 가정(assume)할 수 있는지
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" } # ★ EC2 서비스에게 허용
      Action    = "sts:AssumeRole"
    }]
  })

  tags = var.common_tags
}

# ---- ② IAM Policy: 그 역할이 "무엇을 할 수 있나"(S3 읽기) -------------------
resource "aws_iam_role_policy" "s3_read" {
  name = "s3-read-policy"
  role = aws_iam_role.ec2_role.id # 위 역할에 인라인으로 붙임

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [ # 최소 권한: 읽기 관련 액션만 (와일드카드 * 남발 금지)
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [                # 대상: 루트가 넘겨준 앱 버킷과 그 안의 객체
        var.app_bucket_arn,       # 버킷 자체 (ListBucket 용)
        "${var.app_bucket_arn}/*" # 버킷 안 모든 객체 (GetObject 용)
      ]
    }]
  })
}

# ---- ③ Instance Profile: Role 을 EC2 에 붙이기 위한 연결 고리 ---------------
resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2_role.name # 이 프로파일을 ec2 모듈이 인스턴스에 부착
}
