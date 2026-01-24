# Web3 Study Plugin Design

**Date**: 2025-01-24
**Purpose**: Web3 AI 에이전트 세미나 학습 도구
**Target**: 개인 사용 (세미나 준비 및 학습)

## Overview

11주 세미나 커리큘럼(A2A, AP2, x402 프로토콜)을 학습하기 위한 Claude Code 플러그인.
5주차(1/27) Google AP2 발표 준비가 주요 목표.

### 핵심 기능
- 이론/스펙 정리
- 뉴스/블로그/리포트 수집
- 코드 예제 및 데모 구현
- 수동 인풋으로 최신 자료 추가

## Plugin Structure

```
plugins/web3-study/
├── .claude-plugin/
│   └── plugin.json
├── agents/
│   ├── theory-researcher.md    # 이론/스펙 연구
│   ├── trend-researcher.md     # 뉴스/블로그/리포트
│   └── code-builder.md         # 코드 예제/데모
├── commands/
│   ├── study.md                # /study 5주차 → 종합 학습
│   ├── theory.md               # /theory AP2
│   ├── trends.md               # /trends AP2
│   ├── code.md                 # /code ap2-demo
│   └── input.md                # /input theory "..."
└── skills/
    └── web3-protocols/
        ├── SKILL.md
        └── references/
            ├── a2a-overview.md
            ├── ap2-overview.md
            ├── x402-overview.md
            └── comparison.md
```

### Output Structure

```
study/
├── week-2/    # 에이전트 인터넷 핵심 프로토콜
├── week-3/    # 목표 지향적 에이전트 개발
├── week-4/    # A2A 심층 분석
├── week-5/    # Google AP2 (발표)
├── week-6/    # x402 심층 분석
├── week-7/    # x402 구현 워크숍
├── week-8/    # LLM 협상 전략
├── week-9/    # 전체 시스템 아키텍처
├── week-10/   # 비즈니스 모델
└── week-11/   # 최종 프로젝트 발표
```

## Agents

### theory-researcher
- **트리거**: "이론 정리해줘", "스펙 분석해줘", `/theory`
- **역할**: 프로토콜 개념, 공식 스펙, 아키텍처 다이어그램 정리
- **도구**: WebSearch, WebFetch, Context7, Read
- **인풋**: 사용자가 문서/링크 직접 제공 가능
- **아웃풋**: `study/week-N/theory-*.md`

### trend-researcher
- **트리거**: "최신 동향 찾아줘", "뉴스 정리해줘", `/trends`
- **역할**: 뉴스, 블로그, 리포트, 컨퍼런스 발표, 업계 반응 수집
- **도구**: WebSearch, WebFetch, Read
- **인풋**: 사용자가 블로그/리포트 링크 직접 제공 가능
- **아웃풋**: `study/week-N/trends-*.md`

### code-builder
- **트리거**: "코드 예제 만들어줘", "데모 구현해줘", `/code`
- **역할**: 의사코드, 실제 구현, 오픈소스 분석, 데모 작성
- **도구**: Bash, Read, Write, Glob, Context7
- **인풋**: 사용자가 GitHub 레포/코드 제공 가능
- **아웃풋**: `study/week-N/code-*.md` 또는 `study/week-N/demo/`

## Commands

### /study <주차>
종합 학습 - 3개 에이전트 병렬 실행
```
/study 5주차
/study week-5
/study AP2
```

### /theory <주제>
이론만 - theory-researcher 단독 실행
```
/theory AP2
/theory "에이전트 디스커버리"
```

### /trends <주제>
동향만 - trend-researcher 단독 실행
```
/trends AP2
/trends x402
```

### /code <주제>
코드만 - code-builder 단독 실행
```
/code ap2-demo
/code "AP2 에이전트 통신 예제"
```

### /input <타입>
수동 인풋 - 사용자 자료 추가
```
/input theory "문서 내용"
/input trends https://blog.example.com/ap2
```

## Skill: web3-protocols

에이전트들이 공통으로 참조하는 프로토콜 기본 지식.
초기에는 뼈대만 만들고 공부하면서 보강.

### 트리거 예시
- "A2A가 뭐야?"
- "AP2랑 A2A 차이가 뭐야?"
- "x402로 결제 어떻게 해?"

### References
- a2a-overview.md: A2A 프로토콜 핵심 개념
- ap2-overview.md: AP2 프로토콜 핵심 개념
- x402-overview.md: x402 프로토콜 핵심 개념
- comparison.md: 3개 프로토콜 비교표

## 5주차 발표 준비 워크플로우

| 시점 | 액션 | 명령어 |
|-----|------|--------|
| D-7 | 기초 학습 | `/study 5주차` |
| D-5~3 | 자료 보강 | `/input theory/trends [자료]` |
| D-3 | 심화 학습 | `/theory`, `/trends` 개별 호출 |
| D-2~1 | 데모 준비 | `/code "AP2 데모"` |
| D-1 | 최종 정리 | study/week-5/ 폴더 기반 발표자료 작성 |

## Seminar Schedule Reference

- 2주차 (12/30): 핵심 프로토콜 스택 (A2A, AP2, x402)
- 3주차 (1/6): 목표 지향적 에이전트 개발
- 4주차 (1/13): A2A 심층 분석
- 5주차 (1/20): 에이전트 디스커버리
- **6주차 (1/27): Google AP2 - 발표일**
- 7주차 (2/3): x402 심층 분석
- 8주차 (2/10): x402 구현 워크숍
- 9주차 (2/17): LLM 협상 전략
- 10주차 (2/24): 통합 아키텍처 설계
- 11주차 (3/3): 비즈니스 모델 구상
- 12주차 (3/10): 최종 프로젝트 발표
