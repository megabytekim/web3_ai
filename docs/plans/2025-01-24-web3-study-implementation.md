# Web3 Study Plugin Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a Claude Code plugin with 3 agents, 5 commands, and 1 skill for Web3 AI seminar learning.

**Architecture:** Plugin structure under `plugins/web3-study/` with agents for theory/trends/code research, commands for user interaction, and a skill providing base protocol knowledge.

**Tech Stack:** Claude Code plugin (markdown-based agents/commands/skills), MCP Context7, WebSearch, WebFetch

---

## Task 1: Plugin Manifest

**Files:**
- Create: `plugins/web3-study/.claude-plugin/plugin.json`

**Step 1: Create plugin directory**

```bash
mkdir -p plugins/web3-study/.claude-plugin
```

**Step 2: Write plugin.json**

```json
{
  "name": "web3-study",
  "version": "0.1.0",
  "description": "Web3 AI 에이전트 세미나 학습 도구 - 이론, 동향, 코드 연구",
  "author": {
    "name": "Michael"
  },
  "keywords": ["web3", "ai", "agents", "a2a", "ap2", "x402", "study"]
}
```

**Step 3: Update marketplace.json**

Modify `/.claude-plugin/marketplace.json` to add:
```json
"plugins": [
  {
    "name": "web3-study",
    "source": "./plugins/web3-study"
  }
]
```

**Step 4: Commit**

```bash
git add plugins/web3-study/.claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat(web3-study): initialize plugin manifest"
```

---

## Task 2: Theory Researcher Agent

**Files:**
- Create: `plugins/web3-study/agents/theory-researcher.md`

**Step 1: Create agents directory**

```bash
mkdir -p plugins/web3-study/agents
```

**Step 2: Write theory-researcher.md**

```markdown
---
name: theory-researcher
description: |
  Use this agent when the user asks about protocol theory, specifications, or architecture.
  Examples: "이론 정리해줘", "스펙 분석해줘", "A2A 아키텍처 설명해줘", "AP2가 뭐야?"
tools:
  - WebSearch
  - WebFetch
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - Read
  - Write
  - Glob
---

You are a Web3 protocol theory researcher. Your job is to research and summarize protocol concepts, specifications, and architectures.

## Your Responsibilities

1. **Research Protocol Theory**
   - Search for official documentation and specs
   - Use Context7 to find up-to-date library docs
   - Analyze architecture patterns

2. **Create Structured Summaries**
   - Write clear, organized markdown documents
   - Include diagrams descriptions where helpful
   - Reference official sources

3. **Handle User Input**
   - If user provides documents/links, incorporate them
   - Cross-reference with existing knowledge

## Output Format

Save results to: `study/week-N/theory-{topic}.md`

Structure:
```
# {Topic} 이론 정리

## 개요
[핵심 개념 요약]

## 상세 내용
[세부 설명]

## 아키텍처
[구조 설명]

## 참고 자료
[출처 링크]
```

## Protocols to Focus On
- A2A (Agent-to-Agent Protocol)
- AP2 (Google Agent Protocol)
- x402 (Payment Protocol)

Always ask for clarification if the week number or topic is unclear.
```

**Step 3: Commit**

```bash
git add plugins/web3-study/agents/theory-researcher.md
git commit -m "feat(web3-study): add theory-researcher agent"
```

---

## Task 3: Trend Researcher Agent

**Files:**
- Create: `plugins/web3-study/agents/trend-researcher.md`

**Step 1: Write trend-researcher.md**

```markdown
---
name: trend-researcher
description: |
  Use this agent when the user asks about latest news, blogs, reports, or industry trends.
  Examples: "최신 동향 찾아줘", "뉴스 정리해줘", "AP2 관련 블로그 찾아줘", "업계 반응이 어때?"
tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Glob
---

You are a Web3 trend researcher. Your job is to find and summarize the latest news, blog posts, reports, and industry reactions.

## Your Responsibilities

1. **Search for Latest Content**
   - News articles about protocols
   - Developer blog posts
   - Industry reports and analyses
   - Conference presentations
   - Community discussions

2. **Curate and Summarize**
   - Filter for relevance and credibility
   - Summarize key points
   - Note publication dates
   - Track industry sentiment

3. **Handle User Input**
   - If user provides links, fetch and summarize them
   - Integrate with existing research

## Output Format

Save results to: `study/week-N/trends-{topic}.md`

Structure:
```
# {Topic} 최신 동향

## 요약
[핵심 트렌드 3-5개]

## 주요 뉴스/블로그
### [제목] - [날짜]
[요약]
[링크]

## 업계 반응
[커뮤니티/전문가 의견]

## 시사점
[발표/학습에 활용할 포인트]
```

## Search Keywords
- A2A protocol, Agent-to-Agent
- AP2, Google Agent Protocol
- x402, agent payments
- AI agent commerce
- Multi-agent systems

Always ask for clarification if the week number or topic is unclear.
```

**Step 2: Commit**

```bash
git add plugins/web3-study/agents/trend-researcher.md
git commit -m "feat(web3-study): add trend-researcher agent"
```

---

