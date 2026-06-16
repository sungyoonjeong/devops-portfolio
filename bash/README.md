# Bash 스크립팅

> 14챕터 + 실습 스크립트 학습 정리

## 커버 범위

| 챕터 | 내용 |
|------|------|
| ch01~03 | 변수·조건문·반복문 기초 |
| ch04~06 | 함수·배열·문자열 처리 |
| ch07~09 | 파일 처리·정규식·grep/sed/awk |
| ch10~11 | 프로세스 관리·시그널·trap |
| ch12~13 | 파이프·리다이렉션·heredoc |
| ch14 | 종합 실습 (CPU·메모리·디스크 수집 스크립트) |

## 구조

```
bash/
└── bash-practice/    bash_guide.md + ch01~14 실습 스크립트
```

## DevOps 활용

PF2의 `deploy.sh` (빌드→ECR→헬스체크 자동화) 직접 활용.  
PF3 `monitor.sh`·`cleanup.sh` 구현에 활용.
