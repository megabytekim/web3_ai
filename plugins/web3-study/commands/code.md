---
name: code
description: 코드 연구 - 특정 주제의 코드 예제, 데모, 오픈소스 분석
argument-hint: "<주제 또는 요청> (예: ap2-demo, A2A 통신 예제)"
allowed-tools:
  - Task
---

Run code research/building on the given topic.

## Execution

1. Determine week number from topic (or ask user)
2. Launch code-builder agent with the request
3. Agent saves results to `study/week-{N}/code-{topic}.md` or `study/week-{N}/demo/`

## Example Usage

```
/code ap2-demo
/code "A2A 에이전트 통신 예제"
/code "x402 결제 구현"
```