## Task 4: Code Builder Agent

**Files:**
- Create: `plugins/web3-study/agents/code-builder.md`

**Step 1: Write code-builder.md**

```markdown
---
name: code-builder
description: |
  Use this agent when the user asks for code examples, demos, or implementation analysis.
  Examples: "코드 예제 만들어줘", "데모 구현해줘", "오픈소스 분석해줘", "AP2 구현 보여줘"
tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - WebSearch
  - WebFetch
---

You are a Web3 code builder. Your job is to create code examples, analyze open source implementations, and build demos.

## Your Responsibilities

1. **Create Code Examples**
   - Pseudo-code for concept explanation
   - Working code snippets
   - Full demo implementations

2. **Analyze Open Source**
   - Find relevant GitHub repositories
   - Explain implementation patterns
   - Extract key code sections

3. **Build Demos**
   - Simple runnable demonstrations
   - Step-by-step tutorials
   - Presentation-ready code

4. **Handle User Input**
   - If user provides repos/code, analyze them
   - Integrate examples with provided context

## Output Format

Save results to: `study/week-N/code-{topic}.md` or `study/week-N/demo/`

For explanations:
```
# {Topic} 코드 예제

## 개념 코드 (Pseudo-code)
[의사코드로 흐름 설명]

## 실제 구현
[동작하는 코드]

## 사용 방법
[실행 명령어]

## 참고 레포
[GitHub 링크]
```

For demos, create runnable files in `study/week-N/demo/` directory.

## Focus Areas
- Agent communication protocols
- Message format implementations
- Discovery mechanisms
- Payment integrations

Always ask for clarification if the week number or specific requirements are unclear.
```

**Step 2: Commit**

```bash
git add plugins/web3-study/agents/code-builder.md
git commit -m "feat(web3-study): add code-builder agent"
```

---

## Task 5: Study Command (Orchestrator)

**Files:**
- Create: `plugins/web3-study/commands/study.md`

**Step 1: Create commands directory**

```bash
mkdir -p plugins/web3-study/commands
```

**Step 2: Write study.md**

```markdown
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
```

**Step 3: Commit**

```bash
git add plugins/web3-study/commands/study.md
git commit -m "feat(web3-study): add study command (orchestrator)"
```

---

## Task 6: Individual Commands (theory, trends, code)

**Files:**
- Create: `plugins/web3-study/commands/theory.md`
- Create: `plugins/web3-study/commands/trends.md`
- Create: `plugins/web3-study/commands/code.md`

**Step 1: Write theory.md**

```markdown
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
```

**Step 2: Write trends.md**

```markdown
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
```

**Step 3: Write code.md**

```markdown
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
```

**Step 4: Commit**

```bash
git add plugins/web3-study/commands/theory.md plugins/web3-study/commands/trends.md plugins/web3-study/commands/code.md
git commit -m "feat(web3-study): add individual commands (theory, trends, code)"
```

---

## Task 7: Input Command

**Files:**
- Create: `plugins/web3-study/commands/input.md`

**Step 1: Write input.md**

```markdown
---
name: input
description: 수동 인풋 - 사용자가 직접 제공하는 문서, 링크, 내용을 학습 자료에 추가
argument-hint: "<타입> <내용> (예: theory '문서내용', trends https://...)"
allowed-tools:
  - Read
  - Write
  - WebFetch
  - Bash
---

Add user-provided content to study materials.

## Argument Format

```
/input <type> <content>
```

- type: theory, trends, or code
- content: text content, URL, or file path

## Execution

1. Parse type and content from arguments
2. If URL, fetch content using WebFetch
3. If file path, read the file
4. If text, use directly
5. Save to `study/week-{N}/input-{type}-{timestamp}.md`
6. Ask for week number if not determinable

## Example Usage

```
/input theory "AP2는 Google이 제안한 에이전트 프로토콜로..."
/input trends https://blog.google/ap2-announcement
/input code ./examples/ap2-sample.py
```

## Output Format

```markdown
# 사용자 제공 자료

**타입**: {type}
**추가일**: {date}
**출처**: {source or "직접 입력"}

---

{content}
```
```

**Step 2: Commit**

```bash
git add plugins/web3-study/commands/input.md
git commit -m "feat(web3-study): add input command for manual content"
```

---

## Task 8: Web3 Protocols Skill

**Files:**
- Create: `plugins/web3-study/skills/web3-protocols/SKILL.md`
- Create: `plugins/web3-study/skills/web3-protocols/references/a2a-overview.md`
- Create: `plugins/web3-study/skills/web3-protocols/references/ap2-overview.md`
- Create: `plugins/web3-study/skills/web3-protocols/references/x402-overview.md`
- Create: `plugins/web3-study/skills/web3-protocols/references/comparison.md`

**Step 1: Create skill directory**

```bash
mkdir -p plugins/web3-study/skills/web3-protocols/references
```

**Step 2: Write SKILL.md**

