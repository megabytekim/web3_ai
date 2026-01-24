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
