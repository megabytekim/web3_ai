---
name: study
description: 종합 학습 - 특정 주차/주제에 대해 이론, 동향, 코드를 병렬로 연구
argument-hint: "<주차 또는 주제> (예: 5주차, AP2, x402)"
allowed-tools:
  - Task
  - Read
  - Write
  - Bash
---

Run comprehensive study on the given week or topic by dispatching three agents in parallel.

## Week-Topic Mapping

- week-2: A2A, AP2, x402 핵심 프로토콜 스택
- week-3: 목표 지향적 에이전트 개발
- week-4: A2A 심층 분석
- week-5: 에이전트 디스커버리
- week-6: Google AP2 (발표 준비)
- week-7: x402 심층 분석
- week-8: x402 구현 워크숍
- week-9: LLM 협상 전략
- week-10: 통합 아키텍처
- week-11: 비즈니스 모델
- week-12: 최종 프로젝트

## Execution Steps

1. Parse the argument to determine week number and topic
2. Create output directory: `study/week-{N}/`
3. Launch three agents IN PARALLEL using Task tool:
   - theory-researcher: Research protocol theory
   - trend-researcher: Find latest trends
   - code-builder: Create code examples
4. Each agent saves to `study/week-{N}/` with appropriate filenames
5. After all complete, summarize what was created

## Example Usage

```
/study 5주차
/study week-6
/study AP2
```

## Important

- Use Task tool with `run_in_background: true` for parallel execution
- Wait for all agents to complete
- Report summary of generated files