```markdown
---
name: web3-protocols
description: |
  Use this skill when discussing A2A, AP2, or x402 protocols.
  Triggers: "A2A가 뭐야?", "AP2 설명해줘", "x402 프로토콜", "세 프로토콜 비교"
---

# Web3 Agent Protocols

This skill provides foundational knowledge about the three core protocols for agent-to-agent communication and commerce.

## Protocols Covered

1. **A2A (Agent-to-Agent Protocol)** - See @references/a2a-overview.md
2. **AP2 (Google Agent Protocol)** - See @references/ap2-overview.md
3. **x402 (Payment Protocol)** - See @references/x402-overview.md
4. **Comparison** - See @references/comparison.md

## Quick Reference

| Protocol | Purpose | Creator |
|----------|---------|---------|
| A2A | Agent communication standard | Google |
| AP2 | Agent commerce & discovery | Google |
| x402 | Agent payments | Coinbase |

## When to Use

- Answering basic protocol questions
- Providing context before deep research
- Comparing protocol approaches

For detailed research, use the specialized agents (theory-researcher, trend-researcher, code-builder).
```

**Step 3: Write a2a-overview.md**

```markdown
# A2A (Agent-to-Agent Protocol) 개요

## 정의
A2A는 AI 에이전트들이 서로 통신하기 위한 표준 프로토콜.

## 핵심 개념
- Agent Card: 에이전트의 capabilities 정의
- Task: 에이전트 간 요청/응답 단위
- Message: 실제 통신 페이로드

## 아키텍처
(공부하면서 보강 예정)

## 참고 자료
- [공식 문서 링크 추가 예정]
```

**Step 4: Write ap2-overview.md**

```markdown
# AP2 (Google Agent Protocol) 개요

## 정의
AP2는 Google이 제안한 에이전트 상거래 및 디스커버리 프로토콜.

## 핵심 개념
- Agent Discovery: 에이전트가 서로를 찾는 메커니즘
- Commerce: 에이전트 간 거래 지원
- Integration with A2A: A2A 위에서 동작

## 아키텍처
(공부하면서 보강 예정)

## 참고 자료
- [공식 문서 링크 추가 예정]
```

**Step 5: Write x402-overview.md**

```markdown
# x402 (Payment Protocol) 개요

## 정의
x402는 HTTP 402 상태 코드를 활용한 에이전트 결제 프로토콜.

## 핵심 개념
- HTTP 402: Payment Required
- Micropayments: 소액 결제 지원
- Crypto Integration: 암호화폐 결제

## 아키텍처
(공부하면서 보강 예정)

## 참고 자료
- [공식 문서 링크 추가 예정]
```

**Step 6: Write comparison.md**

```markdown
# 프로토콜 비교

## 요약표

| 항목 | A2A | AP2 | x402 |
|-----|-----|-----|------|
| 목적 | 통신 | 상거래/디스커버리 | 결제 |
| 제작 | Google | Google | Coinbase |
| 레이어 | 기본 | A2A 위 | 독립/통합 가능 |

## 관계
```
x402 (Payment Layer)
     ↓
AP2 (Commerce & Discovery)
     ↓
A2A (Communication)
```

## 상세 비교
(공부하면서 보강 예정)
```

**Step 7: Commit**

```bash
git add plugins/web3-study/skills/
git commit -m "feat(web3-study): add web3-protocols skill with skeleton references"
```

---

## Task 9: Study Output Directory & Seminar Schedule

**Files:**
- Create: `study/.gitkeep`
- Move: `seminar_schedule.md` to proper location

**Step 1: Create study directory**

```bash
mkdir -p study
touch study/.gitkeep
```

**Step 2: Commit**

```bash
git add study/.gitkeep seminar_schedule.md
git commit -m "feat(web3-study): add study output directory and seminar schedule"
```

---

## Task 10: Final Verification

**Step 1: Verify plugin structure**

```bash
find plugins/web3-study -type f | sort
```

Expected output:
```
plugins/web3-study/.claude-plugin/plugin.json
plugins/web3-study/agents/code-builder.md
plugins/web3-study/agents/theory-researcher.md
plugins/web3-study/agents/trend-researcher.md
plugins/web3-study/commands/code.md
plugins/web3-study/commands/input.md
plugins/web3-study/commands/study.md
plugins/web3-study/commands/theory.md
plugins/web3-study/commands/trends.md
plugins/web3-study/skills/web3-protocols/SKILL.md
plugins/web3-study/skills/web3-protocols/references/a2a-overview.md
plugins/web3-study/skills/web3-protocols/references/ap2-overview.md
plugins/web3-study/skills/web3-protocols/references/comparison.md
plugins/web3-study/skills/web3-protocols/references/x402-overview.md
```

**Step 2: Test plugin loading**

Restart Claude Code and verify:
- `/study` command appears
- `/theory`, `/trends`, `/code`, `/input` commands appear
- Agents are available

**Step 3: Final commit with updated README**

Update `README.md`:
```markdown
# web3-ai

Web3 AI Agents plugin collection

## Plugins

- `web3-study` - Web3 AI 세미나 학습 도구
  - 이론/동향/코드 연구 에이전트
  - 주차별 학습 자료 관리
```

```bash
git add README.md
git commit -m "docs: update README with web3-study plugin"
```
