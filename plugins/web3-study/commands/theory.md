---
name: theory
description: 이론 연구 - 특정 주제의 프로토콜 개념, 스펙, 아키텍처 정리
argument-hint: "<주제> (예: AP2, A2A, 에이전트 디스커버리)"
allowed-tools:
  - Task
---

Run theory research on the given topic.

## Execution

1. Determine week number from topic (or ask user)
2. Launch theory-researcher agent with the topic
3. Agent saves results to `study/week-{N}/theory-{topic}.md`

## Example Usage

```
/theory AP2
/theory "에이전트 디스커버리"
/theory x402 결제 흐름
```
