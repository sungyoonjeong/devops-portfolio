# 🐹 Go 언어 완전 입문서 — 챕터 46~60
> 메서드·인터페이스 완전 정리
> Go에서 가장 중요한 개념 — 면접에도 자주 나옴

---

## 목차
46. [Methods 기본](#46-methods-기본)
47. [Methods are Functions](#47-methods-are-functions)
48. [Pointer Receivers](#48-pointer-receivers)
49. [Pointers and Functions](#49-pointers-and-functions)
50. [Methods and Pointer Indirection 1](#50-methods-and-pointer-indirection-1)
51. [Methods and Pointer Indirection 2](#51-methods-and-pointer-indirection-2)
52. [Value vs Pointer Receiver 선택](#52-value-vs-pointer-receiver-선택)
53. [Interfaces 기본](#53-interfaces-기본)
54. [암묵적 인터페이스 구현](#54-암묵적-인터페이스-구현)
55. [Interface Values](#55-interface-values)
56. [Nil Underlying Values](#56-nil-underlying-values)
57. [Nil Interface Values](#57-nil-interface-values)
58. [Empty Interface (빈 인터페이스)](#58-empty-interface-빈-인터페이스)
59. [Type Assertions](#59-type-assertions)
60. [Type Switches](#60-type-switches)
- [실전 종합 코드](#실전-종합-코드)
- [자주 하는 실수](#자주-하는-실수)

---

## 46. Methods 기본

### 메서드란?
특정 타입에 연결된 함수입니다.
`func (리시버) 함수명()` 형태로 선언합니다.

```go
// 일반 함수
func add(x, y int) int {
    return x + y
}

// 메서드: 특정 타입에 연결
type Rectangle struct {
    Width  float64
    Height float64
}

// (r Rectangle) = 리시버: "이 메서드는 Rectangle 타입에 속한다"
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

func (r Rectangle) Perimeter() float64 {
    return 2 * (r.Width + r.Height)
}
```

### 메서드 호출

```go
rect := Rectangle{Width: 10, Height: 5}

// 점(.)으로 메서드 호출
area := rect.Area()
fmt.Println(area)       // 50
fmt.Println(rect.Perimeter())  // 30
```

### Python 클래스와 비교

```python
# Python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):           # self = Python의 리시버
        return self.width * self.height

rect = Rectangle(10, 5)
print(rect.area())   # 50
```

```go
// Go
type Rectangle struct {
    Width  float64
    Height float64
}

func (r Rectangle) Area() float64 {  // r = Go의 리시버
    return r.Width * r.Height
}

rect := Rectangle{Width: 10, Height: 5}
fmt.Println(rect.Area())  // 50
```

### 리시버 이름 규칙

```go
// 리시버 이름은 타입 첫 글자 소문자 사용 (관례)
func (r Rectangle) Area() float64 { ... }   // Rectangle → r
func (s Server) Start() { ... }              // Server → s
func (p Person) Name() string { ... }        // Person → p
```

### 구조체 외에도 메서드 가능

```go
// 같은 패키지 안의 어떤 타입에도 메서드 정의 가능
type MyFloat float64

func (f MyFloat) Abs() float64 {
    if f < 0 {
        return float64(-f)
    }
    return float64(f)
}

f := MyFloat(-3.14)
fmt.Println(f.Abs())  // 3.14
```

---

## 47. Methods are Functions

### 메서드는 사실 함수다

메서드는 리시버를 첫 번째 인수로 받는 함수입니다.
둘은 완전히 동일한 동작을 합니다.

```go
type Rectangle struct {
    Width, Height float64
}

// 메서드 방식
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 함수 방식 (동일한 동작)
func Area(r Rectangle) float64 {
    return r.Width * r.Height
}

rect := Rectangle{10, 5}
fmt.Println(rect.Area())    // 50 (메서드)
fmt.Println(Area(rect))     // 50 (함수)
```

### 언제 메서드를 쓰고 언제 함수를 쓰나?

```
메서드: 특정 타입과 강하게 연관된 동작
  → rect.Area(), server.Start(), user.Validate()

함수: 여러 타입을 다루거나 독립적인 동작
  → calculateTax(amount, rate), formatDate(t)
```

---

## 48. Pointer Receivers

### 포인터 리시버란?
리시버를 값이 아닌 포인터로 받는 메서드입니다.

```go
type Rectangle struct {
    Width  float64
    Height float64
}

// 값 리시버: 복사본으로 동작 (원본 수정 불가)
func (r Rectangle) Scale(factor float64) {
    r.Width *= factor   // 복사본 수정, 원본 그대로
    r.Height *= factor
}

// 포인터 리시버: 원본으로 동작 (원본 수정 가능)
func (r *Rectangle) ScalePtr(factor float64) {
    r.Width *= factor   // 원본 수정
    r.Height *= factor
}
```

### 차이 확인

```go
rect := Rectangle{Width: 10, Height: 5}

rect.Scale(2)
fmt.Println(rect)     // {10 5} ← 원본 그대로!

rect.ScalePtr(2)
fmt.Println(rect)     // {20 10} ← 원본 수정됨!
```

### 포인터 리시버가 필요한 2가지 경우

```
경우 1: 메서드가 구조체 필드를 수정해야 할 때
  → func (r *Rectangle) Scale() → r.Width 수정

경우 2: 구조체가 클 때 (복사 비용 절약)
  → 작은 구조체: 값 리시버 OK
  → 큰 구조체: 포인터 리시버 권장
```

### DevOps 실전 예시

```go
type Server struct {
    Host    string
    CPU     float64
    IsAlive bool
}

// CPU 업데이트 → 원본 수정 필요 → 포인터 리시버
func (s *Server) UpdateCPU(cpu float64) {
    s.CPU = cpu
}

// 상태 확인 → 읽기만 → 값 리시버
func (s Server) IsHealthy() bool {
    return s.IsAlive && s.CPU < 90
}

server := Server{Host: "web-01", CPU: 45.0, IsAlive: true}
server.UpdateCPU(92.5)              // 원본 수정됨
fmt.Println(server.IsHealthy())     // false (CPU > 90)
```

---

## 49. Pointers and Functions

### 함수에서 포인터 리시버와 값 리시버 차이

```go
type Vertex struct {
    X, Y float64
}

// 값으로 받는 함수 → 원본 수정 불가
func ScaleByValue(v Vertex, f float64) {
    v.X *= f
    v.Y *= f
}

// 포인터로 받는 함수 → 원본 수정 가능
func ScaleByPointer(v *Vertex, f float64) {
    v.X *= f
    v.Y *= f
}

v := Vertex{3, 4}

ScaleByValue(v, 2)
fmt.Println(v)     // {3 4} 그대로

ScaleByPointer(&v, 2)
fmt.Println(v)     // {6 8} 수정됨
```

### 메모리로 이해

```
값 리시버:
  v = {X:3, Y:4}
  함수로 전달 시: 복사본 {X:3, Y:4} 생성
  복사본 수정 → 원본 영향 없음

포인터 리시버:
  v = {X:3, Y:4} (주소: 0xc000)
  &v = 0xc000 (주소 전달)
  0xc000 주소의 값 수정 → 원본 직접 수정
```

---

## 50. Methods and Pointer Indirection 1

### Go의 편의 기능: 자동 역참조

포인터 리시버 메서드를 값 변수로 호출해도 자동으로 처리됩니다.

```go
type Vertex struct{ X, Y float64 }

func (v *Vertex) Scale(f float64) {
    v.X *= f
    v.Y *= f
}

v := Vertex{3, 4}   // 값 변수

// 원래는 (&v).Scale(2) 라고 써야 하지만
// Go가 자동으로 &v로 변환해줌
v.Scale(2)           // Go가 (&v).Scale(2)로 자동 처리
fmt.Println(v)       // {6 8}

p := &v              // 포인터 변수
p.Scale(2)           // 포인터로 직접 호출
fmt.Println(v)       // {12 16}
```

---

## 51. Methods and Pointer Indirection 2

### 반대 방향도 자동 처리

값 리시버 메서드를 포인터 변수로 호출해도 자동 역참조됩니다.

```go
type Vertex struct{ X, Y float64 }

func (v Vertex) Abs() float64 {
    return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

v := Vertex{3, 4}
p := &v

// 원래는 (*p).Abs() 라고 써야 하지만
// Go가 자동으로 *p로 역참조
fmt.Println(p.Abs())   // 5 (Go가 (*p).Abs()로 자동 처리)
fmt.Println(v.Abs())   // 5
```

### 정리

```
포인터 리시버 메서드를 값으로 호출    → Go가 자동으로 & 붙여줌
값 리시버 메서드를 포인터로 호출      → Go가 자동으로 * 붙여줌

→ 실무에서는 그냥 .으로 호출하면 됨
  Go가 알아서 처리해줌
```

---

## 52. Value vs Pointer Receiver 선택

### 결정 기준

```
포인터 리시버 (*T) 사용:
  ① 메서드가 구조체 필드를 수정해야 할 때 (필수)
  ② 구조체가 클 때 (성능)

값 리시버 (T) 사용:
  ① 읽기만 하고 수정 안 할 때
  ② 작은 구조체 (int, string 등 기본 타입 수준)
  ③ 불변(immutable) 객체로 만들 때
```

### 일관성 원칙 (★ 중요)

```go
type Server struct {
    Host string
    CPU  float64
}

// 나쁜 예: 같은 타입에 값·포인터 리시버 혼용
func (s Server) GetHost() string { return s.Host }    // 값
func (s *Server) UpdateCPU(cpu float64) { s.CPU = cpu } // 포인터

// 좋은 예: 하나로 통일 (수정 메서드 있으면 전부 포인터)
func (s *Server) GetHost() string { return s.Host }    // 포인터
func (s *Server) UpdateCPU(cpu float64) { s.CPU = cpu } // 포인터
```

**규칙: 한 타입에 포인터 리시버 메서드가 하나라도 있으면 전부 포인터 리시버로 통일**

---

## 53. Interfaces 기본

### 인터페이스란?
메서드들의 집합을 정의하는 타입입니다.
"이 메서드들을 가지고 있으면 이 인터페이스를 구현한 것"

```go
// 인터페이스 정의
type Animal interface {
    Sound() string   // 이 메서드를 구현하면 Animal
    Name() string    // 이 메서드도 구현해야 Animal
}
```

### 인터페이스 구현

```go
type Dog struct{}
type Cat struct{}

// Dog가 Animal 인터페이스 구현
func (d Dog) Sound() string { return "멍멍" }
func (d Dog) Name() string  { return "개" }

// Cat이 Animal 인터페이스 구현
func (c Cat) Sound() string { return "야옹" }
func (c Cat) Name() string  { return "고양이" }
```

### 인터페이스 변수

```go
var a Animal   // Animal 인터페이스 변수

a = Dog{}
fmt.Println(a.Sound())  // 멍멍
fmt.Println(a.Name())   // 개

a = Cat{}
fmt.Println(a.Sound())  // 야옹
fmt.Println(a.Name())   // 고양이
```

### Python과 비교

```python
# Python: ABC 또는 duck typing
from abc import ABC, abstractmethod

class Animal(ABC):
    @abstractmethod
    def sound(self): pass
    @abstractmethod
    def name(self): pass

class Dog(Animal):
    def sound(self): return "멍멍"
    def name(self): return "개"
```

```go
// Go: interface 키워드, 명시적 상속 없음
type Animal interface {
    Sound() string
    Name() string
}

type Dog struct{}
func (d Dog) Sound() string { return "멍멍" }
func (d Dog) Name() string  { return "개" }
// Dog는 자동으로 Animal 인터페이스 구현 완료
```

---

## 54. 암묵적 인터페이스 구현

### Go 인터페이스의 핵심 특징
**"implements" 키워드 없음. 메서드만 맞으면 자동 구현.**

```go
type Stringer interface {
    String() string
}

type Person struct {
    Name string
    Age  int
}

// Person이 Stringer를 구현한다고 어디에도 선언 안 함
// 그냥 String() 메서드만 있으면 자동으로 Stringer 구현
func (p Person) String() string {
    return fmt.Sprintf("%s (%d세)", p.Name, p.Age)
}

var s Stringer = Person{Name: "성윤", Age: 31}
fmt.Println(s.String())  // 성윤 (31세)
```

### Java와 비교

```java
// Java: implements 명시 필요
class Person implements Stringer {  // 명시적 선언
    public String string() { ... }
}
```

```go
// Go: 자동 구현 (명시 불필요)
type Person struct { ... }
func (p Person) String() string { ... }
// 끝. 자동으로 Stringer 구현됨
```

### 왜 암묵적 구현이 좋은가?

```
장점 1: 외부 패키지 타입도 인터페이스 구현 가능
  → 내가 만들지 않은 타입도 내 인터페이스에 맞출 수 있음

장점 2: 인터페이스와 구현이 분리됨
  → 결합도(coupling) 낮아짐
  → 테스트하기 쉬워짐
```

---

## 55. Interface Values

### 인터페이스 내부 구조

인터페이스 변수는 내부적으로 2가지를 가집니다.
```
(타입, 값) 쌍으로 저장
예: Animal 변수에 Dog{} 저장 → (Dog, Dog{})
    Animal 변수에 Cat{} 저장 → (Cat, Cat{})
```

```go
type Animal interface {
    Sound() string
}
type Dog struct{ Name string }
func (d Dog) Sound() string { return "멍멍" }

var a Animal
fmt.Printf("타입: %T, 값: %v\n", a, a)
// 타입: <nil>, 값: <nil>

a = Dog{Name: "뽀삐"}
fmt.Printf("타입: %T, 값: %v\n", a, a)
// 타입: main.Dog, 값: {뽀삐}
```

### 인터페이스로 다형성 구현

```go
type Shape interface {
    Area() float64
}

type Circle struct{ Radius float64 }
type Rectangle struct{ Width, Height float64 }

func (c Circle) Area() float64 {
    return math.Pi * c.Radius * c.Radius
}
func (r Rectangle) Area() float64 {
    return r.Width * r.Height
}

// 서로 다른 타입을 같은 인터페이스로 처리
shapes := []Shape{
    Circle{Radius: 5},
    Rectangle{Width: 10, Height: 3},
    Circle{Radius: 2},
}

for _, s := range shapes {
    fmt.Printf("넓이: %.2f\n", s.Area())
}
// 넓이: 78.54
// 넓이: 30.00
// 넓이: 12.57
```

---

## 56. Nil Underlying Values

### 인터페이스 변수에 nil 포인터 저장

```go
type Animal interface {
    Sound() string
}

type Dog struct{ Name string }
func (d *Dog) Sound() string {
    if d == nil {
        return "이름 없는 개"
    }
    return "멍멍 " + d.Name
}

var d *Dog = nil       // nil 포인터
var a Animal = d       // 인터페이스에 nil 포인터 저장

// a는 nil이 아님! (타입 정보는 있음: *Dog)
fmt.Println(a == nil)  // false
fmt.Println(a.Sound()) // "이름 없는 개" (nil 처리됨)
```

### 중요한 포인트

```
인터페이스 변수 = (타입, 값) 쌍
  nil 포인터 저장 시: (*Dog, nil) → 인터페이스는 nil 아님
  아무것도 없을 때:  (nil, nil)   → 인터페이스가 nil
```

---

## 57. Nil Interface Values

### 완전한 nil 인터페이스

```go
type Animal interface {
    Sound() string
}

var a Animal   // (nil, nil) → 완전한 nil 인터페이스

fmt.Println(a == nil)  // true

// nil 인터페이스 메서드 호출 → 패닉!
// a.Sound()  → 런타임 패닉!

// 안전하게 사용
if a != nil {
    fmt.Println(a.Sound())
}
```

---

## 58. Empty Interface (빈 인터페이스)

### 빈 인터페이스란?
메서드가 하나도 없는 인터페이스.
**모든 타입이 자동으로 구현 → 어떤 값이든 저장 가능**

```go
// interface{} = 빈 인터페이스 (모든 타입 수용)
var i interface{}

i = 42
fmt.Printf("타입: %T, 값: %v\n", i, i)  // int, 42

i = "hello"
fmt.Printf("타입: %T, 값: %v\n", i, i)  // string, hello

i = true
fmt.Printf("타입: %T, 값: %v\n", i, i)  // bool, true

i = []int{1, 2, 3}
fmt.Printf("타입: %T, 값: %v\n", i, i)  // []int, [1 2 3]
```

### Go 1.18+: any 키워드 (interface{} 별칭)

```go
// interface{} 와 완전히 동일
var i any = 42
var j any = "hello"
```

### 언제 쓰나?

```go
// 1. 여러 타입을 받는 함수
func describe(i interface{}) {
    fmt.Printf("타입: %T, 값: %v\n", i, i)
}

describe(42)
describe("hello")
describe(true)

// 2. JSON 파싱 (타입 미리 알 수 없을 때)
var result map[string]interface{}
json.Unmarshal(data, &result)
```

### Python 비교

```python
# Python: 모든 변수가 any 타입 (동적 타입)
x = 42
x = "hello"  # 타입 바꿔도 OK
x = [1, 2, 3]
```

```go
// Go: 명시적으로 interface{} 사용해야 여러 타입 가능
var x interface{}
x = 42
x = "hello"
x = []int{1, 2, 3}
```

---

## 59. Type Assertions

### 타입 어서션이란?
인터페이스 변수에서 실제 타입의 값을 꺼내는 방법

```go
var i interface{} = "hello"

// 방법 1: 직접 어서션 (실패 시 패닉)
s := i.(string)
fmt.Println(s)       // hello
fmt.Println(len(s))  // 5

// 틀린 타입으로 어서션 → 패닉!
// n := i.(int)  → 패닉!
```

### 안전한 타입 어서션 (ok 패턴)

```go
var i interface{} = "hello"

// 방법 2: ok 패턴 (실패해도 패닉 없음)
s, ok := i.(string)
fmt.Println(s, ok)    // hello true

n, ok := i.(int)
fmt.Println(n, ok)    // 0 false (패닉 없음!)

// if와 함께 사용
if s, ok := i.(string); ok {
    fmt.Printf("문자열: %s\n", s)
} else {
    fmt.Println("문자열이 아님")
}
```

### 실전 예시

```go
func processValue(i interface{}) {
    // 타입에 따라 다르게 처리
    if s, ok := i.(string); ok {
        fmt.Printf("문자열 처리: %s (길이: %d)\n", s, len(s))
        return
    }
    if n, ok := i.(int); ok {
        fmt.Printf("정수 처리: %d (두배: %d)\n", n, n*2)
        return
    }
    fmt.Printf("알 수 없는 타입: %T\n", i)
}

processValue("hello")   // 문자열 처리: hello (길이: 5)
processValue(42)         // 정수 처리: 42 (두배: 84)
processValue(3.14)       // 알 수 없는 타입: float64
```

---

## 60. Type Switches

### 타입 스위치란?
여러 타입을 한번에 검사하는 switch문.
Type Assertion을 여러 개 쓰는 것보다 훨씬 깔끔합니다.

```go
func describe(i interface{}) {
    switch v := i.(type) {    // i.(type) → 타입 스위치
    case int:
        fmt.Printf("정수: %d\n", v)
    case string:
        fmt.Printf("문자열: %s (길이: %d)\n", v, len(v))
    case bool:
        fmt.Printf("불리언: %t\n", v)
    case []int:
        fmt.Printf("정수 슬라이스: %v (길이: %d)\n", v, len(v))
    default:
        fmt.Printf("알 수 없는 타입: %T\n", v)
    }
}

describe(42)              // 정수: 42
describe("hello")          // 문자열: hello (길이: 5)
describe(true)             // 불리언: true
describe([]int{1, 2, 3})  // 정수 슬라이스: [1 2 3] (길이: 3)
describe(3.14)             // 알 수 없는 타입: float64
```

### 챕터 24와 비교

```go
// 챕터 24: 일반 타입 스위치 (이미 배움)
switch x {
case 1: ...
case 2: ...
}

// 챕터 60: 타입 스위치 (인터페이스의 실제 타입 검사)
switch v := i.(type) {
case int: ...
case string: ...
}
```

### DevOps 실전 예시

```go
// 설정 값이 다양한 타입일 때
type Config map[string]interface{}

func printConfig(key string, value interface{}) {
    switch v := value.(type) {
    case string:
        fmt.Printf("[%s] 문자열: %s\n", key, v)
    case int:
        fmt.Printf("[%s] 정수: %d\n", key, v)
    case bool:
        fmt.Printf("[%s] 불리언: %t\n", key, v)
    case []string:
        fmt.Printf("[%s] 문자열 배열: %v\n", key, v)
    default:
        fmt.Printf("[%s] 타입: %T, 값: %v\n", key, v, v)
    }
}

config := Config{
    "host":    "localhost",
    "port":    8080,
    "debug":   true,
    "servers": []string{"web-01", "web-02"},
}

for k, v := range config {
    printConfig(k, v)
}
```

---

## 실전 종합 코드

`practice_ch46_60.go`로 저장 후 `go run practice_ch46_60.go` 실행:

```go
package main

import (
    "fmt"
    "math"
)

// ── 메서드 ──────────────────────────────────────

type Server struct {
    Host    string
    CPU     float64
    Memory  float64
    IsAlive bool
}

// 포인터 리시버: 원본 수정
func (s *Server) UpdateMetrics(cpu, mem float64) {
    s.CPU = cpu
    s.Memory = mem
}

// 포인터 리시버: 읽기 (통일성)
func (s *Server) Status() string {
    if !s.IsAlive {
        return "🔴 오프라인"
    }
    if s.CPU > 90 || s.Memory > 90 {
        return "🟡 위험"
    }
    return "🟢 정상"
}

func (s *Server) String() string {
    return fmt.Sprintf("%s | CPU:%.1f%% MEM:%.1f%% | %s",
        s.Host, s.CPU, s.Memory, s.Status())
}

// ── 인터페이스 ──────────────────────────────────

type Alertable interface {
    ShouldAlert() bool
    AlertMessage() string
}

// Server가 Alertable 암묵적 구현
func (s *Server) ShouldAlert() bool {
    return s.CPU > 80 || s.Memory > 85 || !s.IsAlive
}

func (s *Server) AlertMessage() string {
    if !s.IsAlive {
        return fmt.Sprintf("🔴 %s 서버 다운!", s.Host)
    }
    if s.CPU > 80 {
        return fmt.Sprintf("⚠️  %s CPU 위험: %.1f%%", s.Host, s.CPU)
    }
    return fmt.Sprintf("⚠️  %s 메모리 위험: %.1f%%", s.Host, s.Memory)
}

// Shape 인터페이스
type Shape interface {
    Area() float64
    Perimeter() float64
}

type Circle struct{ Radius float64 }
type Rectangle struct{ Width, Height float64 }

func (c Circle) Area() float64      { return math.Pi * c.Radius * c.Radius }
func (c Circle) Perimeter() float64 { return 2 * math.Pi * c.Radius }
func (r Rectangle) Area() float64      { return r.Width * r.Height }
func (r Rectangle) Perimeter() float64 { return 2 * (r.Width + r.Height) }

func printShape(s Shape) {
    fmt.Printf("타입: %T | 넓이: %.2f | 둘레: %.2f\n",
        s, s.Area(), s.Perimeter())
}

// ── 빈 인터페이스 + 타입 스위치 ─────────────────

func describeValue(i interface{}) string {
    switch v := i.(type) {
    case int:
        return fmt.Sprintf("정수 %d", v)
    case float64:
        return fmt.Sprintf("실수 %.2f", v)
    case string:
        return fmt.Sprintf("문자열 '%s'", v)
    case bool:
        if v {
            return "참"
        }
        return "거짓"
    case []string:
        return fmt.Sprintf("문자열 배열 %v", v)
    default:
        return fmt.Sprintf("알 수 없음(%T)", v)
    }
}

func main() {
    // 메서드
    fmt.Println("=== 서버 모니터링 ===")
    servers := []*Server{
        {Host: "web-01", CPU: 92.5, Memory: 78.3, IsAlive: true},
        {Host: "web-02", CPU: 45.0, Memory: 62.1, IsAlive: true},
        {Host: "db-01",  CPU: 33.0, Memory: 87.5, IsAlive: true},
        {Host: "cache-01", CPU: 0, Memory: 0, IsAlive: false},
    }

    for _, s := range servers {
        fmt.Println(s.String())
    }

    // 인터페이스
    fmt.Println("\n=== 알림 확인 ===")
    for _, s := range servers {
        var a Alertable = s
        if a.ShouldAlert() {
            fmt.Println(a.AlertMessage())
        }
    }

    // 메트릭 업데이트 (포인터 리시버)
    fmt.Println("\n=== 메트릭 업데이트 ===")
    servers[1].UpdateMetrics(95.3, 88.1)
    fmt.Println(servers[1].String())

    // Shape 인터페이스
    fmt.Println("\n=== 도형 넓이 ===")
    shapes := []Shape{
        Circle{Radius: 5},
        Rectangle{Width: 10, Height: 3},
        Circle{Radius: 2.5},
    }
    for _, s := range shapes {
        printShape(s)
    }

    // 빈 인터페이스 + 타입 스위치
    fmt.Println("\n=== 타입 스위치 ===")
    values := []interface{}{
        42, 3.14, "DevOps", true,
        []string{"web-01", "db-01"},
    }
    for _, v := range values {
        fmt.Println(describeValue(v))
    }
}
```

---

## 자주 하는 실수

### 실수 1: 값 리시버로 원본 수정 시도
```go
type Counter struct{ Count int }

// 잘못됨: 값 리시버로 수정 시도
func (c Counter) Increment() {
    c.Count++  // 복사본 수정, 원본 그대로
}

// 올바름: 포인터 리시버
func (c *Counter) Increment() {
    c.Count++  // 원본 수정
}
```

### 실수 2: nil 인터페이스 메서드 호출
```go
var a Animal   // nil 인터페이스
a.Sound()      // 패닉!

// 안전하게
if a != nil {
    a.Sound()
}
```

### 실수 3: 타입 어서션 실패 시 패닉
```go
var i interface{} = "hello"
n := i.(int)      // 패닉!

// 안전하게
n, ok := i.(int)
if ok {
    fmt.Println(n)
}
```

### 실수 4: 인터페이스 일부만 구현
```go
type Animal interface {
    Sound() string
    Name() string
}

type Dog struct{}
func (d Dog) Sound() string { return "멍멍" }
// Name() 구현 안 함

var a Animal = Dog{}  // 컴파일 에러!
// "Dog does not implement Animal (missing Name method)"
```

### 실수 5: 포인터·값 리시버 혼용
```go
type Server struct{ CPU float64 }

func (s Server) GetCPU() float64 { return s.CPU }   // 값
func (s *Server) SetCPU(v float64) { s.CPU = v }    // 포인터

// 인터페이스로 사용 시 혼란 발생
// → 하나로 통일 (보통 포인터로)
```

---

## 챕터별 핵심 한줄 요약

| 챕터 | 핵심 |
|------|------|
| 46 | func (r 타입) 메서드명() → 특정 타입에 함수 연결 |
| 47 | 메서드 = 리시버를 첫 인수로 받는 함수와 동일 |
| 48 | func (r *타입) → 포인터 리시버: 원본 수정 가능 |
| 49 | 함수도 포인터로 받으면 원본 수정 가능 |
| 50 | 값 변수로 포인터 리시버 호출 → Go가 자동으로 & 붙임 |
| 51 | 포인터 변수로 값 리시버 호출 → Go가 자동으로 * 붙임 |
| 52 | 수정 필요 or 큰 구조체 → 포인터. 같은 타입은 통일 |
| 53 | interface = 메서드 집합 정의. 구현하면 그 타입이 됨 |
| 54 | implements 없음. 메서드만 맞으면 자동 구현 |
| 55 | 인터페이스 변수 내부 = (타입, 값) 쌍 |
| 56 | nil 포인터를 인터페이스에 넣어도 인터페이스는 nil 아님 |
| 57 | 완전한 nil 인터페이스 = (nil, nil). 메서드 호출 시 패닉 |
| 58 | interface{} = 빈 인터페이스, 모든 타입 수용 |
| 59 | v, ok := i.(타입) → 안전한 타입 변환, 실패해도 패닉 없음 |
| 60 | switch v := i.(type) → 여러 타입 한번에 분기 처리 |

---

