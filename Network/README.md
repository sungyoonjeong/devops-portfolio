# 네트워크 이론

> 이석복 교수 KOCW 23강 기반 학습 정리  
> 실습 프로젝트 포함

## 커버 범위

| 챕터 | 주제 |
|------|------|
| 1 | Introduction (인터넷 구조, 지연·손실·처리량) |
| 2 | Application Layer (HTTP·DNS·SMTP·P2P) |
| 3 | Transport Layer (TCP·UDP·3-way handshake·혼잡제어) |
| 4 | Network Layer (IP·라우팅·OSPF·BGP) |
| 5 | Link Layer (MAC·ARP·이더넷·스위치) |
| 6 | 무선 네트워크 (802.11·CDMA) |
| 7 | 멀티미디어 네트워크 (스트리밍·CDN) |
| 8 | 네트워크 보안 (SSL/TLS·방화벽·IDS) |

## 구조

```
Network/
├── 기초이론/     이석복 교수 강의 정리 (챕터별 .md)
├── 실습/         실습 정리
└── network-project1/  소켓 프로그래밍 실습 (C + Python)
```

## DevOps 연결

TCP 3-way handshake → 로드밸런서 헬스체크 원리.  
DNS → K8s 서비스 디스커버리 (CoreDNS).  
TLS → Ingress SSL 인증서 설정.  
방화벽·IDS → AWS Security Group·NACL·NetworkPolicy.
