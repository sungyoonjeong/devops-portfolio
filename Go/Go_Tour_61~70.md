# 🐹 Go 언어 완전 입문서 — 챕터 61~70 (마지막)
> 동시성(Concurrency) 완전 정리 — Goroutine·Channel·Select·Mutex  
> Go가 가장 강력한 영역 — 면접 단골 + DevOps 핵심

---

## 목차
61. [Goroutines (고루틴)](#61-goroutines-고루틴)
62. [Channels (채널)](#62-channels-채널)
63. [Buffered Channels (버퍼 채널)](#63-buffered-channels-버퍼-채널)
64. [Range & Close](#64-range--close)
65. [Select](#65-select)
66. [Default Selection](#66-default-selection)
67. [sync.Mutex (뮤텍스)](#67-syncmutex-뮤텍스)
68. [sync.WaitGroup](#68-syncwaitgroup)
69. [실전: 동시 다운로드](#69-실전-동시-다운로드)
70. [실전: 웹 크롤러 패턴](#70-실전-웹-크롤러-패턴)
- [실전 종합 코드](#실전-종합-코드)
- [자주 하는 실수](#자주-하는-실수)
- [동시성 핵심 정리](#동시성-핵심-정리)

---

## 동시성이 왜 중요한가? (시작 전 개념)

```
일반 프로그램: 한 번에 하나씩 순서대로 실행 (순차)
  작업1 끝 → 작업2 끝 → 작업3 끝
  총 시간 = 1 + 2 + 3 = 6초

동시성 프로그램: 여러 작업을 동시에 실행
  작업1, 작업2, 작업3 동시 시작
  총 시간 = 가장 오래 걸리는 작업 = 3초

DevOps에서 왜 중요한가:
  100대 서버에 동시에 헬스체크
  여러 API를 동시에 호출
  로그를 병렬로 처리
  → Go의 동시성이 압도적으로 강력
```

Go는 **고루틴(goroutine)**과 **채널(channel)**로 동시성을 매우 쉽게 구현합니다.

---

## 61. Goroutines (고루틴)

### 고루틴이란?
Go 런타임이 관리하는 **초경량 스레드**입니다.
함수 앞에 `go`만 붙이면 그 함수가 동시에 실행됩니다.

```go
go 함수명()   // 이 함수를 고루틴으로 실행 (동시 실행)
```

### 기본 예제

```go
package main

import (
    "fmt"
    "time"
)

func say(s string) {
    for i := 0; i < 3; i++ {
        fmt.Println(s)
        time.Sleep(100 * time.Millisecond)
    }
}

func main() {
    go say("고루틴")  // 동시 실행 (별도 고루틴)
    say("메인")       // 메인에서 실행

    // 출력 순서가 섞임 (동시 실행되므로)
    // 메인
    // 고루틴
    // 메인
    // 고루틴
    // ...
}
```

### ★ 중요: main이 끝나면 고루틴도 죽는다

```go
func main() {
    go say("고루틴")  // 고루틴 시작
    // main이 바로 끝나버림
    // → 고루틴이 실행될 시간도 없이 프로그램 종료!
}
// 출력: (아무것도 안 나올 수 있음)

// 해결: main이 기다리게 만들기
func main() {
    go say("고루틴")
    time.Sleep(1 * time.Second)  // 1초 대기 (임시 방법)
}
// 더 좋은 방법: WaitGroup 또는 Channel (뒤에서 설명)
```

### Python과 비교

```python
# Python: threading 모듈 (복잡함)
import threading

def say(s):
    for _ in range(3):
        print(s)

t = threading.Thread(target=say, args=("스레드",))
t.start()
say("메인")
t.join()  # 스레드 끝날 때까지 대기
```

```go
// Go: go 키워드 하나로 끝 (간단함)
go say("고루틴")
say("메인")
```

### 고루틴의 강점

```
일반 OS 스레드: 1개에 약 1MB 메모리
고루틴:         1개에 약 2KB 메모리

→ 고루틴은 수만~수십만 개 동시 실행 가능
→ OS 스레드는 수천 개가 한계
```

---

## 62. Channels (채널)

### 채널이란?
고루틴 사이에 **데이터를 주고받는 통로**입니다.
고루틴끼리 안전하게 값을 전달할 수 있습니다.

```go
// 채널 생성
ch := make(chan int)   // int를 주고받는 채널

// 채널에 값 보내기
ch <- 42   // 42를 채널에 보냄

// 채널에서 값 받기
x := <-ch  // 채널에서 값을 받아 x에 저장
```

### 화살표 방향 기억법

```go
ch <- v    // 채널로 v를 보냄 (화살표가 ch 쪽으로)
v := <-ch  // 채널에서 받아서 v에 (화살표가 v 쪽으로)
```

### 기본 예제

```go
package main

import "fmt"

func sum(nums []int, ch chan int) {
    total := 0
    for _, n := range nums {
        total += n
    }
    ch <- total   // 결과를 채널로 보냄
}

func main() {
    nums := []int{1, 2, 3, 4, 5, 6}

    ch := make(chan int)

    // 절반씩 나눠서 동시에 계산
    go sum(nums[:3], ch)  // 1+2+3 = 6
    go sum(nums[3:], ch)  // 4+5+6 = 15

    x := <-ch  // 첫 번째 결과
    y := <-ch  // 두 번째 결과

    fmt.Println(x, y, x+y)  // 6 15 21 (또는 15 6 21)
}
```

### ★ 채널은 동기화 도구

```go
// 채널은 값을 받을 때까지 기다림 (블로킹)
ch := make(chan int)

go func() {
    fmt.Println("고루틴 작업 중...")
    ch <- 1  // 작업 완료 신호
}()

<-ch  // 신호 올 때까지 여기서 대기
fmt.Println("고루틴 완료됨")
// → time.Sleep 없이도 고루틴 완료를 기다릴 수 있음!
```

---

## 63. Buffered Channels (버퍼 채널)

### 버퍼 채널이란?
값을 **여러 개 저장**할 수 있는 채널입니다.

```go
// make(chan 타입, 버퍼크기)
ch := make(chan int, 2)  // 2개까지 저장 가능

ch <- 1   // OK (버퍼에 1개)
ch <- 2   // OK (버퍼에 2개)
// ch <- 3  // 버퍼 가득 참 → 블로킹! (누가 받아갈 때까지 대기)

fmt.Println(<-ch)  // 1
fmt.Println(<-ch)  // 2
```

### 버퍼 없는 채널 vs 버퍼 채널

```go
// 버퍼 없는 채널 (unbuffered)
ch := make(chan int)
// 보내는 즉시 받는 쪽이 있어야 함 (동기)

// 버퍼 채널 (buffered)
ch := make(chan int, 3)
// 버퍼가 차기 전까지 안 기다림 (비동기적)
```

### 동작 비교

```
버퍼 없는 채널:
  ch <- 1  → 누군가 받을 때까지 여기서 멈춤 (블로킹)

버퍼 채널 (크기 3):
  ch <- 1  → 버퍼에 저장, 계속 진행
  ch <- 2  → 버퍼에 저장, 계속 진행
  ch <- 3  → 버퍼에 저장, 계속 진행
  ch <- 4  → 버퍼 가득 참, 여기서 멈춤
```

### 언제 버퍼를 쓰나?

```go
// 작업 결과를 모아둘 때
results := make(chan int, 100)  // 100개 결과 버퍼

for i := 0; i < 100; i++ {
    go func(n int) {
        results <- n * n  // 결과를 버퍼에 쌓음
    }(i)
}
```

---

## 64. Range & Close

### close: 채널 닫기

```go
ch := make(chan int, 3)
ch <- 1
ch <- 2
ch <- 3
close(ch)  // 더 이상 보내지 않겠다고 선언

// 닫힌 채널에 보내면 패닉
// ch <- 4  // panic!

// 닫힌 채널에서 받기는 가능 (남은 값까지)
fmt.Println(<-ch)  // 1
fmt.Println(<-ch)  // 2
```

### range로 채널 순회

```go
ch := make(chan int, 5)

// 값 보내고 닫기
go func() {
    for i := 1; i <= 5; i++ {
        ch <- i
    }
    close(ch)  // 다 보냈으면 반드시 닫기
}()

// range로 채널이 닫힐 때까지 받기
for v := range ch {
    fmt.Println(v)  // 1, 2, 3, 4, 5
}
// close 안 하면 range가 영원히 대기 → deadlock!
```

### 채널 닫힘 확인

```go
ch := make(chan int, 2)
ch <- 1
close(ch)

// 두 번째 반환값으로 닫힘 확인
v, ok := <-ch
fmt.Println(v, ok)  // 1 true (값 있음)

v, ok = <-ch
fmt.Println(v, ok)  // 0 false (닫혔고 값 없음)
```

### ★ close 규칙

```
1. 보내는 쪽(sender)만 close해야 함
2. 받는 쪽은 close하면 안 됨
3. 닫힌 채널에 보내면 panic
4. close는 "더 보낼 값 없음"을 알리는 용도
5. 꼭 필요할 때만 close (range 쓸 때 등)
```

---

## 65. Select

### select란?
여러 채널을 **동시에 기다리는** 제어문입니다.
switch와 비슷하지만 채널 전용입니다.

```go
select {
case v := <-ch1:
    fmt.Println("ch1에서 받음:", v)
case v := <-ch2:
    fmt.Println("ch2에서 받음:", v)
case ch3 <- 10:
    fmt.Println("ch3로 보냄")
}
// 준비된 case 하나가 실행됨
// 여러 개 준비되면 무작위로 하나 선택
```

### 기본 예제

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    ch1 := make(chan string)
    ch2 := make(chan string)

    go func() {
        time.Sleep(1 * time.Second)
        ch1 <- "1초 후 도착"
    }()

    go func() {
        time.Sleep(2 * time.Second)
        ch2 <- "2초 후 도착"
    }()

    // 2개 채널 동시 대기 → 먼저 오는 것부터 처리
    for i := 0; i < 2; i++ {
        select {
        case msg1 := <-ch1:
            fmt.Println(msg1)  // 먼저 출력 (1초)
        case msg2 := <-ch2:
            fmt.Println(msg2)  // 나중 출력 (2초)
        }
    }
}
```

### 타임아웃 패턴 (★ 실무 매우 중요)

```go
select {
case result := <-ch:
    fmt.Println("결과:", result)
case <-time.After(3 * time.Second):
    fmt.Println("타임아웃! 3초 안에 응답 없음")
}
// 채널 응답이 3초 안에 안 오면 타임아웃 처리
// → API 호출, DB 쿼리 등에 필수
```

---

## 66. Default Selection

### default: 대기 없이 즉시 처리

select에 default를 넣으면 준비된 case가 없을 때 즉시 실행됩니다.

```go
select {
case v := <-ch:
    fmt.Println("받음:", v)
default:
    fmt.Println("받을 게 없음 (대기 안 함)")
}
```

### 논블로킹 채널 동작

```go
// 블로킹: 값 올 때까지 대기
v := <-ch  // 값 없으면 영원히 대기

// 논블로킹: default로 즉시 처리
select {
case v := <-ch:
    fmt.Println("값 있음:", v)
default:
    fmt.Println("값 없음, 다른 일 함")  // 즉시 실행
}
```

### 주기적 폴링 패턴

```go
func monitor(done chan bool) {
    ticker := time.Tick(1 * time.Second)  // 1초마다 신호

    for {
        select {
        case <-done:
            fmt.Println("모니터링 종료")
            return
        case <-ticker:
            fmt.Println("서버 상태 체크...")  // 1초마다 실행
        default:
            time.Sleep(100 * time.Millisecond)  // CPU 과부하 방지
        }
    }
}
```

---

## 67. sync.Mutex (뮤텍스)

### 경쟁 상태(Race Condition) 문제

여러 고루틴이 같은 변수를 동시에 수정하면 문제가 생깁니다.

```go
// 위험한 코드 (race condition)
counter := 0

for i := 0; i < 1000; i++ {
    go func() {
        counter++  // 여러 고루틴이 동시에 수정 → 값이 꼬임!
    }()
}
// counter가 1000이 아닐 수 있음 (예: 987)
```

### Mutex로 해결

Mutex(Mutual Exclusion)는 한 번에 하나의 고루틴만 접근하도록 잠급니다.

```go
import "sync"

var (
    counter int
    mu      sync.Mutex
)

func increment() {
    mu.Lock()         // 잠금 (다른 고루틴 대기)
    counter++         // 안전하게 수정
    mu.Unlock()       // 잠금 해제
}
```

### defer와 함께 사용 (권장)

```go
func increment() {
    mu.Lock()
    defer mu.Unlock()  // 함수 끝나면 자동 해제
    counter++
}
```

### 완전한 예제

```go
package main

import (
    "fmt"
    "sync"
)

type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Increment() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) Value() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}

func main() {
    counter := SafeCounter{}
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            counter.Increment()
        }()
    }

    wg.Wait()
    fmt.Println("최종 값:", counter.Value())  // 정확히 1000
}
```

---

## 68. sync.WaitGroup

### WaitGroup이란?
여러 고루틴이 **모두 끝날 때까지 기다리는** 도구입니다.
time.Sleep으로 어림짐작하는 것보다 정확합니다.

```go
import "sync"

var wg sync.WaitGroup

wg.Add(1)    // 기다릴 고루틴 수 +1
wg.Done()    // 고루틴 완료 (카운트 -1)
wg.Wait()    // 카운트가 0이 될 때까지 대기
```

### 기본 패턴

```go
package main

import (
    "fmt"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()  // 함수 끝나면 완료 신호
    fmt.Printf("작업자 %d 시작\n", id)
    // 작업 수행...
    fmt.Printf("작업자 %d 완료\n", id)
}

func main() {
    var wg sync.WaitGroup

    for i := 1; i <= 5; i++ {
        wg.Add(1)              // 고루틴 추가할 때마다 +1
        go worker(i, &wg)      // 고루틴 실행
    }

    wg.Wait()  // 5개 모두 끝날 때까지 대기
    fmt.Println("모든 작업 완료!")
}
```

### ★ Add·Done·Wait 사용 규칙

```
1. wg.Add(n) → 고루틴 시작 전에 호출
2. wg.Done() → 고루틴 안에서 defer로 호출
3. wg.Wait() → 모든 고루틴 시작 후 호출
4. &wg로 포인터 전달 (값 복사하면 안 됨)
```

---

## 69. 실전: 동시 다운로드

### DevOps 시나리오: 여러 서버 동시 헬스체크

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Result struct {
    Server string
    Status string
    Latency time.Duration
}

func checkServer(server string, ch chan Result, wg *sync.WaitGroup) {
    defer wg.Done()

    start := time.Now()
    // 실제로는 http.Get(server) 등
    time.Sleep(time.Duration(len(server)*50) * time.Millisecond)  // 모의 지연
    latency := time.Since(start)

    ch <- Result{
        Server:  server,
        Status:  "🟢 OK",
        Latency: latency,
    }
}

func main() {
    servers := []string{
        "web-01", "web-02", "db-01", "cache-01", "api-01",
    }

    ch := make(chan Result, len(servers))
    var wg sync.WaitGroup

    start := time.Now()

    // 모든 서버 동시 체크
    for _, s := range servers {
        wg.Add(1)
        go checkServer(s, ch, &wg)
    }

    // 별도 고루틴에서 완료 대기 후 채널 닫기
    go func() {
        wg.Wait()
        close(ch)
    }()

    // 결과 수집
    for result := range ch {
        fmt.Printf("%s %s (%.0fms)\n",
            result.Status, result.Server,
            float64(result.Latency.Milliseconds()))
    }

    fmt.Printf("\n총 소요 시간: %.0fms\n",
        float64(time.Since(start).Milliseconds()))
    // 순차 실행이면 모든 지연의 합
    // 동시 실행이면 가장 느린 서버 하나의 시간
}
```

---

## 70. 실전: 웹 크롤러 패턴

### Worker Pool 패턴 (작업자 풀)

대량의 작업을 정해진 수의 고루틴으로 처리하는 패턴입니다.

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// 작업자: jobs 채널에서 받아서 results 채널로 보냄
func worker(id int, jobs <-chan int, results chan<- int, wg *sync.WaitGroup) {
    defer wg.Done()
    for job := range jobs {
        fmt.Printf("작업자 %d → 작업 %d 처리\n", id, job)
        time.Sleep(100 * time.Millisecond)  // 작업 시뮬레이션
        results <- job * 2                   // 결과 전송
    }
}

func main() {
    const numJobs = 9
    const numWorkers = 3

    jobs := make(chan int, numJobs)
    results := make(chan int, numJobs)
    var wg sync.WaitGroup

    // 작업자 3명 생성
    for w := 1; w <= numWorkers; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    // 작업 9개 투입
    for j := 1; j <= numJobs; j++ {
        jobs <- j
    }
    close(jobs)  // 작업 다 넣었으면 닫기

    // 완료 대기 후 결과 채널 닫기
    go func() {
        wg.Wait()
        close(results)
    }()

    // 결과 수집
    total := 0
    for r := range results {
        total += r
    }
    fmt.Printf("\n모든 작업 완료, 결과 합계: %d\n", total)
}
```

### 채널 방향 제한 (읽기 전용·쓰기 전용)

```go
// <-chan : 읽기 전용 채널
// chan<- : 쓰기 전용 채널

func producer(out chan<- int) {  // 쓰기 전용
    for i := 0; i < 5; i++ {
        out <- i
    }
    close(out)
}

func consumer(in <-chan int) {   // 읽기 전용
    for v := range in {
        fmt.Println(v)
    }
}

// → 함수 시그니처만 봐도 채널을 어떻게 쓰는지 명확
// → 실수로 잘못된 방향 사용 시 컴파일 에러
```

---

## 실전 종합 코드

`practice_ch61_70.go`로 저장 후 실행:

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

// 서버 상태 구조체
type ServerStatus struct {
    Name    string
    Healthy bool
    CPU     float64
}

// 안전한 카운터 (Mutex)
type Stats struct {
    mu      sync.Mutex
    healthy int
    down    int
}

func (s *Stats) Record(healthy bool) {
    s.mu.Lock()
    defer s.mu.Unlock()
    if healthy {
        s.healthy++
    } else {
        s.down++
    }
}

// 서버 체크 (고루틴으로 실행)
func checkServer(name string, results chan<- ServerStatus, stats *Stats, wg *sync.WaitGroup) {
    defer wg.Done()

    // 체크 시뮬레이션
    time.Sleep(time.Duration(len(name)*30) * time.Millisecond)

    // 모의 결과 (이름 길이로 판정)
    healthy := len(name) % 2 == 0
    cpu := float64(len(name) * 10)

    stats.Record(healthy)
    results <- ServerStatus{Name: name, Healthy: healthy, CPU: cpu}
}

func main() {
    servers := []string{
        "web-01", "web-02", "web-03",
        "db-01", "db-02",
        "cache-01", "api-gateway",
    }

    fmt.Println("=== 동시 헬스체크 시작 ===")
    start := time.Now()

    results := make(chan ServerStatus, len(servers))
    stats := &Stats{}
    var wg sync.WaitGroup

    // 모든 서버 동시 체크
    for _, name := range servers {
        wg.Add(1)
        go checkServer(name, results, stats, &wg)
    }

    // 완료 후 채널 닫기
    go func() {
        wg.Wait()
        close(results)
    }()

    // 결과 수집 (select + timeout)
    for {
        select {
        case result, ok := <-results:
            if !ok {
                goto DONE  // 채널 닫힘 → 종료
            }
            icon := "🟢"
            if !result.Healthy {
                icon = "🔴"
            }
            fmt.Printf("%s %s (CPU: %.0f%%)\n", icon, result.Name, result.CPU)

        case <-time.After(5 * time.Second):
            fmt.Println("⏱️ 타임아웃!")
            goto DONE
        }
    }

DONE:
    elapsed := time.Since(start)
    fmt.Printf("\n=== 체크 완료 ===\n")
    fmt.Printf("정상: %d대 | 다운: %d대\n", stats.healthy, stats.down)
    fmt.Printf("총 소요: %.0fms\n", float64(elapsed.Milliseconds()))
}
```

---

## 자주 하는 실수

### 실수 1: main이 고루틴을 안 기다림
```go
// 잘못됨
func main() {
    go doWork()  // 시작만 하고
    // main 끝남 → 고루틴 실행 못 함
}

// 올바름: WaitGroup으로 대기
func main() {
    var wg sync.WaitGroup
    wg.Add(1)
    go func() {
        defer wg.Done()
        doWork()
    }()
    wg.Wait()
}
```

### 실수 2: 닫힌 채널에 전송
```go
ch := make(chan int)
close(ch)
ch <- 1  // panic: send on closed channel
```

### 실수 3: 받는 쪽에서 close
```go
// 잘못됨: 받는 쪽(consumer)이 close
func consumer(ch chan int) {
    v := <-ch
    close(ch)  // ❌ 받는 쪽은 닫으면 안 됨
}

// 올바름: 보내는 쪽(producer)이 close
func producer(ch chan int) {
    ch <- 1
    close(ch)  // ✅ 보내는 쪽이 닫음
}
```

### 실수 4: range 채널인데 close 안 함
```go
ch := make(chan int)
go func() {
    ch <- 1
    ch <- 2
    // close(ch) 안 함!
}()

for v := range ch {  // 2개 받고 영원히 대기 → deadlock!
    fmt.Println(v)
}
```

### 실수 5: WaitGroup을 값으로 전달
```go
// 잘못됨: 값 복사
func worker(wg sync.WaitGroup) {  // ❌ 복사본
    defer wg.Done()
}

// 올바름: 포인터 전달
func worker(wg *sync.WaitGroup) {  // ✅ 포인터
    defer wg.Done()
}
```

### 실수 6: 루프 변수 캡처 (Go 1.22 이전)
```go
// 위험 (Go 1.22 미만)
for i := 0; i < 3; i++ {
    go func() {
        fmt.Println(i)  // 모두 3 출력될 수 있음
    }()
}

// 안전: 인자로 전달
for i := 0; i < 3; i++ {
    go func(n int) {
        fmt.Println(n)  // 0, 1, 2 정상 출력
    }(i)
}
```

---

## 동시성 핵심 정리

### 황금률
```
"메모리를 공유하여 통신하지 말고,
 통신하여 메모리를 공유하라"
 (Don't communicate by sharing memory;
  share memory by communicating)

→ 변수를 여러 고루틴이 직접 공유하지 말고
  채널로 값을 주고받아라
```

### 도구 선택 가이드

| 상황 | 도구 |
|------|------|
| 함수를 동시 실행 | `go 함수()` |
| 고루틴 간 값 전달 | `channel` |
| 여러 채널 동시 대기 | `select` |
| 타임아웃 처리 | `select` + `time.After` |
| 고루틴 완료 대기 | `sync.WaitGroup` |
| 공유 변수 보호 | `sync.Mutex` |
| 대량 작업 처리 | Worker Pool 패턴 |

---

## 챕터별 핵심 한줄 요약

| 챕터 | 핵심 |
|------|------|
| 61 | go 함수() → 함수를 고루틴으로 동시 실행 |
| 62 | ch <- v 보내기, v := <-ch 받기 — 고루틴 간 통신 |
| 63 | make(chan T, n) → n개 버퍼, 가득 차면 블로킹 |
| 64 | close()로 닫고 range로 순회, 보내는 쪽만 close |
| 65 | select → 여러 채널 중 준비된 것 처리 |
| 66 | default → 준비된 채널 없으면 즉시 실행 (논블로킹) |
| 67 | sync.Mutex Lock/Unlock → 공유 변수 안전하게 보호 |
| 68 | sync.WaitGroup Add/Done/Wait → 고루틴 완료 대기 |
| 69 | 여러 서버 동시 헬스체크 — 고루틴+채널+WaitGroup |
| 70 | Worker Pool — 정해진 수의 고루틴으로 대량 작업 처리 |

---

## 🎉 Go Tour 70챕터 전체 완료!

```
1~15:  기초 (변수·타입·함수)
16~30: 제어문·포인터·구조체
31~45: 배열·슬라이스·맵·Range
46~60: 메서드·인터페이스
61~70: 동시성 (고루틴·채널·select·mutex)

→ Go 언어 핵심 문법 전체 학습 완료
→ DevOps에서 필요한 수준 충분히 도달
```

다음 단계: 실제로 코드를 읽고 수정하면서 익히기. 외우려 하지 말고 필요할 때 이 자료를 참고하세요.

---

*Go Tour 챕터 61~70 완전 정리 — 2026.06.03*