# 🐹 Go 언어 완전 입문서 — 챕터 16~30
> 챕터 1~15 이어서 / 제어문·Defer·포인터·구조체 완전 정리  
> 모든 개념을 "왜 필요한가"부터 설명 + Python 비교 + 실수 포인트

---

## 목차
16. [Numeric Constants](#16-numeric-constants)
17. [For 기본](#17-for-기본)
18. [For = While](#18-for--while)
19. [Forever 무한루프](#19-forever-무한루프)
20. [If 기본](#20-if-기본)
21. [If with init statement](#21-if-with-init-statement)
22. [If-Else](#22-if-else)
23. [Switch 기본](#23-switch-기본)
24. [Switch 심화](#24-switch-심화)
25. [Switch with no condition](#25-switch-with-no-condition)
26. [Defer](#26-defer)
27. [Stacking Defers](#27-stacking-defers)
28. [Pointers 포인터](#28-pointers-포인터)
29. [Structs 구조체](#29-structs-구조체)
30. [Struct Literals & Pointers](#30-struct-literals--pointers)
- [실전 종합 코드](#실전-종합-코드)

---

## 16. Numeric Constants

### 먼저 복습: 챕터 15에서 배운 상수

```go
const Pi = 3.14159   // 타입 없는 상수
const MaxSize = 1024 // 타입 없는 상수
```

### Numeric Constants가 특별한 이유

타입 없이 선언한 숫자 상수는 **엄청나게 높은 정밀도**로 저장됩니다.

```go
const Big   = 1 << 62  // 2의 62승 = 4611686018427387904
const Small = Big >> 61 // 2
```

### 핵심: 상수는 필요한 타입으로 자동 변환

```go
const x = 42  // 타입 없음

// 어떤 숫자 타입에든 넣을 수 있음
var a int     = x  // int로 변환
var b float64 = x  // float64로 변환
var c int64   = x  // int64로 변환

fmt.Println(a, b, c)  // 42 42 42
```

### 변수와 비교

```go
// 변수: 타입이 고정됨
y := 42           // int로 고정
var z float64 = y // 에러! int를 float64에 못 넣음 (명시적 변환 필요)

// 상수: 유연하게 변환됨
const w = 42
var z float64 = w  // OK! 상수는 자동 변환
```

### Python 비교

```python
# Python: 숫자는 항상 유연하게 변환됨
x = 42
a: int = x    # OK
b: float = x  # OK (자동 변환)
```

```go
// Go: 변수는 타입 고정, 상수만 유연함
const x = 42       // 상수: 유연
var y int = 42     // 변수: int로 고정
```

---

## 17. For 기본

### Go에는 반복문이 for 하나뿐

Python은 `for`와 `while` 두 개지만, Go는 `for` 하나로 전부 처리합니다.

### 기본 구조 (C스타일 for)

```
for 초기문; 조건문; 후처리문 {
    반복 실행할 코드
}
```

```go
for i := 0; i < 5; i++ {
    fmt.Println(i)
}
// 출력: 0, 1, 2, 3, 4
```

### 실행 순서 (★ 중요)

```
① 초기문 실행: i := 0    (딱 한 번만)
② 조건 확인:   i < 5?    → true면 계속
③ 본문 실행:   Println(i)
④ 후처리:      i++
⑤ ② 로 돌아감
... 반복 ...
⑥ 조건이 false → 종료
```

### 각 부분 설명

```go
for i := 0; i < 5; i++ {
//  ↑        ↑       ↑
//  초기문   조건문   후처리문
//  시작값   언제까지 매번 무엇을
```

```
초기문:   i := 0   → 루프 시작 전 한 번만 실행
조건문:   i < 5    → 매번 확인, false면 탈출
후처리문: i++      → 매 반복 끝에 실행
```

### Python 비교

```python
# Python for (range)
for i in range(5):
    print(i)  # 0, 1, 2, 3, 4

# Python for (시작값, 끝, 증가)
for i in range(0, 5, 1):
    print(i)
```

```go
// Go for
for i := 0; i < 5; i++ {
    fmt.Println(i)
}

// 역순
for i := 5; i > 0; i-- {
    fmt.Println(i)  // 5, 4, 3, 2, 1
}

// 2씩 증가
for i := 0; i < 10; i += 2 {
    fmt.Println(i)  // 0, 2, 4, 6, 8
}
```

### for range: 슬라이스·맵 순회 (★ 매우 자주 씀)

```go
// 슬라이스 순회
servers := []string{"web-01", "web-02", "db-01"}

for i, name := range servers {
    fmt.Printf("[%d] %s\n", i, name)
}
// [0] web-01
// [1] web-02
// [2] db-01

// 인덱스 필요 없으면 _ 로 버리기
for _, name := range servers {
    fmt.Println(name)
}

// 인덱스만 필요하면
for i := range servers {
    fmt.Println(i)
}
```

```go
// 맵 순회
scores := map[string]int{"Alice": 95, "Bob": 87}

for name, score := range scores {
    fmt.Printf("%s: %d점\n", name, score)
}
```

### break와 continue

```go
for i := 0; i < 10; i++ {
    if i == 3 {
        continue  // 3은 건너뜀, 다음 반복으로
    }
    if i == 7 {
        break     // 7에서 루프 완전 종료
    }
    fmt.Println(i)
}
// 출력: 0, 1, 2, 4, 5, 6
```

### ★ 자주 하는 실수: 세미콜론 vs 콤마

```go
// 에러! 콤마(,) 사용
for i := 0, i < 5, i++ {  // 문법 오류

// 올바름: 세미콜론(;) 사용
for i := 0; i < 5; i++ {
```

---

## 18. For = While

### 초기문·후처리문 생략 → while처럼 동작

```go
// 세미콜론도 빼고 조건만 남기면 while
i := 0
for i < 5 {
    fmt.Println(i)
    i++
}
// 출력: 0, 1, 2, 3, 4
```

```python
# Python while
i = 0
while i < 5:
    print(i)
    i += 1
```

### 언제 쓰나요?

```go
// 파일을 한 줄씩 읽을 때
scanner := bufio.NewScanner(file)
for scanner.Scan() {
    line := scanner.Text()
    fmt.Println(line)
}

// 조건이 맞을 때까지 재시도
attempts := 0
for attempts < 3 {
    err := connectToServer()
    if err == nil {
        break
    }
    attempts++
    fmt.Printf("재시도 %d/3...\n", attempts)
}
```

---

## 19. Forever 무한루프

### 조건 없는 for = 영원히 반복

```go
for {
    // 영원히 실행됨
    // break를 만나야 탈출
}
```

```python
# Python 무한루프
while True:
    pass
```

### 실전 사용 예시

```go
// 서버 프로그램 (계속 요청 받기)
for {
    request := waitForRequest()   // 요청 대기
    go handleRequest(request)     // 처리 (고루틴)
}

// 주기적 모니터링 (5분마다 실행)
for {
    checkServerStatus()           // 서버 상태 확인
    time.Sleep(5 * time.Minute)   // 5분 대기
}

// 재시도 로직
for {
    err := connectDB()
    if err == nil {
        fmt.Println("DB 연결 성공!")
        break   // 성공하면 탈출
    }
    fmt.Println("재시도 중...")
    time.Sleep(1 * time.Second)
}
```

### ★ break 없으면 프로그램이 영원히 실행됨

반드시 탈출 조건(`break` 또는 `return`)을 설계해야 합니다.

---

## 20. If 기본

### 기본 구조

```go
if 조건 {
    // 조건이 true일 때 실행
}
```

```go
cpu := 85.5
if cpu > 80.0 {
    fmt.Println("CPU 사용률 높음!")
}
```

### Python과 가장 큰 차이 2가지

```python
# Python
if x > 5:        # 1. 콜론(:) 필요
    print("ok")  # 2. 들여쓰기로 블록 구분
```

```go
// Go
if x > 5 {       // 1. 소괄호() 없음
    fmt.Println("ok")  // 2. 중괄호{} 필수
}
// 3. { 는 반드시 if 와 같은 줄에!
```

### ★ { 위치 규칙 (자주 실수)

```go
// 올바름 ✅
if x > 5 {
    fmt.Println("ok")
}

// 에러 ❌ ({ 를 다음 줄에)
if x > 5
{
    fmt.Println("ok")
}
// 컴파일 에러: "unexpected newline, expecting { after if clause"
```

**이유**: Go는 세미콜론을 자동으로 삽입합니다.  
`if x > 5` 뒤에 자동으로 `;`이 붙어버려서 문법 오류가 납니다.

### 비교 연산자 정리

```go
x == y  // 같다 (= 하나는 할당, == 두개는 비교)
x != y  // 다르다
x < y   // 작다
x > y   // 크다
x <= y  // 작거나 같다
x >= y  // 크거나 같다
```

### 논리 연산자

```go
x > 0 && x < 100  // AND (Python의 and)
x < 0 || x > 100  // OR  (Python의 or)
!(x > 0)          // NOT (Python의 not)
```

---

## 21. If with init statement

### Go만의 특별한 문법

if 문 안에서 변수를 선언하고 바로 조건 검사합니다.

```go
if 초기문; 조건문 {
    // 초기문에서 선언한 변수 사용 가능
}
// 초기문의 변수는 if 블록 안에서만 존재
```

### 왜 필요한가?

```go
// 일반적인 방식 (변수가 if 밖에도 보임)
result, err := divide(10, 2)
if err != nil {
    fmt.Println("에러:", err)
}
fmt.Println(result)  // if 밖에서도 result, err 접근 가능
// → 실수로 result를 잘못 사용할 수 있음

// if with init 방식 (변수가 if 블록 안에만 존재)
if result, err := divide(10, 2); err != nil {
    fmt.Println("에러:", err)
} else {
    fmt.Println("결과:", result)  // else에서도 result 사용 가능
}
// fmt.Println(result)  → 에러! if 밖에서는 result 없음
```

### 실전 패턴 (★ Go 코드에서 매우 자주 보임)

```go
// 파일 존재 확인
if _, err := os.Stat("config.json"); err != nil {
    fmt.Println("설정 파일 없음")
}

// 맵에서 키 확인
users := map[string]int{"Alice": 1, "Bob": 2}
if id, ok := users["Alice"]; ok {
    fmt.Printf("Alice의 ID: %d\n", id)
} else {
    fmt.Println("Alice 없음")
}
```

---

## 22. If-Else

### 기본 구조

```go
if 조건1 {
    // 조건1 true
} else if 조건2 {
    // 조건2 true
} else if 조건3 {
    // 조건3 true
} else {
    // 모두 false
}
```

### ★ else 위치 규칙

```go
// 올바름 ✅ (} else { 같은 줄)
if x > 0 {
    fmt.Println("양수")
} else {
    fmt.Println("음수 or 0")
}

// 에러 ❌ (} 다음 줄에 else)
if x > 0 {
    fmt.Println("양수")
}
else {          // ← 에러!
    fmt.Println("음수 or 0")
}
```

### 실전 예시: 서버 CPU 상태

```go
cpu := 87.5

if cpu >= 90 {
    fmt.Println("🔴 위험: 즉시 대응 필요")
} else if cpu >= 80 {
    fmt.Println("🟡 주의: 모니터링 강화")  // 출력됨
} else if cpu >= 60 {
    fmt.Println("🟠 보통: 정상 범위")
} else {
    fmt.Println("🟢 정상: 여유 있음")
}
```

---

## 23. Switch 기본

### Switch란?

여러 값을 비교할 때 if-else 대신 사용합니다.  
코드가 훨씬 깔끔해집니다.

### 기본 구조

```go
switch 변수 {
case 값1:
    // 값1일 때
case 값2:
    // 값2일 때
case 값3, 값4:  // 여러 값을 한 case에
    // 값3 또는 값4일 때
default:
    // 어떤 case도 해당 없을 때
}
```

```go
day := "Monday"

switch day {
case "Monday":
    fmt.Println("월요일 — 운동 없는 날")
case "Saturday", "Sunday":
    fmt.Println("주말")
default:
    fmt.Println("평일")
}
```

### Python 비교

```python
# Python 3.10+ match
match day:
    case "Monday":
        print("월요일")
    case "Saturday" | "Sunday":
        print("주말")
    case _:
        print("평일")
```

### ★ Go Switch vs C/Java Switch 결정적 차이

```
C/Java: 각 case마다 break 안 쓰면 다음 case로 "떨어짐" (fall-through)
Go:     자동으로 break됨 — 다음 case로 절대 안 넘어감
```

```go
x := 1
switch x {
case 1:
    fmt.Println("하나")
    // break 없어도 자동 종료
case 2:
    fmt.Println("둘")  // 실행 안 됨
}
// 출력: 하나
```

```go
// 다음 case로 넘기고 싶으면 명시적으로 fallthrough
x := 1
switch x {
case 1:
    fmt.Println("하나")
    fallthrough  // 명시적으로 다음 case 실행
case 2:
    fmt.Println("둘")  // fallthrough로 인해 실행됨
case 3:
    fmt.Println("셋")  // 실행 안 됨
}
// 출력: 하나, 둘
```

---

## 24. Switch 심화

### case에 조건식 사용 가능

```go
score := 85

switch {            // ← 변수 없음
case score >= 90:
    fmt.Println("A")
case score >= 80:
    fmt.Println("B")  // 출력됨
case score >= 70:
    fmt.Println("C")
default:
    fmt.Println("F")
}
```

### 타입 Switch (Type Switch) ★ DevOps에서 자주 씀

인터페이스 변수의 **실제 타입**을 확인할 때 사용합니다.

```go
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("정수: %d\n", v)
    case string:
        fmt.Printf("문자열: %s (길이: %d)\n", v, len(v))
    case bool:
        fmt.Printf("불리언: %t\n", v)
    case []int:
        fmt.Printf("정수 슬라이스: %v\n", v)
    default:
        fmt.Printf("알 수 없는 타입: %T\n", v)
    }
}

describe(42)            // 정수: 42
describe("hello")       // 문자열: hello (길이: 5)
describe(true)          // 불리언: true
describe([]int{1,2,3})  // 정수 슬라이스: [1 2 3]
```

---

## 25. Switch with no condition

### 조건 없는 switch = 깔끔한 if-else 대체

```go
hour := 14

// if-else 방식 (길고 지저분)
if hour >= 6 && hour < 12 {
    fmt.Println("오전")
} else if hour >= 12 && hour < 18 {
    fmt.Println("오후")
} else if hour >= 18 && hour < 22 {
    fmt.Println("저녁")
} else {
    fmt.Println("밤")
}

// switch 방식 (깔끔)
switch {
case hour >= 6 && hour < 12:
    fmt.Println("오전")
case hour >= 12 && hour < 18:
    fmt.Println("오후")  // 출력됨
case hour >= 18 && hour < 22:
    fmt.Println("저녁")
default:
    fmt.Println("밤")
}
```

### 언제 if-else 대신 switch를 쓰나?

```
3개 이상의 조건을 비교할 때 → switch가 더 읽기 쉬움
2개 이하의 조건 → if-else로 충분
같은 변수를 여러 값과 비교 → switch가 명확함
```

---

## 26. Defer

### Defer란?

함수가 **종료될 때** 특정 코드를 실행하도록 예약하는 키워드입니다.

```go
func main() {
    defer fmt.Println("3. defer 실행")

    fmt.Println("1. 먼저")
    fmt.Println("2. 그 다음")
}
// 출력:
// 1. 먼저
// 2. 그 다음
// 3. defer 실행
```

### 왜 defer가 필요한가?

프로그래밍에서 자원을 열면 반드시 닫아야 합니다.

```go
// defer 없는 코드 (위험)
func readFile(filename string) {
    file, err := os.Open(filename)
    if err != nil {
        return  // 에러 시 file.Close() 없이 return
    }

    data, err := io.ReadAll(file)
    if err != nil {
        file.Close()  // 매번 직접 닫아야 함
        return
    }

    process(data)
    file.Close()  // 또 직접 닫아야 함
}

// defer 사용 (안전하고 깔끔)
func readFile(filename string) {
    file, err := os.Open(filename)
    if err != nil {
        return
    }
    defer file.Close()  // ← 한 줄로 끝, 어디서 return해도 항상 실행

    data, _ := io.ReadAll(file)
    process(data)
    // 함수 종료 시 자동으로 file.Close() 실행
}
```

### defer의 3가지 보장

```
1. 함수가 정상 종료되어도 실행
2. 에러로 return해도 실행
3. panic(충돌)이 발생해도 실행 (recover 패턴)
```

### 실전 사용 패턴

```go
// 1. 파일 닫기
file, _ := os.Open("data.txt")
defer file.Close()

// 2. HTTP 응답 닫기
resp, _ := http.Get("https://api.example.com/data")
defer resp.Body.Close()

// 3. DB 연결 닫기
db, _ := sql.Open("postgres", connStr)
defer db.Close()

// 4. 뮤텍스 해제
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()  // 함수 끝나면 자동 해제

// 5. 함수 실행 시간 측정
func process() {
    start := time.Now()
    defer func() {
        fmt.Printf("실행 시간: %v\n", time.Since(start))
    }()
    // 실제 처리 로직
}
```

### Python과 비교

```python
# Python: with문 (컨텍스트 매니저)
with open("data.txt") as file:
    data = file.read()
# with 블록 끝나면 자동으로 file.close()
```

```go
// Go: defer
file, _ := os.Open("data.txt")
defer file.Close()  // 함수 종료 시 자동으로 닫힘
data, _ := io.ReadAll(file)
// Python with보다 유연: 함수 어느 위치에서든 return해도 실행됨
```

### ★ defer의 값 캡처 시점 (함정)

```go
x := 1
defer fmt.Println("x =", x)  // x값이 defer 등록 시점(1)에 캡처됨
x = 100
// 출력: x = 1  (100이 아님!)

// 실행 시점의 값을 쓰려면 클로저 사용
defer func() {
    fmt.Println("x =", x)  // 실행 시점의 x 사용
}()
x = 100
// 출력: x = 100
```

---

## 27. Stacking Defers

### defer 여러 개 = 역순 실행

```go
func main() {
    fmt.Println("시작")

    defer fmt.Println("1번 defer")
    defer fmt.Println("2번 defer")
    defer fmt.Println("3번 defer")

    fmt.Println("끝")
}
// 출력:
// 시작
// 끝
// 3번 defer  ← 마지막 등록이 먼저 실행
// 2번 defer
// 1번 defer  ← 처음 등록이 마지막 실행
```

### 왜 역순인가? — 스택(Stack) 자료구조

```
등록 순서: defer1 → defer2 → defer3
           (스택에 쌓임: 아래에서 위로)

스택 상태:
  [3번]  ← top (나중에 쌓임)
  [2번]
  [1번]  ← bottom (먼저 쌓임)

실행 순서: top부터 꺼냄
  3번 → 2번 → 1번 (역순)
```

### 실전 예시: 중첩된 자원 해제

```go
func processData() {
    db, _ := sql.Open("postgres", connStr)
    defer db.Close()           // 3번째로 해제 (마지막 등록이라 아님, 역순)

    tx, _ := db.Begin()
    defer tx.Rollback()        // 2번째로 해제

    file, _ := os.Open("data")
    defer file.Close()         // 1번째로 해제 (마지막 등록이므로 첫 실행)

    // 실제 처리
}
// 종료 시 실행 순서: file.Close() → tx.Rollback() → db.Close()
// 가장 나중에 연 것부터 닫힘 (자원 의존성 역순)
```

---

## 28. Pointers 포인터

### 포인터가 왜 필요한가?

이해를 위해 먼저 "값이 복사되는 문제"를 봅니다.

```go
func addTen(n int) {
    n = n + 10  // n은 복사본, 원본에 영향 없음
}

score := 85
addTen(score)
fmt.Println(score)  // 85 (변경 안 됨!)
```

Go는 함수에 값을 넘길 때 **복사본**을 만듭니다.  
포인터를 쓰면 **원본의 주소**를 넘겨서 직접 수정할 수 있습니다.

### 메모리 구조로 이해하기

```
변수 score := 85가 메모리에 저장되는 모습:

주소:  0xc000018090
값:    85

포인터 p := &score 는:
주소:  0xc000018098
값:    0xc000018090  ← score의 주소를 저장
```

### 포인터 기호 2가지

```go
// & : 변수의 메모리 주소를 가져옴
p := &score     // score의 주소 → p에 저장

// * : 포인터가 가리키는 곳의 값을 가져옴 (역참조)
fmt.Println(*p) // p가 가리키는 곳의 값 = 85
```

```go
score := 85

p := &score           // p = score의 주소
fmt.Println(score)    // 85
fmt.Println(p)        // 0xc000018090 (주소값, 실행마다 다름)
fmt.Println(*p)       // 85 (p가 가리키는 값)

*p = 100              // p가 가리키는 곳에 100 저장
fmt.Println(score)    // 100 (score가 바뀜!)
```

### 포인터로 원본 수정하기

```go
// 포인터 없음: 복사본 수정 (원본 그대로)
func addTen(n int) {
    n = n + 10
}

// 포인터 사용: 원본 수정
func addTenPtr(n *int) {  // *int = int를 가리키는 포인터
    *n = *n + 10          // 역참조해서 원본 수정
}

score := 85
addTenPtr(&score)         // score의 주소 전달
fmt.Println(score)        // 95 (원본 변경됨!)
```

### 포인터 타입

```go
var p *int      // int를 가리키는 포인터 (기본값: nil)
var q *string   // string을 가리키는 포인터
var r *float64  // float64를 가리키는 포인터

// *타입 형태
// 포인터 선언만 하면 nil (아무것도 가리키지 않음)
fmt.Println(p)  // <nil>
```

### nil 포인터 주의

```go
var p *int
fmt.Println(*p)  // 패닉(crash)! nil 포인터 역참조

// 사용 전 반드시 nil 확인
if p != nil {
    fmt.Println(*p)  // 안전
}
```

### Python과 비교

```python
# Python: 기본 타입(int, str 등)은 불변, 함수에서 수정 불가
def add_ten(n):
    n += 10  # 원본 수정 안 됨

score = 85
add_ten(score)
print(score)  # 85

# Python에서 원본 수정하려면 리스트/딕셔너리 같은 가변 객체 사용
def add_ten(data):
    data['score'] += 10

data = {'score': 85}
add_ten(data)
print(data['score'])  # 95
```

---

## 29. Structs 구조체

### 구조체란?

관련된 여러 데이터를 하나로 묶는 자료구조입니다.

```go
// 사람 정보를 하나로 묶기
type Person struct {
    Name string
    Age  int
    City string
}
```

```python
# Python 비교: 클래스
class Person:
    def __init__(self, name: str, age: int, city: str):
        self.name = name
        self.age = age
        self.city = city

# 또는 dataclass
from dataclasses import dataclass

@dataclass
class Person:
    name: str
    age: int
    city: str
```

### 구조체 정의 위치

```go
// 패키지 레벨 (다른 함수에서도 사용 가능) - 권장
type Server struct {
    Host    string
    Port    int
    CPU     float64
    IsAlive bool
}

func main() {
    // ...
}
```

### 구조체 생성 방법 3가지

```go
// 방법 1: 필드명 지정 (권장 ★)
p1 := Person{
    Name: "성윤",
    Age:  31,
    City: "서울",
}

// 방법 2: 순서대로 (비권장 - 순서 바뀌면 버그)
p2 := Person{"성윤", 31, "서울"}

// 방법 3: 일부만 초기화 (나머지는 zero value)
p3 := Person{Name: "성윤"}
// p3.Age = 0 (zero value)
// p3.City = "" (zero value)
```

### 필드 접근 (점 . 사용)

```go
p := Person{Name: "성윤", Age: 31, City: "서울"}

// 읽기
fmt.Println(p.Name)   // 성윤
fmt.Println(p.Age)    // 31

// 수정
p.Age = 32
fmt.Printf("%s의 나이: %d\n", p.Name, p.Age)  // 성윤의 나이: 32
```

### 구조체 비교

```go
p1 := Person{Name: "성윤", Age: 31}
p2 := Person{Name: "성윤", Age: 31}
p3 := Person{Name: "길동", Age: 25}

fmt.Println(p1 == p2)  // true (필드값 모두 같음)
fmt.Println(p1 == p3)  // false
```

### 구조체 안에 구조체 (중첩)

```go
type Address struct {
    Street string
    City   string
}

type Employee struct {
    Name    string
    Age     int
    Address Address  // 구조체 안에 구조체
}

e := Employee{
    Name: "성윤",
    Age:  31,
    Address: Address{
        Street: "노원로 123",
        City:   "서울",
    },
}

fmt.Println(e.Name)            // 성윤
fmt.Println(e.Address.City)    // 서울
```

### DevOps 실전 예시

```go
type Server struct {
    Host    string
    Port    int
    CPU     float64
    Memory  float64
    Disk    float64
    IsAlive bool
}

// 서버 상태 확인 함수
func checkAlert(s Server) {
    if s.CPU > 90 {
        fmt.Printf("[알림] %s CPU 위험: %.1f%%\n", s.Host, s.CPU)
    }
    if s.Memory > 85 {
        fmt.Printf("[알림] %s 메모리 위험: %.1f%%\n", s.Host, s.Memory)
    }
    if s.Disk > 80 {
        fmt.Printf("[알림] %s 디스크 위험: %.1f%%\n", s.Host, s.Disk)
    }
}

servers := []Server{
    {Host: "web-01", Port: 8080, CPU: 92.5, Memory: 70.0, Disk: 55.0, IsAlive: true},
    {Host: "db-01",  Port: 5432, CPU: 45.0, Memory: 87.3, Disk: 72.0, IsAlive: true},
}

for _, s := range servers {
    checkAlert(s)
}
```

---

## 30. Struct Literals & Pointers

### 구조체 포인터 생성

```go
// 방법 1: & 사용
p := Person{Name: "성윤", Age: 31}
ptr := &p  // 구조체 포인터

// 방법 2: & 와 literal 동시에 (자주 씀)
ptr2 := &Person{Name: "성윤", Age: 31}
// ptr2의 타입: *Person
```

### 포인터로 필드 접근

```go
p := &Person{Name: "성윤", Age: 31}

// (*p).Name 이렇게 써야 하지만 → 불편
fmt.Println((*p).Name)  // 성윤

// Go에서 자동 역참조 지원 → 그냥 . 으로 접근
fmt.Println(p.Name)     // 성윤 (동일하게 동작)
p.Age = 32              // 포인터로 직접 수정
```

### 구조체 복사 vs 포인터 (★ 중요한 차이)

```go
type Server struct {
    CPU float64
}

s1 := Server{CPU: 50.0}

// 복사: s2는 s1과 완전히 별개
s2 := s1
s2.CPU = 90.0
fmt.Println(s1.CPU)  // 50.0 (s1은 그대로)
fmt.Println(s2.CPU)  // 90.0

// 포인터: s3은 s1을 가리킴
s3 := &s1
s3.CPU = 90.0
fmt.Println(s1.CPU)  // 90.0 (s1도 바뀜!)
```

### 함수에서 구조체 수정

```go
// 복사로 전달: 함수 안에서 수정해도 원본 그대로
func updateCPU_copy(s Server, cpu float64) {
    s.CPU = cpu  // 복사본 수정, 원본 그대로
}

// 포인터로 전달: 함수 안에서 원본 수정 가능
func updateCPU_ptr(s *Server, cpu float64) {
    s.CPU = cpu  // 원본 수정됨
}

server := Server{CPU: 50.0}

updateCPU_copy(server, 90.0)
fmt.Println(server.CPU)  // 50.0 (변경 안 됨)

updateCPU_ptr(&server, 90.0)
fmt.Println(server.CPU)  // 90.0 (변경됨!)
```

### 언제 포인터를 쓰나요?

```
1. 함수에서 구조체 원본을 수정해야 할 때
2. 구조체가 클 때 (복사 비용 절약)
3. nil 체크가 필요할 때 (존재하지 않을 수 있는 경우)

작은 구조체 (2~3개 필드) → 복사 OK
큰 구조체 (많은 필드) → 포인터 권장
```

---

## 실전 종합 코드

아래를 `practice_ch16_30.go`로 저장 후 `go run practice_ch16_30.go` 실행:

```go
package main

import (
    "fmt"
    "time"
)

// 서버 구조체
type Server struct {
    Host    string
    Port    int
    CPU     float64
    Memory  float64
    IsAlive bool
}

// 포인터로 CPU 업데이트
func updateMetrics(s *Server, cpu, mem float64) {
    s.CPU = cpu
    s.Memory = mem
}

// 상태 확인
func getStatus(cpu float64) string {
    switch {
    case cpu >= 90:
        return "🔴 위험"
    case cpu >= 70:
        return "🟡 주의"
    case cpu >= 50:
        return "🟠 보통"
    default:
        return "🟢 정상"
    }
}

func main() {
    // === For 루프 ===
    fmt.Println("=== 서버 목록 ===")
    servers := []Server{
        {Host: "web-01", Port: 8080, CPU: 45.5, Memory: 62.0, IsAlive: true},
        {Host: "web-02", Port: 8080, CPU: 91.2, Memory: 87.5, IsAlive: true},
        {Host: "db-01",  Port: 5432, CPU: 33.0, Memory: 45.0, IsAlive: false},
    }

    for i, s := range servers {
        status := "🟢 온라인"
        if !s.IsAlive {
            status = "🔴 오프라인"
        }
        fmt.Printf("[%d] %s:%d | CPU: %.1f%% %s | 상태: %s\n",
            i, s.Host, s.Port, s.CPU, getStatus(s.CPU), status)
    }

    // === If-Else ===
    fmt.Println("\n=== 알림 확인 ===")
    for _, s := range servers {
        if !s.IsAlive {
            fmt.Printf("⚠️  %s 서버 다운!\n", s.Host)
        } else if s.CPU >= 90 {
            fmt.Printf("🔴 %s CPU 위험: %.1f%%\n", s.Host, s.CPU)
        } else if s.Memory >= 85 {
            fmt.Printf("🟡 %s 메모리 주의: %.1f%%\n", s.Host, s.Memory)
        }
    }

    // === Defer ===
    fmt.Println("\n=== Defer 데모 ===")
    func() {
        defer fmt.Println("작업 완료 로그 기록")  // 마지막에 실행
        defer fmt.Println("연결 해제")            // 그 전에 실행
        fmt.Println("작업 시작")
        fmt.Println("데이터 처리 중...")
        // 함수 종료 시 defer 역순 실행
    }()

    // === Pointer ===
    fmt.Println("\n=== 포인터로 구조체 수정 ===")
    target := servers[0]
    fmt.Printf("수정 전 CPU: %.1f%%\n", target.CPU)

    updateMetrics(&target, 95.3, 88.1)
    fmt.Printf("수정 후 CPU: %.1f%%\n", target.CPU)
    fmt.Printf("상태: %s\n", getStatus(target.CPU))

    // === Switch ===
    fmt.Println("\n=== 요일별 일정 ===")
    weekday := time.Now().Weekday().String()
    switch weekday {
    case "Monday":
        fmt.Println("월요일: 운동 없음")
    case "Saturday", "Sunday":
        fmt.Println("주말: 주간 보고서 작성")
    default:
        fmt.Println("평일: 운동 있음 (21:00~23:00)")
    }

    // === Stacking Defers ===
    fmt.Println("\n=== Stacking Defers ===")
    func() {
        defer fmt.Println("1단계 자원 해제")
        defer fmt.Println("2단계 자원 해제")
        defer fmt.Println("3단계 자원 해제")
        fmt.Println("작업 실행 중...")
    }()
    // 출력 순서: 3→2→1 (역순)
}
```

---

## 챕터별 핵심 한줄 요약

| 챕터 | 핵심 |
|------|------|
| 16 | 타입 없는 상수 → 어떤 타입에도 자동 변환 |
| 17 | for 초기;조건;후처리 — { 는 반드시 같은 줄 |
| 18 | for 조건 {} — Go의 while |
| 19 | for {} — 무한루프, break 없으면 영원히 |
| 20 | if 조건 {} — () 없음, {} 필수, { 같은 줄 |
| 21 | if 초기문; 조건 {} — 변수 스코프를 if 안으로 제한 |
| 22 | } else { — else는 반드시 } 와 같은 줄 |
| 23 | switch — 자동 break, fallthrough로 다음 case |
| 24 | switch { case 조건: } — 타입 switch도 가능 |
| 25 | 조건 없는 switch — 여러 조건 비교 시 if-else보다 깔끔 |
| 26 | defer — 함수 종료 시 실행, 자원 해제에 필수 |
| 27 | defer 여러 개 → 역순(LIFO) 실행 |
| 28 | & = 주소 가져오기, * = 값 가져오기(역참조), 원본 수정 가능 |
| 29 | struct — 관련 데이터를 하나로 묶음, . 으로 접근 |
| 30 | &Struct{} — 구조체 포인터 생성, 자동 역참조 지원 |

---