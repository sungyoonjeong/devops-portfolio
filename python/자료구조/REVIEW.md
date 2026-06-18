# 신찬수 알고리즘 55강 — 종합 정리

> 기반: `python/자료구조/` 강의노트 1~41 + 42~55강 내용  
> 목적: 코딩테스트·기술면접 즉시 참조 레퍼런스  
> 완료일: 2026-06-18

---

## 목차

1. [기초 개념](#1-기초-개념)
2. [선형 자료구조](#2-선형-자료구조)
3. [해시 테이블](#3-해시-테이블)
4. [트리](#4-트리)
5. [균형 트리](#5-균형-트리)
6. [집합 자료구조](#6-집합-자료구조)
7. [그래프·최단경로](#7-그래프최단경로)
8. [정렬](#8-정렬)
9. [이진 인덱스 트리 (BIT)](#9-이진-인덱스-트리-bit)
10. [분할정복](#10-분할정복)
11. [동적 프로그래밍 (DP)](#11-동적-프로그래밍-dp)
12. [그리디 알고리즘](#12-그리디-알고리즘)
13. [백트래킹](#13-백트래킹)
14. [Python 내부 구현](#14-python-내부-구현)
15. [시간복잡도 총정리](#15-시간복잡도-총정리)

---

## 1. 기초 개념

### 자료구조와 알고리즘 (강의 1)
- **자료**: 저장공간(memory) + 연산(읽기·쓰기·삽입·삭제·탐색)
- **자료구조**: 저장 방식 + 연산의 조합
- **알고리즘**: 데이터 입력 → 유한 횟수의 연산 → 정답 출력

### 시간복잡도 (강의 2~4)

| Big-O | 이름 | 대표 예시 |
|-------|------|-----------|
| O(1) | 상수 | 해시 탐색, 배열 인덱스 접근 |
| O(log n) | 로그 | 이진탐색, AVL/힙 연산 |
| O(n) | 선형 | 배열 순회, BFS/DFS |
| O(n log n) | 선형로그 | 병합정렬, 힙정렬, 다익스트라 |
| O(n²) | 이차 | 버블·선택·삽입 정렬 |
| O(2ⁿ) | 지수 | 피보나치(순수재귀), 부분집합 |

**점화식 마스터 정리** T(n) = aT(n/b) + f(n):
- f(n) = O(n^(log_b a − ε)) → T(n) = Θ(n^(log_b a))
- f(n) = Θ(n^(log_b a)) → T(n) = Θ(n^(log_b a) · log n)
- f(n) = Ω(n^(log_b a + ε)) → T(n) = Θ(f(n))

---

## 2. 선형 자료구조

### 배열·리스트 (강의 5)

| 연산 | 배열(정적) | Python list(동적) |
|------|-----------|------------------|
| 인덱스 접근 | O(1) | O(1) |
| 탐색 | O(n) | O(n) |
| 끝 삽입/삭제 | — | O(1) 분할상환 |
| 중간 삽입/삭제 | O(n) | O(n) |

### 스택 (강의 6~7)
LIFO — push/pop/peek 모두 O(1)

```python
stack = []
stack.append(x)   # push
stack.pop()       # pop
stack[-1]         # peek
```

**활용**: 괄호 검사, DFS 반복 구현, 단조스택(히스토그램 최대 직사각형), 함수 호출 스택

### 큐 (강의 8)
FIFO — enqueue/dequeue 모두 O(1)

```python
from collections import deque
q = deque()
q.append(x)    # enqueue
q.popleft()    # dequeue — list.pop(0)은 O(n)이므로 deque 필수
```

**활용**: BFS, 프로세스 스케줄링, 슬라이딩 윈도우 최솟값(deque 단조큐)

### 연결리스트 (강의 9~13)

| 연산 | 단순(한방향) | 양방향 |
|------|------------|--------|
| 헤드 삽입/삭제 | O(1) | O(1) |
| 임의 삽입(노드 주소 앎) | O(1) | O(1) |
| 탐색 | O(n) | O(n) |
| 인덱스 접근 | O(n) | O(n) |

- **splice 연산**: 양방향 연결리스트에서 노드 그룹을 O(1)로 다른 위치로 이동
- Python `collections.deque` 내부 구현이 양방향 연결리스트

---

## 3. 해시 테이블

### 개념 (강의 14)
키(Key) → 해시함수 → 인덱스 → 값(Value)  
평균 탐색·삽입·삭제: **O(1)** / 최악(모든 충돌): O(n)

### 충돌 해결 (강의 15~16)

**Open Addressing**:
- Linear Probing: 다음 빈 슬롯 순서대로
- Quadratic Probing: +1², +2², +3²...
- Double Hashing: 두 번째 해시함수로 점프 크기 결정

**Separate Chaining**: 각 슬롯에 연결리스트 — 구현 단순, 캐시 불리

**성능**: 적재율(load factor) α = n/m 낮게 유지해야 O(1) 보장  
- Open Addressing: α < 0.7 권장  
- Chaining: α < 1.0 수준에서도 동작하나 성능 저하

---

## 4. 트리

### 트리 기본 (강의 17)
- 용어: 루트·부모·자식·잎·높이(h)·깊이·레벨
- **이진트리**: 각 노드 자식 ≤ 2

### 순회 4가지
```python
def preorder(node):    # 전위: 루트→왼→오 (트리 복사·직렬화)
    if not node: return
    visit(node)
    preorder(node.left)
    preorder(node.right)

def inorder(node):     # 중위: 왼→루트→오 (BST 정렬 출력)
    if not node: return
    inorder(node.left)
    visit(node)
    inorder(node.right)

def postorder(node):   # 후위: 왼→오→루트 (트리 삭제·자식 먼저)
    if not node: return
    postorder(node.left)
    postorder(node.right)
    visit(node)
```
레벨순서(BFS): deque로 너비 우선 순회

### 힙 (강의 18~20)
완전이진트리 + 힙 성질 (최대힙: 부모 ≥ 자식)  
**배열 인덱스**: 노드 k → 부모 k//2, 왼쪽 자식 2k, 오른쪽 2k+1

| 연산 | 시간 |
|------|------|
| insert | O(log n) |
| delete_max | O(log n) |
| find_max | O(1) |
| make_heap (배열→힙) | **O(n)** |

```python
import heapq        # Python 기본: 최소 힙
h = []
heapq.heappush(h, x)
heapq.heappop(h)
heapq.heapify(lst)  # O(n)
# 최대 힙: 음수로 변환해서 사용 → heappush(h, -x)
```

### 이진탐색트리 BST (강의 21~22)
왼쪽 서브트리 < 루트 < 오른쪽 서브트리

| 연산 | 평균 | 최악(편향 트리) |
|------|------|---------------|
| 탐색·삽입·삭제 | O(log n) | O(n) |

삭제 시 후계자(successor) = 오른쪽 서브트리의 최솟값으로 대체

---

## 5. 균형 트리

### AVL 트리 (강의 23~26)
균형인수 BF = 왼쪽 높이 − 오른쪽 높이 ∈ {−1, 0, 1} 항상 유지

4가지 회전:
- LL 불균형 → 오른쪽 회전
- RR 불균형 → 왼쪽 회전
- LR 불균형 → 왼쪽 회전 후 오른쪽 회전
- RL 불균형 → 오른쪽 회전 후 왼쪽 회전

**탐색·삽입·삭제 항상 O(log n)** — 높이 ≤ 1.44 log n 보장

### Red-Black 트리 (강의 27~28)
5가지 성질:
1. 모든 노드는 빨강 또는 검정
2. 루트는 검정
3. 잎(NIL)은 검정
4. 빨강 노드의 자식은 모두 검정 (빨강 연속 불가)
5. 루트에서 각 잎까지 경로의 검정 노드 수 동일

- 높이 ≤ 2 log(n+1) 보장 → 탐색·삽입·삭제 O(log n)
- 삽입 후: Recoloring + Rotation으로 복구

| 비교 | Red-Black | AVL |
|------|-----------|-----|
| 탐색 | O(log n) | O(log n) (약간 빠름) |
| 삽입/삭제 | O(log n) (약간 빠름, 회전 적음) | O(log n) |
| 용도 | 삽입/삭제 빈번 | 탐색 빈번 |

Python `sortedcontainers.SortedList`, Java `TreeMap`이 내부적으로 사용

### 2-3-4 트리 (강의 29)
- 각 노드: 키 1~3개, 자식 2~4개
- 항상 완벽히 균형 (모든 잎이 동일 레벨)
- Red-Black 트리와 1:1 대응 관계 (이론적 등가)

---

## 6. 집합 자료구조

### Union-Find (강의 30)
**경로 압축 + 랭크 기반 합집합** → 실질적 O(1) (역 아커만 함수 O(α(n)))

```python
parent = list(range(n))
rank = [0] * n

def find(x):                        # 경로 압축
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(x, y):                    # 랭크 기반
    rx, ry = find(x), find(y)
    if rx == ry: return False
    if rank[rx] < rank[ry]: rx, ry = ry, rx
    parent[ry] = rx
    if rank[rx] == rank[ry]: rank[rx] += 1
    return True
```

**활용**: 크루스칼 MST, 연결 여부 판단 O(1), 사이클 감지

---

## 7. 그래프·최단경로

### 그래프 표현 (강의 31)
```python
# 인접 리스트 (V+E 공간, 일반적 권장)
graph = [[] for _ in range(n+1)]
graph[u].append((v, weight))

# 인접 행렬 (V² 공간, 밀집 그래프 or 간선 존재 여부 빠른 확인)
adj = [[0]*n for _ in range(n)]
adj[u][v] = weight
```

### BFS (강의 32)
```python
from collections import deque
def bfs(start, graph, n):
    visited = [False] * (n+1)
    dist = [-1] * (n+1)
    q = deque([start])
    visited[start] = True
    dist[start] = 0
    while q:
        v = q.popleft()
        for nv in graph[v]:
            if not visited[nv]:
                visited[nv] = True
                dist[nv] = dist[v] + 1
                q.append(nv)
    return dist
```
- 시간: O(V + E)
- **가중치 없는 그래프 최단경로**, 레벨 탐색, 최단 경로 길이

### DFS (강의 33)
```python
def dfs(v, visited, graph):
    visited[v] = True
    for nv in graph[v]:
        if not visited[nv]:
            dfs(nv, visited, graph)
```
- 시간: O(V + E)
- **연결 요소 수**, 사이클 감지, 위상 정렬, 백트래킹 기반

### 다익스트라 (강의 34)
음수 가중치 없는 그래프의 단일 출발 최단경로

```python
import heapq
def dijkstra(start, graph, n):
    INF = float('inf')
    dist = [INF] * (n+1)
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, v = heapq.heappop(pq)
        if d > dist[v]: continue    # 이미 처리된 노드 스킵
        for nv, w in graph[v]:
            if dist[v] + w < dist[nv]:
                dist[nv] = dist[v] + w
                heapq.heappush(pq, (dist[nv], nv))
    return dist
```
시간: O((V + E) log V)

### 벨만-포드 (강의 34)
음수 가중치 허용, 음수 사이클 감지 가능

```python
def bellman_ford(start, edges, n):
    INF = float('inf')
    dist = [INF] * (n+1)
    dist[start] = 0
    for _ in range(n-1):            # V-1번 반복
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    # 음수 사이클 감지
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None             # 음수 사이클 존재
    return dist
```
시간: O(VE)

### 플로이드-워셜 (강의 35)
모든 쌍 최단경로 (All-to-All)

```python
def floyd_warshall(dist, n):
    # dist[i][j] 초기화: 직접 연결 간선 or INF, dist[i][i]=0
    for k in range(1, n+1):         # 경유 노드
        for i in range(1, n+1):
            for j in range(1, n+1):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
```
시간: O(V³) / 음수 가중치 허용, 음수 사이클 있으면 dist[i][i] < 0

---

## 8. 정렬

### Tim 정렬 (강의 36~37)
Python 기본 정렬(`list.sort()`, `sorted()`)의 실제 구현  
Insertion Sort(작은 구간) + Merge Sort(병합) 결합  
- 최악: O(n log n) / 최선(거의 정렬됨): **O(n)** / Stable

### 정렬 알고리즘 비교

| 정렬 | 평균 | 최악 | 공간 | 안정? |
|------|------|------|------|-------|
| 버블 | O(n²) | O(n²) | O(1) | ✅ |
| 선택 | O(n²) | O(n²) | O(1) | ❌ |
| 삽입 | O(n²) | O(n²) | O(1) | ✅ |
| 병합(Merge) | O(n log n) | O(n log n) | O(n) | ✅ |
| 퀵(Quick) | O(n log n) | O(n²) | O(log n) | ❌ |
| 힙(Heap) | O(n log n) | O(n log n) | O(1) | ❌ |
| Tim | O(n log n) | O(n log n) | O(n) | ✅ |
| 계수(Counting) | O(n+k) | O(n+k) | O(k) | ✅ |
| 기수(Radix) | O(nk) | O(nk) | O(n+k) | ✅ |

```python
# 병합 정렬
def merge_sort(arr):
    if len(arr) <= 1: return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

# 퀵 정렬
def quick_sort(arr, lo, hi):
    if lo >= hi: return
    pivot_idx = partition(arr, lo, hi)
    quick_sort(arr, lo, pivot_idx - 1)
    quick_sort(arr, pivot_idx + 1, hi)

def partition(arr, lo, hi):
    pivot = arr[hi]
    i = lo - 1
    for j in range(lo, hi):
        if arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i+1], arr[hi] = arr[hi], arr[i+1]
    return i + 1
```

---

## 9. 이진 인덱스 트리 (BIT)

### 개념 (강의 38)
구간 합 조회 + 점 업데이트를 동시에 O(log n)  
핵심: **LSB(Least Significant Bit)** = `k & -k`

- `T[k]`: 인덱스 k에서 LSB(k)개 원소의 합 저장
- Query: k에서 LSB 빼가며 이동 (합산)
- Update: k에서 LSB 더해가며 이동 (갱신)

```python
class BIT:
    def __init__(self, n):
        self.n = n
        self.tree = [0] * (n + 1)

    def update(self, i, delta):     # A[i] += delta
        while i <= self.n:
            self.tree[i] += delta
            i += i & -i             # LSB 더하기

    def query(self, i):             # sum(A[1..i])
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & -i             # LSB 빼기
        return s

    def range_query(self, l, r):    # sum(A[l..r])
        return self.query(r) - self.query(l - 1)
```

| 연산 | 단순배열 | 합배열(Prefix) | BIT |
|------|---------|--------------|-----|
| 구간합 조회 | O(n) | O(1) | O(log n) |
| 점 업데이트 | O(1) | O(n) | O(log n) |

→ **업데이트가 빈번한 구간합 문제**에서 BIT가 최적

### 순열 복원 문제 (강의 39)
BIT + 이진탐색으로 O(n log² n) → O(n log n) 해결  
핵심: "사용 가능한 k번째 수 찾기"를 BIT 구간합으로 빠르게 처리

---

## 10. 분할정복

### 개념 (강의 42~43)
1. **Divide**: 문제를 동일한 구조의 부분 문제로 분할
2. **Conquer**: 부분 문제를 재귀 해결
3. **Combine**: 부분 해를 합쳐 전체 해 도출

### 이진 탐색 (Binary Search)
```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if arr[mid] == target: return mid
        elif arr[mid] < target: lo = mid + 1
        else: hi = mid - 1
    return -1   # O(log n), 정렬된 배열 전제

# 조건 만족하는 최솟값/최댓값 탐색 패턴
lo, hi = 범위_최솟값, 범위_최댓값
while lo < hi:
    mid = (lo + hi) // 2
    if check(mid): hi = mid      # 최솟값 탐색
    else: lo = mid + 1
```

### 빠른 거듭제곱 (분할정복 응용)
```python
def fast_pow(base, exp, mod):   # O(log exp)
    result = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            result = result * base % mod
        base = base * base % mod
        exp //= 2
    return result
```

---

## 11. 동적 프로그래밍 (DP)

### 핵심 개념 (강의 44~49)
- **최적 부분구조**: 전체 최적해가 부분 문제 최적해로 구성
- **중복 부분 문제**: 같은 부분 문제가 반복 등장
- **메모이제이션** (Top-Down, 재귀+캐시) vs **타뷸레이션** (Bottom-Up, 반복)

### 대표 패턴

**피보나치 (DP 입문)**:
```python
dp = [0] * (n+1)
dp[1] = 1
for i in range(2, n+1):
    dp[i] = dp[i-1] + dp[i-2]   # O(n)
```

**배낭 문제 (0/1 Knapsack)**:
```python
# dp[w] = 용량 w일 때 최대 가치
dp = [0] * (capacity + 1)
for i in range(n):
    for w in range(capacity, weight[i]-1, -1):  # 역순 (같은 아이템 중복 방지)
        dp[w] = max(dp[w], dp[w - weight[i]] + value[i])
```

**최장 공통 부분수열 (LCS)**:
```python
# dp[i][j] = A[:i], B[:j]의 LCS 길이
dp = [[0]*(len(B)+1) for _ in range(len(A)+1)]
for i in range(1, len(A)+1):
    for j in range(1, len(B)+1):
        if A[i-1] == B[j-1]:
            dp[i][j] = dp[i-1][j-1] + 1
        else:
            dp[i][j] = max(dp[i-1][j], dp[i][j-1])
# 결과: dp[len(A)][len(B)]
```

**최장 증가 부분수열 (LIS) — O(n log n)**:
```python
import bisect
def lis_length(arr):
    tails = []
    for x in arr:
        pos = bisect.bisect_left(tails, x)
        if pos == len(tails): tails.append(x)
        else: tails[pos] = x
    return len(tails)   # tails 자체는 실제 LIS 아님, 길이만 정확
```

**동전 문제 (최소 동전 수)**:
```python
dp = [float('inf')] * (amount + 1)
dp[0] = 0
for coin in coins:
    for i in range(coin, amount+1):
        dp[i] = min(dp[i], dp[i-coin] + 1)
```

---

## 12. 그리디 알고리즘

### 개념 (강의 50~51)
매 선택마다 현재 최선 → 전체 최선이 되는 경우  
**탐욕 선택 속성** + **최적 부분구조** 두 조건이 성립해야 최적해 보장  
DP로 풀 수 있는 문제를 더 빠르게 해결

### 대표 패턴

**활동 선택 (Interval Scheduling)**:
```python
# 종료 시간 오름차순 정렬 → 끝나는 게 빠른 것 우선 선택
activities.sort(key=lambda x: x[1])
last_end, count = -1, 0
for start, end in activities:
    if start >= last_end:
        count += 1
        last_end = end
```

**회의실 배정 / 구간 최소 중첩**: 같은 패턴 변형

**크루스칼 MST (Minimum Spanning Tree)**:
```python
edges.sort(key=lambda x: x[2])   # 가중치 오름차순
mst_cost = 0
for u, v, w in edges:
    if find(u) != find(v):        # 같은 집합이면 사이클
        union(u, v)
        mst_cost += w
```
시간: O(E log E)

**프림 MST** (밀집 그래프에 유리):
```python
import heapq
def prim(start, graph, n):
    visited = [False] * (n+1)
    pq = [(0, start)]
    total = 0
    while pq:
        w, v = heapq.heappop(pq)
        if visited[v]: continue
        visited[v] = True
        total += w
        for nv, nw in graph[v]:
            if not visited[nv]:
                heapq.heappush(pq, (nw, nv))
    return total
```

---

## 13. 백트래킹

### 개념 (강의 52~53)
DFS + **가지치기(Pruning)**: 조건 불만족 시 조기 종료  
완전탐색(O(n!))보다 실용적 — 평균 탐색 공간 대폭 감소

### 대표 패턴

**순열 생성**:
```python
def permutations(arr):
    result = []
    def bt(path, used):
        if len(path) == len(arr):
            result.append(path[:])
            return
        for i in range(len(arr)):
            if not used[i]:
                used[i] = True
                path.append(arr[i])
                bt(path, used)
                path.pop()
                used[i] = False
    bt([], [False]*len(arr))
    return result
```

**조합 생성**:
```python
def combinations(arr, k):
    result = []
    def bt(start, path):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, len(arr)):
            path.append(arr[i])
            bt(i+1, path)
            path.pop()
    bt(0, [])
    return result
```

**N-Queens**:
```python
def n_queens(n):
    cols = set()
    diag1 = set()   # 우하향 대각선 (row-col 일정)
    diag2 = set()   # 우상향 대각선 (row+col 일정)
    count = [0]
    def bt(row):
        if row == n:
            count[0] += 1
            return
        for col in range(n):
            if col in cols or (row-col) in diag1 or (row+col) in diag2:
                continue
            cols.add(col); diag1.add(row-col); diag2.add(row+col)
            bt(row + 1)
            cols.discard(col); diag1.discard(row-col); diag2.discard(row+col)
    bt(0)
    return count[0]
```

**부분집합**:
```python
def subsets(arr):
    result = []
    def bt(start, path):
        result.append(path[:])
        for i in range(start, len(arr)):
            path.append(arr[i])
            bt(i+1, path)
            path.pop()
    bt(0, [])
    return result
```

---

## 14. Python 내부 구현

### Python dict (강의 40)
내부: 해시테이블 (Open Addressing + perturb 무작위성)

```
다음 인덱스 = (5 * 현재 인덱스 + 1 + perturb) % 테이블크기
```
- 초기 크기: 8 슬롯
- **2/3 이상 채워지면 2배 확장** (Rehashing)
- 탐색·삽입·삭제 평균 **O(1)**, 분할상환 O(1)
- 테이블 크기는 항상 2의 거듭제곱 유지

### Python list (강의 41)
내부: 동적 배열 (포인터 배열 — 실제 데이터 아닌 객체 주소 저장)

- **약 1.125배씩** 리사이징 (공간 낭비 최소화)
- `append`: 분할상환 **O(1)**
- `a = a + [x]`: 매번 새 배열 복사 → **O(n)** → 절대 사용 금지

**리스트 생성 속도 비교** (1000개 기준):
```
list(range(1000))        # 가장 빠름 — 크기 미리 알고 한 번에 할당
[i for i in range(1000)] # 빠름 — 내부 최적화
for x: lst.append(x)    # 보통
lst = lst + [x]          # 매우 느림 — O(n²) 총합
```

---

## 15. 시간복잡도 총정리

### 자료구조별

| 자료구조 | 탐색 | 삽입 | 삭제 | 비고 |
|----------|------|------|------|------|
| 배열 | O(n) | O(n) | O(n) | 인덱스 접근 O(1) |
| 스택/큐(deque) | O(n) | O(1) | O(1) | push/pop/enqueue/dequeue |
| 해시테이블 | **O(1)** | **O(1)** | **O(1)** | 평균; 최악 O(n) |
| BST | O(h) | O(h) | O(h) | h=높이, 편향 시 O(n) |
| AVL / Red-Black | O(log n) | O(log n) | O(log n) | 항상 보장 |
| 힙 | O(1) find-max | O(log n) | O(log n) | make_heap O(n) |
| BIT (Fenwick) | O(log n) 구간합 | O(log n) | O(log n) | 구간합+점업데이트 |
| Union-Find | O(α(n))≈O(1) | O(α(n)) | — | 경로압축+랭크 |

### 알고리즘별

| 알고리즘 | 시간 | 공간 | 특징 |
|----------|------|------|------|
| 이진탐색 | O(log n) | O(1) | 정렬된 배열 전제 |
| 병합정렬 | O(n log n) | O(n) | stable, 최악 보장 |
| 퀵정렬 | O(n log n) avg | O(log n) | 최악 O(n²), 실용적 빠름 |
| 힙정렬 | O(n log n) | O(1) | 제자리 정렬, unstable |
| BFS / DFS | O(V+E) | O(V) | |
| 다익스트라 | O((V+E) log V) | O(V) | 음수 간선 불가 |
| 벨만-포드 | O(VE) | O(V) | 음수 간선·사이클 감지 |
| 플로이드-워셜 | O(V³) | O(V²) | 전체 쌍 최단경로 |
| 크루스칼 MST | O(E log E) | O(V) | Union-Find 병용 |
| DP LCS | O(mn) | O(mn) | 2차원 DP |
| DP LIS | O(n log n) | O(n) | bisect + 이진탐색 |
| 백트래킹 | O(n!) 최악 | O(n) | 가지치기로 실용적 단축 |
