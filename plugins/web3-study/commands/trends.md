---
name: trends
description: 동향 연구 - 특정 주제의 최신 뉴스, 블로그, 리포트 수집
argument-hint: "<주제> (예: AP2, Google Agent, x402)"
allowed-tools:
  - Task
---

Run trend research on the given topic.

## Execution

1. Determine week number from topic (or ask user)
2. Launch trend-researcher agent with the topic
3. Agent saves results to `study/week-{N}/trends-{topic}.md`

## Example Usage

```
/trends AP2
/trends "Google Agent Protocol 발표"
/trends x402 업계 반응
```
