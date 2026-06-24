# =============================================================================
# outputs.tf (루트 모듈)
# 모듈이 돌려준 값을 다시 최상위 출력으로 노출 → apply 후 터미널에 표시되고,
# 다른 도구(Ansible 등)가 이 값을 읽어 쓸 수 있다.
# =============================================================================

output "vpc_id" { # 모듈 출력을 그대로 전달(pass-through)
  description = "생성된 VPC ID"
  value       = module.vpc.vpc_id # module.<이름>.<출력명> 으로 모듈 출력 참조
}

output "public_subnet_ids" { # 퍼블릭 서브넷 ID 목록
  description = "퍼블릭 서브넷 ID 리스트"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" { # 프라이빗 서브넷 ID 목록
  description = "프라이빗 서브넷 ID 리스트"
  value       = module.vpc.private_subnet_ids
}

output "summary" { # 사람이 읽기 좋은 요약 한 줄 (문자열 보간 예시)
  description = "VPC 구성 요약"
  value       = "VPC ${module.vpc.vpc_id} (${module.vpc.vpc_cidr}) — 퍼블릭 ${length(module.vpc.public_subnet_ids)}개 / 프라이빗 ${length(module.vpc.private_subnet_ids)}개"
}
