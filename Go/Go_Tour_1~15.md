# 🐹 Go 언어 완전 입문서 — 챕터 1~15
> 초보자를 위한 한국어 완전 설명서  
> Python 사용자 기준으로 설명

---

## 목차
1. [Go 언어란?](#1-go-언어란)
2. [Package](#2-package)
3. [Import](#3-import)
4. [Exported Names](#4-exported-names)
5. [Functions](#5-functions)
6. [Multiple Return Values](#6-multiple-return-values)
7. [Named Return Values](#7-named-return-values)
8. [Variables](#8-variables)
9. [Short Variable Declaration](#9-short-variable-declaration-)
10. [Basic Types](#10-basic-types)
11. [Zero Values](#11-zero-values)
12. [Type Conversions](#12-type-conversions)
13. [Type Inference](#13-type-inference)
14. [Constants](#14-constants)
15. [심화: 자주 쓰는 것들](#15-심화-자주-쓰는-것들)

---

## 1. Go 언어란?

### Go가 뭔가요?
Google이 2009년에 만든 프로그래밍 언어입니다.

### 왜 DevOps 엔지니어가 Go를 배워야 하나요?
DevOps에서 쓰는 핵심 도구들이 전부 Go로 만들어져 있습니다.

| 도구 | 언어 | 용도 |
|------|------|------|
| Docker | Go | 컨테이너 |
| Kubernetes | Go | 컨테이너 오케스트레이션 |
| Terraform | Go | 인프라 자동화 |
| Prometheus | Go | 모니터링 |
| GitHub CLI | Go | Git 명령줄 도구 |

이 도구들의 코드를 읽고, 플러그인을 만들고, 커스터마이징하려면 Go를 알아야 합니다.

### Python이랑 뭐가 다른가요?

```
Python:
  - 인터프리터 언어 (코드를 한 줄씩 읽으면서 실행)
  - 타입을 안 써도 됨 (동적 타입)
  - 느림
  - 배포할 때 Python 설치 필요

Go:
  - 컴파일 언어 (코드를 기계어로 미리 변환해서 실행)
  - 타입을 반드시 써야 함 (정적 타입)
  - 매우 빠름 (C 수준)
  - 배포할 때 파일 하나만 있으면 됨 (Python 설치 불필요)
```

---

## 2. Package

### Package가 뭔가요?
Go 파일을 그룹으로 묶는 단위입니다.  
모든 Go 파일의 **첫 번째 줄**은 반드시 package 선언이어야 합니다.

```go
package main
```

### package main이 특별한 이유
Go에서 `main`은 예약된 특별한 이름입니다.

```
package main  →  "이 파일은 실행할 수 있는 프로그램이다"
              →  반드시 func main() 함수가 있어야 함
              →  go run 또는 go build로 실행 가능

package utils →  "이 파일은 다른 곳에서 가져다 쓰는 도구 모음이다"
              →  func main() 없어도 됨
              →  직접 실행 불가, import해서 사용
```

### Python이랑 비교
```python
# Python: 파일 자체가 모듈
# 파일 이름이 곧 모듈 이름
# utils.py → import utils

# Go: package 선언이 모듈 이름을 결정
# 파일 이름과 달라도 됨 (하지만 같게 하는 게 관례)
```

### 주의사항
```
같은 폴더 안의 .go 파일들은 모두 같은 package이어야 합니다.

폴더 구조 예시:
  myapp/
    ├── main.go      → package main
    ├── helper.go    → package main   ← 같은 폴더, 같은 package
    └── utils/
        └── tools.go → package utils  ← 다른 폴더, 다른 package 가능
```

---

## 3. Import

### Import가 뭔가요?
다른 패키지(기능 모음)를 내 코드에서 사용하겠다고 선언하는 것입니다.  
Python의 `import`와 완전히 같은 개념입니다.

```go
// Go
import "fmt"

// Python
import os
```

### 여러 개 import하는 방법

```go
// 방법 1: 개별로 (비권장)
import "fmt"
import "math"
import "strings"

// 방법 2: 괄호로 묶기 (권장 ★★★)
import (
    "fmt"
    "math"
    "strings"
)
```

### fmt 패키지가 뭔가요?
`fmt`는 **format**의 줄임말입니다.  
출력, 입력, 문자열 포맷 관련 기능을 모아놓은 패키지입니다.

```go
fmt.Println("hello")      // Python의 print("hello")
fmt.Printf("%d", 42)      // Python의 print(f"{42}")
fmt.Sprintf("%d", 42)     // Python의 f"{42}" (출력 안 하고 문자열로 반환)
fmt.Scan(&x)              // Python의 input()
```

### 표준 라이브러리 자주 쓰는 패키지

| 패키지 | 용도 | 예시 |
|--------|------|------|
| `fmt` | 출력·입력·포맷 | fmt.Println() |
| `math` | 수학 계산 | math.Sqrt() |
| `strings` | 문자열 처리 | strings.Contains() |
| `strconv` | 타입 변환 | strconv.Itoa() |
| `os` | 파일·환경변수 | os.Exit() |
| `time` | 시간 처리 | time.Now() |
| `errors` | 에러 생성 | errors.New() |

### ★ 중요한 규칙: import 했으면 반드시 써야 함

```go
import "fmt"
import "math"  // ← math를 사용하지 않으면

func main() {
    fmt.Println("hello")
    // math를 사용 안 함
}
// → 컴파일 에러: "math" imported and not used
```

```python
# Python은 이래도 경고만 나오고 실행됨
import os  # 사용 안 해도 OK
print("hello")
```

Go는 사용하지 않는 import를 허용하지 않습니다.  
**이유**: 코드를 깔끔하게 유지하고, 컴파일 속도를 빠르게 하기 위해서입니다.

---

## 4. Exported Names

### 공개(Public) vs 비공개(Private)
Go에서 접근 제어는 딱 하나의 규칙으로 결정됩니다.

```
대문자로 시작  →  공개 (Public)  →  다른 패키지에서 사용 가능
소문자로 시작  →  비공개 (Private)  →  같은 패키지 안에서만 사용 가능
```

### 실제 예시

```go
// fmt 패키지 안에 있는 함수들
fmt.Println()   // ← 대문자 P → 공개 → 우리가 사용 가능 ✅
fmt.println()   // ← 소문자 p → 비공개 → 우리가 사용 불가 ❌

// math 패키지
math.Sqrt()     // ← 대문자 S → 공개 → 사용 가능 ✅
math.Pi         // ← 대문자 P → 공개 → 사용 가능 ✅
```

### Python이랑 비교

```python
# Python: _ 관례 (권고사항, 실제로는 접근 가능)
class MyClass:
    def public_method(self):    # 공개 (관례)
        pass
    def _private_method(self):  # 비공개 (관례, 실제론 접근 가능)
        pass
```

```go
// Go: 대소문자로 컴파일러가 강제 차단
func PublicFunc() {}   // 공개 (다른 패키지에서 사용 가능)
func privateFunc() {}  // 비공개 (컴파일러가 강제로 차단)
```

### 적용 범위
함수뿐만 아니라 모든 식별자에 적용됩니다.

```go
// 변수
var PublicVar = 1    // 공개
var privateVar = 2   // 비공개

// 상수
const MaxSize = 100  // 공개
const minSize = 10   // 비공개

// 구조체
type User struct {
    Name string  // 공개 (외부에서 접근 가능)
    age  int     // 비공개 (같은 패키지 안에서만)
}
```

---

## 5. Functions

### 기본 구조

```go
func 함수이름(파라미터명 타입) 반환타입 {
    // 함수 내용
    return 반환값
}
```

### Python이랑 비교

```python
# Python: 타입 없음
def add(x, y):
    return x + y
```

```go
// Go: 타입 필수
func add(x int, y int) int {
    return x + y
}
```

### 타입이 같으면 축약 가능

```go
// 원래 형태
func add(x int, y int) int { return x + y }

// 축약 형태 (같은 타입이면 마지막에만)
func add(x, y int) int { return x + y }
```

### 반환값 없는 함수 (void)

```go
// 반환 타입을 아예 쓰지 않음
func sayHello(name string) {
    fmt.Printf("안녕하세요, %s님!\n", name)
    // return 없어도 됨
}
```

```python
# Python의 None 반환 함수와 동일
def say_hello(name):
    print(f"안녕하세요, {name}님!")
```

### 함수 호출 방법

```go
// 기본 호출
add(3, 4)

// 반환값 저장
result := add(3, 4)   // result = 7

// 반환값 무시 (Go에서는 드문 경우)
// _ = add(3, 4)
```

### 에러 처리 함수 패턴 (★ 매우 중요)

Go에서 가장 많이 보게 되는 패턴입니다.

```go
// 함수 정의: 결과값 + 에러를 함께 반환
func divide(x, y float64) (float64, error) {
    if y == 0 {
        return 0, fmt.Errorf("0으로 나눌 수 없습니다")
    }
    return x / y, nil  // nil = 에러 없음
}

// 함수 사용
result, err := divide(10, 2)
if err != nil {  // err가 nil이 아니면 에러 발생
    fmt.Println("에러:", err)
} else {
    fmt.Println("결과:", result)
}
```

```python
# Python 방식: try/except
try:
    result = 10 / 2
except ZeroDivisionError as e:
    print("에러:", e)
```

**Go 방식이 더 명시적입니다.**  
함수 시그니처만 봐도 "이 함수는 에러가 날 수 있다"는 게 바로 보입니다.

---

## 6. Multiple Return Values

### Go만의 강력한 기능: 반환값 여러 개

```go
// 두 값을 동시에 반환
func swap(a, b string) (string, string) {
    return b, a  // 순서를 바꿔서 반환
}

// 사용
x, y := swap("hello", "world")
// x = "world", y = "hello"
```

### Python이랑 비교

```python
# Python: tuple로 반환
def swap(a, b):
    return b, a  # tuple (b, a) 반환

x, y = swap("hello", "world")
```

```go
// Go: 명시적으로 반환 타입 선언
func swap(a, b string) (string, string) {
    return b, a
}
```

Go는 반환 타입을 미리 선언해야 해서 더 명확합니다.

### 사용하지 않는 반환값 버리기

```go
result, err := divide(10, 2)  // 둘 다 사용

result2, _ := divide(10, 2)   // err 무시 (비권장)
// _ = 이 값은 사용 안 할 거야, 버려줘
```

```python
# Python의 _ 와 동일한 개념
result, _ = some_function()
```

---

## 7. Named Return Values

### 개념
함수 반환값에 미리 이름을 붙여두는 방법입니다.

```go
// 일반 방식
func split(sum int) (int, int) {
    x := sum * 4 / 9
    y := sum - x
    return x, y
}

// Named return 방식
func split(sum int) (x, y int) {  // ← 반환값에 이름 붙임
    x = sum * 4 / 9               // ← 선언 없이 바로 사용
    y = sum - x
    return                         // ← naked return: x, y 자동 반환
}
```

### 언제 쓰나요?
짧고 간단한 함수에서 코드를 문서처럼 읽히게 할 때 씁니다.

```go
// "이 함수는 width와 height를 반환한다"는 게 한눈에 보임
func getImageSize() (width, height int) {
    width = 1920
    height = 1080
    return
}
```

### 주의사항
함수가 길면 naked return은 혼란을 줍니다.  
10줄 이상의 함수에서는 명시적으로 `return x, y` 쓰는 게 좋습니다.

---

## 8. Variables

### 변수 선언 4가지 방법

#### 방법 1: var + 타입 + 값
```go
var name string = "성윤"
var age int = 31
var height float64 = 175.5
var isStudent bool = false
```

#### 방법 2: var + 타입만 (값은 zero value)
```go
var name string    // "" (빈 문자열)
var age int        // 0
var height float64 // 0.0
var isStudent bool // false
```

#### 방법 3: var + 값만 (타입 추론)
```go
var name = "성윤"     // string으로 자동 추론
var age = 31         // int로 자동 추론
var height = 175.5   // float64로 자동 추론
```

#### 방법 4: := (가장 많이 씀)
```go
name := "성윤"      // var name string = "성윤" 과 동일
age := 31           // var age int = 31 과 동일
height := 175.5     // var height float64 = 175.5 와 동일
```

### 언제 어떤 방법을 쓰나요?

```
함수 밖 (패키지 레벨):  var만 사용 가능 (:= 불가)
함수 안:               := 를 주로 사용 (간결하니까)

명시적 타입 지정 필요할 때: var x float64 = 42
                           (42는 int로 추론되지만, float64로 쓰고 싶을 때)
```

### 여러 변수 한번에 선언

```go
// var 블록
var (
    name    string = "성윤"
    age     int    = 31
    city    string = "서울"
)

// := 여러 개
x, y, z := 1, 2, 3

// 함수 반환값으로 여러 변수 동시 선언
result, err := divide(10, 2)
```

### ★ 중요: 선언한 변수는 반드시 써야 함

```go
x := 10
// x를 한 번도 사용하지 않으면 → 컴파일 에러
// "x declared but not used"

// 해결책 1: 사용하기
fmt.Println(x)

// 해결책 2: _ 로 명시적 무시
_ = x
```

---

## 9. Short Variable Declaration (:=)

### := 란?

`:=`는 **선언 + 할당**을 동시에 하는 연산자입니다.

```go
x := 42
// 이것은 아래와 완전히 동일합니다:
var x int = 42
```

### 중요한 규칙들

#### 규칙 1: 함수 안에서만 사용 가능
```go
package main

x := 10  // ← 에러! 함수 밖에서 := 사용 불가
var y = 20  // ← OK, 함수 밖에서는 var 사용

func main() {
    z := 30  // ← OK, 함수 안에서는 := 사용 가능
}
```

#### 규칙 2: 같은 스코프에서 같은 변수명 재선언 불가
```go
func main() {
    x := 1
    x := 2  // ← 에러! x는 이미 선언됨
    x = 2   // ← OK! 재할당은 = 사용
}
```

#### 규칙 3: 새 변수가 하나 이상 있으면 기존 변수와 함께 사용 가능
```go
func main() {
    x := 1
    x, y := 2, 3  // ← OK! y가 새 변수라서 허용됨
                   // x는 재할당, y는 새 선언
    fmt.Println(x, y)  // 2 3
}
```

#### 규칙 4: = 과 := 의 차이
```go
x := 10   // 선언 + 할당 (변수가 없을 때 처음 만들 때)
x = 20    // 할당만 (이미 있는 변수에 새 값 넣을 때)
```

---

## 10. Basic Types

### 전체 타입 목록

#### 정수형
```
int    → 가장 많이 씀. 32비트 시스템이면 32비트, 64비트면 64비트
int8   → -128 ~ 127
int16  → -32,768 ~ 32,767
int32  → -2,147,483,648 ~ 2,147,483,647
int64  → -9,223,372,036,854,775,808 ~ 9,223,372,036,854,775,807
uint   → 0 이상의 정수 (양수만)
uint8  → 0 ~ 255 (byte와 동일)
uint16 → 0 ~ 65,535
uint32 → 0 ~ 4,294,967,295
uint64 → 0 ~ 매우 큰 수
```

#### 실수형
```
float32 → 소수점 (정밀도 낮음, 약 7자리)
float64 → 소수점 (정밀도 높음, 약 15자리) ← 가장 많이 씀
```

#### 불리언
```
bool → true 또는 false만 가능
```

#### 문자열
```
string → "큰따옴표로 감싼 문자열"
byte   → uint8과 동일. 문자 하나 (ASCII)
rune   → int32와 동일. 유니코드 문자 하나 (한글, 한자 등)
```

### 언제 어떤 타입을 쓰나요?

```
일반적인 정수    → int
매우 큰 정수     → int64
양수만인 정수    → uint
소수점 있는 수   → float64
참/거짓          → bool
텍스트           → string
ASCII 문자 하나  → byte
유니코드 문자    → rune (한글 처리할 때)
```

### Python이랑 비교

```python
# Python: 타입이 자동으로 결정됨
x = 42        # 자동으로 int
y = 3.14      # 자동으로 float
z = "hello"   # 자동으로 str
b = True      # 자동으로 bool
```

```go
// Go: 타입을 명시하거나 추론됨
var x int = 42
var y float64 = 3.14
var z string = "hello"
var b bool = true

// 또는 추론 방식
x := 42      // int
y := 3.14    // float64
z := "hello" // string
b := true    // bool
```

---

## 11. Zero Values

### Zero Value란?
변수를 선언할 때 값을 주지 않으면 자동으로 할당되는 기본값입니다.

```go
var x int        // x = 0
var y float64    // y = 0.0
var z string     // z = "" (빈 문자열)
var b bool       // b = false
```

### 타입별 Zero Value

| 타입 | Zero Value | 의미 |
|------|-----------|------|
| int, float64 등 숫자 | `0` | 숫자 0 |
| bool | `false` | 거짓 |
| string | `""` | 빈 문자열 |
| pointer | `nil` | 가리키는 곳 없음 |
| slice | `nil` | 비어있음 |
| map | `nil` | 비어있음 |
| channel | `nil` | 비어있음 |

### nil이란?
Python의 `None`과 비슷합니다.  
"아무것도 없음", "존재하지 않음"을 의미합니다.

```go
var p *int    // 포인터, zero value = nil
var s []int   // 슬라이스, zero value = nil

if p == nil {
    fmt.Println("p는 아무것도 가리키지 않음")
}
```

### Python이랑 비교

```python
# Python: 선언만 하면 undefined → 에러
x  # NameError: name 'x' is not defined
```

```go
// Go: 선언만 해도 항상 안전한 기본값 있음
var x int
fmt.Println(x)  // 0 출력, 에러 없음
```

Go가 더 안전합니다. 초기화 안 해도 항상 예측 가능한 값을 가집니다.

---

## 12. Type Conversions

### Go는 자동 타입 변환이 없다

이것이 Python과 가장 큰 차이점입니다.

```python
# Python: 자동 변환
x = 1 + 1.5    # int + float → float 자동 변환
print(x)        # 2.5
```

```go
// Go: 자동 변환 없음 → 에러!
var x int = 1
var y float64 = 1.5
z := x + y  // 에러! int + float64 연산 불가

// 해결: 명시적 변환
z := float64(x) + y  // int를 float64로 변환 후 연산
```

### 변환 방법: 원하는타입(값)

```go
// 숫자 간 변환
var i int = 42
f := float64(i)    // int → float64: 42.0
j := int(3.99)     // float64 → int: 3 (소수점 버림!)
k := int(-3.99)    // float64 → int: -3 (버림, 반올림 아님!)

// 주의: 소수점은 반올림이 아니라 버림!
fmt.Println(int(9.9))   // 9 (10이 아님!)
fmt.Println(int(3.01))  // 3
fmt.Println(int(-3.9))  // -3 (절대값 기준 버림)
```

### ★ 숫자 ↔ 문자열 변환 주의사항

```go
// ❌ 잘못된 방법
s := string(65)          // "A" (65는 ASCII 코드 'A')
s2 := string(9829)       // "♥" (유니코드로 해석)

// ✅ 올바른 방법: strconv 패키지 사용
import "strconv"

s := strconv.Itoa(65)    // "65" (숫자를 문자열로)
i, err := strconv.Atoi("65")  // 65, nil (문자열을 숫자로)
```

### strconv 자주 쓰는 함수

```go
// 정수 ↔ 문자열
strconv.Itoa(42)         // int → string: "42"
strconv.Atoi("42")       // string → int: 42, nil(에러)

// 실수 ↔ 문자열
strconv.FormatFloat(3.14, 'f', 2, 64)  // float64 → "3.14"
// 3.14:바꾸고 싶은 실제 실수 숫자
// 'f': 일반적인 소수점 형식으로 (3.14e+00)이 아닌 3.140000으로
// 2: 정밀도, 소수점 아래 2째자리 까지 보여줌
// 64: 비트수, float32,float64인지 
strconv.ParseFloat("3.14", 64)          // string → 3.14, nil
//64는 비트수

// 불리언 ↔ 문자열
strconv.FormatBool(true)   // bool → "true"
//컴퓨터 내부의 조건 판단 결과인 true를 눈에 보이는 글자인 "true"로 바꿔줍니다.
strconv.ParseBool("true")  // string → true, nil
//이 함수도 마찬가지로 "오류글자" 같은 엉뚱한 텍스트가 들어오면 실패할 수 있기 때문에, [변환된 결과, 에러 주머니]를 함께 돌려줍니다.
//겉보기에는 똑같이 true로 보이지만, 컴퓨터 입장에서는 글자 상자에서 꺼내서 진짜 조건문(if)에 쓸 수 있는 데이터로 변한 것입니다.

// Format으로 시작하는 함수: 데이터를 가져와서 예쁘게 포맷(글자 화)한다는 뜻 ➡️ 데이터를 문자열로!
// Parse로 시작하는 함수: 글자를 분석(파싱)해서 알맹이를 꺼낸다는 뜻 ➡️ 문자열을 데이터로! (실패할 수 있으므로 에러 주머니 동반)
```

---

## 13. Type Inference

### 타입 추론이란?
변수의 타입을 직접 쓰지 않아도, 오른쪽 값을 보고 자동으로 타입을 결정하는 것입니다.

```go
x := 42         // 42는 정수니까 → int
y := 3.14       // 3.14는 소수니까 → float64
z := "hello"    // "hello"는 문자열이니까 → string
b := true       // true는 불리언이니까 → bool
```

### 타입 추론 규칙

```go
정수 리터럴  → int     (int64가 아님!)
실수 리터럴  → float64 (float32가 아님!)
문자열      → string
불리언      → bool
문자(작은따옴표) → rune (int32)
```

### 확인하는 방법: %T

```go
x := 42
fmt.Printf("%T\n", x)  // int 출력

y := 3.14
fmt.Printf("%T\n", y)  // float64 출력
```

### 원하는 타입이 추론 타입과 다를 때

```go
// 42는 int로 추론되지만 float64로 쓰고 싶을 때
var x float64 = 42    // 명시적 타입 지정
// 또는
x := float64(42)      // 변환

// "100"을 int로 쓰고 싶을 때
n, _ := strconv.Atoi("100")  // "100" → 100 (int)
```

---

## 14. Constants

### 상수란?
한번 선언하면 절대 변경할 수 없는 값입니다.

```go
const Pi = 3.14159

Pi = 3.14  // ← 에러! 상수는 변경 불가
```

### 선언 방법

```go
// 단일 상수
const MaxSize = 100
const AppName = "MyApp"
const Debug = false

// 여러 상수 한번에
const (
    MaxRetry = 3
    Timeout  = 30
    Version  = "1.0.0"
)
```

### var와 const 차이

```go
var x = 10    // 변수: 나중에 x = 20 으로 변경 가능
const y = 10  // 상수: 절대 변경 불가

x = 20   // OK
y = 20   // 에러!
```

### iota: 자동 증가 상수

`iota`는 `const` 블록 안에서 **0부터 1씩 자동으로 증가**하는 특별한 값입니다.

```go
const (
    A = iota  // 0
    B = iota  // 1
    C = iota  // 2
)

// iota는 생략 가능 (앞 줄의 표현식이 반복됨)
const (
    A = iota  // 0
    B         // 1 (iota 자동 반복)
    C         // 2
    D         // 3
)
```

### iota 실용 예시

```go
// 요일 (0=일요일, 1=월요일...)
const (
    Sunday = iota   // 0
    Monday          // 1
    Tuesday         // 2
    Wednesday       // 3
    Thursday        // 4
    Friday          // 5
    Saturday        // 6
)

// 서버 상태
const (
    StatusStopped = iota  // 0
    StatusStarting        // 1
    StatusRunning         // 2
    StatusStopping        // 3
)

// 파일 권한 (비트 플래그)
const (
    ReadPerm  = 1 << iota  // 1  (001)
    WritePerm               // 2  (010)
    ExecPerm                // 4  (100)
)
// 조합: ReadPerm | WritePerm = 3 (011)

// 첫 번째 iota 값 버리기
const (
    _        = iota        // 0 버림
    KB int64 = 1 << (10 * iota)  // 1024
    MB                     // 1048576
    GB                     // 1073741824
    TB                     // 1099511627776
)
```

---

## 15. 심화: 자주 쓰는 것들

### fmt 포맷 동사 (Verbs) 전체 정리

```go
// 숫자
fmt.Printf("%d", 42)      // 정수: 42
fmt.Printf("%b", 42)      // 이진수: 101010
fmt.Printf("%o", 42)      // 8진수: 52
fmt.Printf("%x", 42)      // 16진수 소문자: 2a
fmt.Printf("%X", 42)      // 16진수 대문자: 2A
fmt.Printf("%f", 3.14)    // 실수: 3.140000
fmt.Printf("%.2f", 3.14)  // 소수점 2자리: 3.14
fmt.Printf("%e", 3.14)    // 지수: 3.140000e+00

// 문자열
fmt.Printf("%s", "hello") // 문자열: hello
fmt.Printf("%q", "hello") // 따옴표 포함: "hello"

// 기타
fmt.Printf("%t", true)    // 불리언: true
fmt.Printf("%T", 42)      // 타입: int
fmt.Printf("%v", 42)      // 기본 형식: 42 (모든 타입에 사용 가능)
fmt.Printf("%%")           // % 기호 자체

// 너비와 정렬
fmt.Printf("%5d", 42)     // '   42' (너비 5, 오른쪽 정렬)
fmt.Printf("%-5d", 42)    // '42   ' (너비 5, 왼쪽 정렬)
fmt.Printf("%05d", 42)    // '00042' (너비 5, 0으로 채움)
```

### 문자열 자주 쓰는 조작

```go
import "strings"

s := "Hello, Go World!"

// 검색
strings.Contains(s, "Go")        // true (포함 여부)
strings.HasPrefix(s, "Hello")    // true (시작 여부)
strings.HasSuffix(s, "World!")   // true (끝 여부)
strings.Index(s, "Go")           // 7 (위치, 없으면 -1)
strings.Count(s, "l")            // 2 (개수)

// 변환
strings.ToUpper(s)               // "HELLO, GO WORLD!"
strings.ToLower(s)               // "hello, go world!"
strings.Replace(s, "Go", "Python", 1)   // 1번만 교체
strings.Replace(s, "l", "L", -1)        // 전체 교체 (-1)
strings.TrimSpace("  hello  ")   // "hello" (앞뒤 공백 제거)

// 분리·결합
strings.Split("a,b,c", ",")      // ["a", "b", "c"]
strings.Join([]string{"a","b"}, "-")  // "a-b"

// 길이
len(s)  // 17 (바이트 수)
// 주의: 한글은 3바이트라서 len("한글") = 6
```

### 연산자 정리

```go
// 산술 연산자
x + y   // 더하기
x - y   // 빼기
x * y   // 곱하기
x / y   // 나누기 (정수/정수 = 정수!)
x % y   // 나머지

// 비교 연산자 (결과는 bool)
x == y  // 같다
x != y  // 다르다
x < y   // 작다
x > y   // 크다
x <= y  // 작거나 같다
x >= y  // 크거나 같다

// 논리 연산자
x && y  // AND (Python의 and)
x || y  // OR  (Python의 or)
!x      // NOT (Python의 not)

// 증감 연산자
x++     // x = x + 1 (후위만 가능, ++x 불가)
x--     // x = x - 1

// 비트 연산자
x & y   // AND
x | y   // OR
x ^ y   // XOR
x << 1  // 왼쪽 시프트 (×2)
x >> 1  // 오른쪽 시프트 (÷2)
```

### 자주 하는 실수 TOP 5

```
실수 1: import 했는데 안 씀
  → "imported and not used" 에러
  → 해결: 사용하거나 제거

실수 2: 변수 선언했는데 안 씀
  → "declared but not used" 에러
  → 해결: 사용하거나 _ = 변수명

실수 3: int + float64 연산
  → "mismatched types" 에러
  → 해결: float64(intVar) + floatVar

실수 4: string(숫자) = ASCII 변환
  → string(65) = "A" (숫자로 변환 안 됨)
  → 해결: strconv.Itoa(65) = "65"

실수 5: { 을 다음 줄에 쓰기
  → syntax error
  → 해결: 반드시 같은 줄에 {
```

---

## 실행 예제 코드

아래 코드를 `practice.go`로 저장하고 `go run practice.go`로 실행하세요.

```go
package main

import (
    "fmt"
    "strings"
    "strconv"
    "math"
)

func main() {
    // 변수 선언 연습
    name := "정성윤"
    age := 31
    height := 175.5
    isPassed := true

    fmt.Printf("이름: %s, 나이: %d, 키: %.1f, 합격: %t\n",
        name, age, height, isPassed)

    // 타입 확인
    fmt.Printf("타입: %T, %T, %T, %T\n",
        name, age, height, isPassed)

    // 타입 변환
    ageFloat := float64(age)
    fmt.Printf("나이(float): %.1f\n", ageFloat)

    // 문자열 ↔ 숫자
    numStr := strconv.Itoa(age)
    fmt.Printf("나이(문자열): %s\n", numStr)

    // 문자열 조작
    upperName := strings.ToUpper(name)
    fmt.Printf("대문자: %s\n", upperName)

    // 수학 계산
    fmt.Printf("Sqrt(144) = %.0f\n", math.Sqrt(144))

    // 상수
    const MaxScore = 100
    fmt.Printf("최고점: %d\n", MaxScore)
}
```

---
