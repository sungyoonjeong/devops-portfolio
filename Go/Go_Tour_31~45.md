# 🐹 Go 언어 완전 입문서 — 챕터 31~45
> 배열·슬라이스·Range·맵 완전 정리  
> DevOps에서 가장 많이 쓰는 자료구조들

---

## 목차
31. [Arrays (배열)](#31-arrays-배열)
32. [Slices (슬라이스) 기초](#32-slices-슬라이스-기초)
33. [슬라이스는 배열의 참조](#33-슬라이스는-배열의-참조)
34. [Slice Literals](#34-slice-literals)
35. [Slice Defaults (기본값)](#35-slice-defaults-기본값)
36. [Slice Length & Capacity](#36-slice-length--capacity)
37. [Nil Slices](#37-nil-slices)
38. [make로 슬라이스 생성](#38-make로-슬라이스-생성)
39. [Slices of Slices (2차원)](#39-slices-of-slices-2차원)
40. [append로 슬라이스 추가](#40-append로-슬라이스-추가)
41. [Range 기본](#41-range-기본)
42. [Range 심화](#42-range-심화)
43. [Maps (맵) 기초](#43-maps-맵-기초)
44. [Map Literals](#44-map-literals)
45. [Maps 조작 (추가·수정·삭제·확인)](#45-maps-조작-추가수정삭제확인)
- [실전 종합 코드](#실전-종합-코드)
- [자주 하는 실수](#자주-하는-실수)

---

## 31. Arrays (배열)

### 배열이란?
**같은 타입**의 값을 **고정된 개수**만큼 저장하는 자료구조입니다.

```go
// 선언 방법
var a [5]int         // int 5개짜리 배열 (zero value로 초기화)
b := [3]string{"Go", "Python", "Bash"}  // 초기값 지정
```

### 선언 문법

```go
var 변수명 [크기]타입
```

```go
var nums [5]int          // [0 0 0 0 0]
var names [3]string      // ["" "" ""]
var flags [2]bool        // [false false]
```

### 인덱스로 접근 (0부터 시작)

```go
a := [5]int{10, 20, 30, 40, 50}

fmt.Println(a[0])   // 10 (첫번째)
fmt.Println(a[4])   // 50 (마지막)
fmt.Println(a[2])   // 30 (중간)

a[0] = 100           // 값 변경
fmt.Println(a)       // [100 20 30 40 50]
```

### 배열 길이: len()

```go
a := [5]int{1, 2, 3, 4, 5}
fmt.Println(len(a))   // 5
```

### ... 으로 크기 자동 설정

```go
a := [...]int{1, 2, 3, 4, 5}  // 크기를 직접 세지 않아도 됨
fmt.Println(len(a))             // 5
```

### Python 리스트와 비교

```python
# Python 리스트: 크기 제한 없음, 타입 혼합 가능
a = [1, 2, 3, "hello", True]  # OK
a.append(4)                    # 크기 동적으로 변경 가능
```

```go
// Go 배열: 크기 고정, 같은 타입만
a := [3]int{1, 2, 3}  // 딱 3개, int만
// a[3] = 4  → 에러! 인덱스 범위 초과
// a = append(a, 4)  → 에러! 배열은 크기 변경 불가
```

### ★ Go에서 배열은 거의 안 씀

```
배열의 문제: 크기가 고정 → 유연하지 않음
해결책: 슬라이스(Slice) 사용 → 크기 동적 변경 가능
실무에서 배열 직접 쓰는 경우는 거의 없음
슬라이스를 압도적으로 많이 씀
```

---

## 32. Slices (슬라이스) 기초

### 슬라이스란?
배열과 비슷하지만 **크기가 동적으로 변하는** 자료구조입니다.  
Go에서 가장 많이 쓰는 자료구조입니다.

```go
// 선언 방법 ([] 안에 크기 없음 = 슬라이스)
var s []int                    // nil 슬라이스
s2 := []int{1, 2, 3, 4, 5}   // 초기값 있는 슬라이스
```

### 배열 vs 슬라이스 선언 차이

```go
// 배열: [] 안에 숫자 있음
a := [5]int{1, 2, 3, 4, 5}   // 배열 (크기 고정)

// 슬라이스: [] 안이 비어있음
s := []int{1, 2, 3, 4, 5}    // 슬라이스 (크기 동적)
```

### 배열에서 슬라이스 만들기

```go
a := [6]int{1, 2, 3, 4, 5, 6}

// a[시작:끝] → 시작 이상, 끝 미만
s := a[1:4]   // a[1], a[2], a[3] → [2 3 4]
fmt.Println(s)   // [2 3 4]
```

### 슬라이싱 규칙

```go
a := [6]int{1, 2, 3, 4, 5, 6}
//          0  1  2  3  4  5  (인덱스)

s1 := a[0:3]  // [1 2 3]    (0,1,2번 인덱스)
s2 := a[2:5]  // [3 4 5]    (2,3,4번 인덱스)
s3 := a[1:4]  // [2 3 4]    (1,2,3번 인덱스)
```

```python
# Python 슬라이싱과 동일
a = [1, 2, 3, 4, 5, 6]
s1 = a[0:3]  # [1, 2, 3]
s2 = a[2:5]  # [3, 4, 5]
```

### 인덱스 접근·수정

```go
s := []int{10, 20, 30, 40, 50}

fmt.Println(s[0])   // 10
fmt.Println(s[4])   // 50

s[0] = 100
fmt.Println(s)      // [100 20 30 40 50]
```

---

## 33. 슬라이스는 배열의 참조

### ★ 매우 중요한 개념

슬라이스는 배열을 **복사하지 않고** 원본 배열을 **참조(가리킴)**합니다.

```go
a := [4]int{1, 2, 3, 4}  // 원본 배열

s := a[1:3]               // a의 1~2번 참조 → [2 3]

// 슬라이스 수정 → 원본 배열도 바뀜!
s[0] = 999
fmt.Println(s)    // [999 3]
fmt.Println(a)    // [1 999 3 4]  ← 원본도 바뀜!
```

### 메모리 구조로 이해

```
원본 배열 a:
  주소: [0x01][0x02][0x03][0x04]
  값:    [1]   [2]   [3]   [4]

슬라이스 s = a[1:3]:
  s는 0x02 주소를 가리킴 (복사 아님!)
  s[0] = 0x02 주소의 값 = 2
  s[1] = 0x03 주소의 값 = 3

s[0] = 999 하면:
  0x02 주소에 999 저장
  → a[1]도 999로 바뀜 (같은 주소니까)
```

### 여러 슬라이스가 같은 배열 참조

```go
a := [6]int{1, 2, 3, 4, 5, 6}

s1 := a[0:3]  // [1 2 3]
s2 := a[2:6]  // [3 4 5 6]

// s1을 수정하면 s2에도 영향
s1[2] = 999   // a[2]를 999로 변경
fmt.Println(s1)  // [1 2 999]
fmt.Println(s2)  // [999 4 5 6]  ← s2도 영향받음!
fmt.Println(a)   // [1 2 999 4 5 6]
```

---

## 34. Slice Literals

### 슬라이스 리터럴: 값을 직접 넣어 생성

배열처럼 보이지만 크기 지정 없음 → 자동으로 배열 생성 + 슬라이스 반환

```go
// 배열 리터럴: 크기 지정
a := [3]int{1, 2, 3}

// 슬라이스 리터럴: 크기 없음
s := []int{1, 2, 3}
```

### 다양한 타입의 슬라이스 리터럴

```go
// 정수 슬라이스
nums := []int{10, 20, 30, 40, 50}

// 문자열 슬라이스
servers := []string{"web-01", "web-02", "db-01"}

// 불리언 슬라이스
flags := []bool{true, false, true}

// 실수 슬라이스
cpus := []float64{45.5, 87.3, 23.1}
```

### 구조체 슬라이스 (★ 실무에서 자주 씀)

```go
type Server struct {
    Host string
    CPU  float64
}

servers := []Server{
    {Host: "web-01", CPU: 45.5},
    {Host: "web-02", CPU: 87.3},
    {Host: "db-01",  CPU: 23.1},
}

for _, s := range servers {
    fmt.Printf("%s: %.1f%%\n", s.Host, s.CPU)
}
```

---

## 35. Slice Defaults (기본값)

### 슬라이싱 시 시작·끝 생략 가능

```go
a := []int{1, 2, 3, 4, 5}

// 시작 생략 → 0부터
s1 := a[:3]    // a[0:3] 와 동일 → [1 2 3]

// 끝 생략 → len(a)까지
s2 := a[2:]    // a[2:5] 와 동일 → [3 4 5]

// 둘 다 생략 → 전체
s3 := a[:]     // a[0:5] 와 동일 → [1 2 3 4 5]
```

```python
# Python과 동일한 개념
a = [1, 2, 3, 4, 5]
s1 = a[:3]   # [1, 2, 3]
s2 = a[2:]   # [3, 4, 5]
s3 = a[:]    # [1, 2, 3, 4, 5]
```

### 자주 쓰는 패턴

```go
s := []int{1, 2, 3, 4, 5}

first3 := s[:3]    // 앞 3개 → [1 2 3]
last3  := s[2:]    // 뒤 3개 → [3 4 5]
copy   := s[:]     // 전체 참조
```

---

## 36. Slice Length & Capacity

### Length (길이): 현재 슬라이스에 있는 요소 수

```go
s := []int{1, 2, 3, 4, 5}
fmt.Println(len(s))   // 5
```

### Capacity (용량): 슬라이스 시작점부터 원본 배열 끝까지

```go
a := [6]int{1, 2, 3, 4, 5, 6}
s := a[2:4]   // [3 4]

fmt.Println(len(s))   // 2  (슬라이스에 있는 요소: 3, 4)
fmt.Println(cap(s))   // 4  (2번 인덱스부터 배열 끝까지: 3,4,5,6)
```

### 왜 capacity가 필요한가?

```
append()로 요소 추가 시:
  현재 용량 안이면 → 같은 배열에 추가 (빠름)
  용량 초과하면   → 새 배열 할당 + 복사 (느림, 자동 처리)

→ 성능 최적화할 때 capacity 미리 설정
```

### len vs cap

```go
a := [6]int{1, 2, 3, 4, 5, 6}

s1 := a[0:3]
fmt.Printf("len=%d cap=%d %v\n", len(s1), cap(s1), s1)
// len=3 cap=6 [1 2 3]

s2 := a[2:4]
fmt.Printf("len=%d cap=%d %v\n", len(s2), cap(s2), s2)
// len=2 cap=4 [3 4]

s3 := a[4:6]
fmt.Printf("len=%d cap=%d %v\n", len(s3), cap(s3), s3)
// len=2 cap=2 [5 6]
```

---

## 37. Nil Slices

### nil 슬라이스란?

선언만 하고 초기화하지 않은 슬라이스 = nil

```go
var s []int           // nil 슬라이스

fmt.Println(s)        // []
fmt.Println(len(s))   // 0
fmt.Println(cap(s))   // 0
fmt.Println(s == nil) // true
```

### nil 슬라이스는 안전하게 사용 가능

```go
var s []int

// append 가능
s = append(s, 1)
s = append(s, 2, 3)
fmt.Println(s)   // [1 2 3]

// range 가능 (반복 안 함)
for _, v := range s {
    fmt.Println(v)
}
```

### nil 슬라이스 vs 빈 슬라이스

```go
var s1 []int       // nil 슬라이스
s2 := []int{}      // 빈 슬라이스 (nil 아님)

fmt.Println(s1 == nil)  // true
fmt.Println(s2 == nil)  // false

// 둘 다 len=0, 사용 방식은 동일
fmt.Println(len(s1), len(s2))  // 0 0
```

---

## 38. make로 슬라이스 생성

### make 함수: 크기와 용량을 지정해서 슬라이스 생성

```go
// make([]타입, 길이)
s1 := make([]int, 5)
fmt.Println(s1)   // [0 0 0 0 0]
fmt.Println(len(s1), cap(s1))  // 5 5

// make([]타입, 길이, 용량)
s2 := make([]int, 3, 10)
fmt.Println(s2)   // [0 0 0]
fmt.Println(len(s2), cap(s2))  // 3 10
```

### 왜 make를 쓰나?

```
리터럴 방식: 초기값을 알 때
  s := []int{1, 2, 3}

make 방식: 크기만 알고 값은 나중에 채울 때
  s := make([]int, 100)  // 100개짜리 슬라이스 미리 확보
  for i := 0; i < 100; i++ {
      s[i] = i * 2
  }
```

### 성능 최적화: 용량 미리 지정

```go
// 나쁜 방법: 매번 새 배열 할당
var s []int
for i := 0; i < 1000; i++ {
    s = append(s, i)  // 용량 초과할 때마다 새 배열 생성
}

// 좋은 방법: 용량 미리 지정
s := make([]int, 0, 1000)  // 길이 0, 용량 1000
for i := 0; i < 1000; i++ {
    s = append(s, i)  // 용량 충분하므로 새 배열 안 만들어도 됨
}
```

---

## 39. Slices of Slices (2차원)

### 슬라이스 안에 슬라이스

```go
// 2차원 슬라이스
board := [][]string{
    {"X", "O", "X"},
    {"O", "X", "O"},
    {"X", "O", "X"},
}

// 접근
fmt.Println(board[0][0])   // X
fmt.Println(board[1][2])   // O

// 전체 출력
for _, row := range board {
    fmt.Println(row)
}
// [X O X]
// [O X O]
// [X O X]
```

### DevOps 실전 예시: 서버 그룹 관리

```go
// 서버를 역할별로 그룹화
serverGroups := [][]string{
    {"web-01", "web-02", "web-03"},  // 웹 서버
    {"db-01", "db-02"},              // DB 서버
    {"cache-01"},                    // 캐시 서버
}

groupNames := []string{"웹", "DB", "캐시"}

for i, group := range serverGroups {
    fmt.Printf("[%s 서버] %v\n", groupNames[i], group)
}
```

---

## 40. append로 슬라이스 추가

### append: 슬라이스에 요소 추가

```go
// append(슬라이스, 추가할값...)
s := []int{1, 2, 3}

s = append(s, 4)          // 하나 추가
fmt.Println(s)             // [1 2 3 4]

s = append(s, 5, 6, 7)    // 여러 개 추가
fmt.Println(s)             // [1 2 3 4 5 6 7]
```

### ★ 반드시 반환값을 받아야 함

```go
s := []int{1, 2, 3}

// 잘못된 방법 (반환값 무시)
append(s, 4)       // 아무 효과 없음!
fmt.Println(s)     // [1 2 3] (변화 없음)

// 올바른 방법 (반환값 받기)
s = append(s, 4)   // s에 다시 저장
fmt.Println(s)     // [1 2 3 4]
```

### 슬라이스에 슬라이스 추가: ... 사용

```go
s1 := []int{1, 2, 3}
s2 := []int{4, 5, 6}

// s2를 s1에 붙이기
s1 = append(s1, s2...)   // ... = 슬라이스를 풀어서 전달
fmt.Println(s1)           // [1 2 3 4 5 6]
```

```python
# Python 비교
s1 = [1, 2, 3]
s2 = [4, 5, 6]
s1.extend(s2)    # 또는 s1 += s2
print(s1)        # [1, 2, 3, 4, 5, 6]
```

### DevOps 실전: 동적으로 서버 목록 관리

```go
var alertServers []string  // 알림 대상 서버 목록

servers := []struct {
    Host string
    CPU  float64
}{
    {"web-01", 92.5},
    {"web-02", 45.0},
    {"db-01",  88.3},
}

for _, s := range servers {
    if s.CPU > 80 {
        alertServers = append(alertServers, s.Host)
    }
}

fmt.Println("알림 대상:", alertServers)
// 알림 대상: [web-01 db-01]
```

---

## 41. Range 기본

### range란?
슬라이스, 배열, 맵을 순회(iterate)하는 키워드입니다.

```go
// for i, v := range 슬라이스
nums := []int{10, 20, 30, 40, 50}

for i, v := range nums {
    fmt.Printf("인덱스: %d, 값: %d\n", i, v)
}
// 인덱스: 0, 값: 10
// 인덱스: 1, 값: 20
// 인덱스: 2, 값: 30
// 인덱스: 3, 값: 40
// 인덱스: 4, 값: 50
```

```python
# Python 비교
nums = [10, 20, 30, 40, 50]

for i, v in enumerate(nums):
    print(f"인덱스: {i}, 값: {v}")
```

### range의 반환값 2개: 인덱스, 값

```go
nums := []int{10, 20, 30}

// 둘 다 사용
for i, v := range nums {
    fmt.Println(i, v)
}

// 인덱스만 사용
for i := range nums {
    fmt.Println(i)
}

// 값만 사용 (인덱스 버리기)
for _, v := range nums {
    fmt.Println(v)
}
```

### 합계·평균 구하기

```go
nums := []float64{45.5, 87.3, 23.1, 62.4, 91.2}

sum := 0.0
for _, v := range nums {
    sum += v
}
avg := sum / float64(len(nums))
fmt.Printf("합계: %.1f, 평균: %.1f\n", sum, avg)
```

---

## 42. Range 심화

### range로 문자열 순회

```go
// 문자열을 range로 순회하면 rune(유니코드) 단위
for i, c := range "Hello" {
    fmt.Printf("%d: %c\n", i, c)
}
// 0: H
// 1: e
// 2: l
// 3: l
// 4: o
```

### range로 맵 순회

```go
scores := map[string]int{
    "Alice": 95,
    "Bob":   87,
    "Carol": 92,
}

for name, score := range scores {
    fmt.Printf("%s: %d점\n", name, score)
}
// 순서는 매번 다를 수 있음 (맵은 순서 없음)
```

### range + continue·break

```go
nums := []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}

// 짝수만 출력
for _, v := range nums {
    if v % 2 != 0 {
        continue  // 홀수는 건너뜀
    }
    fmt.Println(v)  // 2, 4, 6, 8, 10
}

// 5 이상이면 중단
for _, v := range nums {
    if v >= 5 {
        break  // 5 만나면 종료
    }
    fmt.Println(v)  // 1, 2, 3, 4
}
```

### range로 인덱스를 이용한 수정

```go
nums := []int{1, 2, 3, 4, 5}

// v를 수정해도 원본 안 바뀜 (v는 복사본)
for _, v := range nums {
    v = v * 2  // 원본 안 바뀜!
}
fmt.Println(nums)  // [1 2 3 4 5]

// 원본 수정하려면 인덱스 사용
for i := range nums {
    nums[i] = nums[i] * 2  // 원본 수정됨
}
fmt.Println(nums)  // [2 4 6 8 10]
```

---

## 43. Maps (맵) 기초

### 맵이란?
**키(key)와 값(value)**을 쌍으로 저장하는 자료구조입니다.  
Python의 딕셔너리와 동일한 개념입니다.

```go
// map[키타입]값타입
var m map[string]int   // nil 맵 (사용 불가)

m2 := make(map[string]int)  // 사용 가능한 빈 맵
```

### Python 딕셔너리와 비교

```python
# Python
d = {}
d["Alice"] = 95
d["Bob"] = 87
print(d["Alice"])  # 95
```

```go
// Go
m := make(map[string]int)
m["Alice"] = 95
m["Bob"] = 87
fmt.Println(m["Alice"])  // 95
```

### 맵 생성 방법

```go
// 방법 1: make 사용
m1 := make(map[string]int)

// 방법 2: 리터럴 (초기값 있을 때)
m2 := map[string]int{
    "Alice": 95,
    "Bob":   87,
}
```

### 기본 조작

```go
m := make(map[string]int)

// 추가·수정 (같은 문법)
m["Alice"] = 95
m["Bob"] = 87
m["Alice"] = 100   // Alice 값 수정

// 읽기
fmt.Println(m["Alice"])  // 100
fmt.Println(m["Carol"])  // 0 (없는 키 → zero value 반환)

// 삭제
delete(m, "Bob")
fmt.Println(m)  // map[Alice:100]

// 길이
fmt.Println(len(m))  // 1
```

---

## 44. Map Literals

### 맵 리터럴: 초기값을 직접 넣어 생성

```go
// 기본 맵 리터럴
scores := map[string]int{
    "Alice": 95,
    "Bob":   87,
    "Carol": 92,
}

// 문자열 → 문자열
capitals := map[string]string{
    "Korea":  "Seoul",
    "Japan":  "Tokyo",
    "USA":    "Washington",
}

// 문자열 → 슬라이스
serverTags := map[string][]string{
    "web-01": {"web", "nginx", "prod"},
    "db-01":  {"db", "mysql", "prod"},
}
```

### 구조체를 값으로 사용

```go
type Server struct {
    CPU    float64
    Memory float64
}

servers := map[string]Server{
    "web-01": {CPU: 45.5, Memory: 62.3},
    "db-01":  {CPU: 33.0, Memory: 87.5},
}

fmt.Println(servers["web-01"].CPU)    // 45.5
fmt.Println(servers["db-01"].Memory)  // 87.5
```

---

## 45. Maps 조작 (추가·수정·삭제·확인)

### 키 존재 확인 (★ 매우 중요)

```go
m := map[string]int{"Alice": 95, "Bob": 87}

// 없는 키 조회 → zero value 반환 (에러 없음)
score := m["Carol"]
fmt.Println(score)  // 0 (Carol은 없지만 에러 안 남)

// 키 존재 여부 확인: 두 번째 반환값 사용
score, ok := m["Alice"]
fmt.Println(score, ok)  // 95 true (있음)

score, ok = m["Carol"]
fmt.Println(score, ok)  // 0 false (없음)
```

### ok 패턴으로 안전하게 사용

```go
m := map[string]int{"Alice": 95}

// 이렇게 쓰면 됨
if score, ok := m["Alice"]; ok {
    fmt.Printf("Alice 점수: %d\n", score)
} else {
    fmt.Println("Alice 없음")
}
```

```python
# Python 비교
d = {"Alice": 95}

if "Alice" in d:
    print(f"Alice 점수: {d['Alice']}")
else:
    print("Alice 없음")

# 또는
score = d.get("Alice", 0)  # 없으면 0 반환
```

### delete로 키 삭제

```go
m := map[string]int{"Alice": 95, "Bob": 87, "Carol": 92}

delete(m, "Bob")         // Bob 삭제
fmt.Println(m)            // map[Alice:95 Carol:92]

// 없는 키 삭제해도 에러 없음
delete(m, "Dave")        // OK (아무 일도 안 일어남)
```

### 맵 전체 순회

```go
m := map[string]int{"Alice": 95, "Bob": 87, "Carol": 92}

for key, value := range m {
    fmt.Printf("%s: %d\n", key, value)
}
// 순서는 매번 다름! (맵은 순서 없음)
```

### ★ nil 맵에 쓰기 → 패닉!

```go
// 위험: nil 맵에 쓰기
var m map[string]int
m["Alice"] = 95   // 패닉! nil 맵에 쓰기 불가

// 안전: make로 초기화 후 사용
m := make(map[string]int)
m["Alice"] = 95   // OK
```

---

## 실전 종합 코드

`practice_ch31_45.go`로 저장 후 `go run practice_ch31_45.go` 실행:

```go
package main

import "fmt"

type Server struct {
    Host    string
    Port    int
    CPU     float64
    Memory  float64
    Tags    []string
}

func main() {
    // === 슬라이스 기초 ===
    fmt.Println("=== 슬라이스 ===")
    servers := []string{"web-01", "web-02", "db-01", "cache-01"}
    fmt.Println("전체:", servers)
    fmt.Println("웹서버:", servers[:2])   // [web-01 web-02]
    fmt.Println("길이:", len(servers))    // 4

    // === append ===
    fmt.Println("\n=== append ===")
    var alertList []string
    cpuData := []struct {
        Host string
        CPU  float64
    }{
        {"web-01", 92.5},
        {"web-02", 45.0},
        {"db-01", 88.3},
        {"cache-01", 12.1},
    }

    for _, s := range cpuData {
        if s.CPU > 80 {
            alertList = append(alertList, s.Host)
        }
    }
    fmt.Println("위험 서버:", alertList)  // [web-01 db-01]

    // === range ===
    fmt.Println("\n=== range ===")
    cpus := []float64{92.5, 45.0, 88.3, 12.1}
    sum := 0.0
    for _, v := range cpus {
        sum += v
    }
    avg := sum / float64(len(cpus))
    fmt.Printf("CPU 평균: %.1f%%\n", avg)

    // === map 기초 ===
    fmt.Println("\n=== map ===")
    serverStatus := map[string]string{
        "web-01":   "running",
        "web-02":   "running",
        "db-01":    "stopped",
        "cache-01": "running",
    }

    for host, status := range serverStatus {
        icon := "🟢"
        if status == "stopped" {
            icon = "🔴"
        }
        fmt.Printf("%s %s: %s\n", icon, host, status)
    }

    // === map 키 확인 ===
    fmt.Println("\n=== map 키 확인 ===")
    if status, ok := serverStatus["db-01"]; ok {
        fmt.Printf("db-01 상태: %s\n", status)
    }

    if _, ok := serverStatus["db-02"]; !ok {
        fmt.Println("db-02: 서버 없음")
    }

    // === 구조체 슬라이스 + 맵 조합 ===
    fmt.Println("\n=== 종합 예시 ===")
    serverList := []Server{
        {
            Host:   "web-01",
            Port:   8080,
            CPU:    92.5,
            Memory: 78.3,
            Tags:   []string{"web", "nginx", "prod"},
        },
        {
            Host:   "db-01",
            Port:   5432,
            CPU:    45.0,
            Memory: 87.5,
            Tags:   []string{"db", "mysql", "prod"},
        },
    }

    // 태그별 서버 분류
    tagMap := make(map[string][]string)
    for _, s := range serverList {
        for _, tag := range s.Tags {
            tagMap[tag] = append(tagMap[tag], s.Host)
        }
    }

    fmt.Println("태그별 서버:")
    for tag, hosts := range tagMap {
        fmt.Printf("  [%s]: %v\n", tag, hosts)
    }
}
```

---

## 자주 하는 실수

### 실수 1: 슬라이스 수정이 원본에 영향
```go
a := []int{1, 2, 3}
b := a          // 슬라이스 복사 (참조 복사!)
b[0] = 999
fmt.Println(a)  // [999 2 3] ← a도 바뀜!

// 진짜 복사하려면 copy() 사용
c := make([]int, len(a))
copy(c, a)
c[0] = 777
fmt.Println(a)  // [999 2 3] (a 그대로)
fmt.Println(c)  // [777 2 3]
```

### 실수 2: append 반환값 무시
```go
s := []int{1, 2, 3}
append(s, 4)      // ❌ 반환값 무시
s = append(s, 4)  // ✅ 반환값 받기
```

### 실수 3: nil 맵에 쓰기
```go
var m map[string]int
m["key"] = 1          // ❌ 패닉!

m := make(map[string]int)
m["key"] = 1          // ✅ OK
```

### 실수 4: range에서 값 수정
```go
nums := []int{1, 2, 3}
for _, v := range nums {
    v = v * 2   // ❌ v는 복사본, 원본 안 바뀜
}

for i := range nums {
    nums[i] = nums[i] * 2   // ✅ 인덱스로 원본 수정
}
```

### 실수 5: 맵 순회 순서 가정
```go
m := map[string]int{"A": 1, "B": 2, "C": 3}
for k, v := range m {
    fmt.Println(k, v)
}
// 순서가 매번 다름! 순서 보장이 필요하면 슬라이스 사용
```

---

## 챕터별 핵심 한줄 요약

| 챕터 | 핵심 |
|------|------|
| 31 | 배열 = 고정 크기, 실무에서 거의 안 씀 |
| 32 | 슬라이스 = 동적 크기, Go에서 가장 많이 씀 |
| 33 | 슬라이스는 배열 참조 → 수정하면 원본도 바뀜 |
| 34 | []타입{값...} = 슬라이스 리터럴 |
| 35 | s[:3] s[2:] s[:] = 시작·끝 생략 가능 |
| 36 | len=현재 길이, cap=최대 용량 |
| 37 | nil 슬라이스도 append·range 가능 |
| 38 | make([]타입, 길이, 용량) = 크기 미리 지정 |
| 39 | [][]타입 = 2차원 슬라이스 |
| 40 | s = append(s, 값) → 반환값 반드시 받기 |
| 41 | for i, v := range s → 인덱스·값 동시 |
| 42 | range에서 v 수정은 원본에 영향 없음 |
| 43 | map = 키·값 쌍, Python 딕셔너리와 동일 |
| 44 | map[키타입]값타입{키:값...} = 맵 리터럴 |
| 45 | value, ok := m[key] → 키 존재 확인 필수 |

---

*Go Tour 챕터 31~45 완전 정리 — 2026.06.01*