# Agent M Soul Store — TODO

## 현재 상태

- [x] api/state.py — 공유 상태 모듈
- [x] api/x402.py — x402 V2 프로토콜 시뮬레이션 (9 tests)
- [x] api/soul_store.py — 아이템 뽑기 + 대화 요약 (5 tests)
- [x] api/index.py — 시스템 프롬프트, SOUL_STORE_LINK 치환, 라우트 핸들러
- [x] api/chat.html — 마크다운 링크 렌더링
- [x] api/pay.html — 결제 UI + x402 프로토콜 시각화
- [x] 22 tests 전부 통과
- [x] dev 브랜치 push 완료

## 즉시 해야 할 것

### 1. Vercel Preview 테스트
- [ ] Vercel Dashboard에서 dev Preview URL 확인
- [ ] `/chat`에서 Agent M과 3턴 이상 대화
- [ ] "이 대화를 간직하고 싶어" → Agent M이 영혼 저장소 링크 제안하는지 확인
- [ ] 링크 클릭 → `/soul-store?ctx=xxx` 결제 페이지 정상 로드 확인
- [ ] "결제하기" 클릭 → x402 프로토콜 7단계 시각화 정상 동작 확인
- [ ] 아이템 공개 + 대화 요약 표시 확인
- [ ] 에러 케이스: ctx 없이 `/soul-store` 접속 시 안내 메시지 확인

### 2. Preview 검증 후 main merge
- [ ] 위 테스트 전부 통과 시:
  ```bash
  git checkout main
  git merge dev
  git push origin main
  git checkout dev
  ```

## 발견 시 수정할 것

### pay.html 디버깅
- [ ] 402 응답에서 PAYMENT-REQUIRED 헤더 파싱이 정상 동작하는지 (CORS 이슈 가능)
- [ ] PAYMENT-SIGNATURE 헤더 전송 시 preflight OPTIONS 처리 확인
- [ ] 아이템 reveal 애니메이션이 모바일에서도 정상인지

### Agent M 프롬프트 튜닝
- [ ] SOUL_STORE_LINK 제안 타이밍이 너무 이르거나 늦지 않은지
- [ ] Gemini가 마크다운 링크 형식을 잘 따르는지 (가끔 형식 깨질 수 있음)
- [ ] 필요하면 SYSTEM_INSTRUCTION 의 영혼 저장소 섹션 조정

## 향후 확장 (현재 범위 아님)

- [ ] 아이템별 차등 기능 (영혼석=전체 저장, 금고=핵심만, 수정구=명언 생성)
- [ ] NFT 민팅 (아이템을 온체인 NFT로)
- [ ] 실제 x402 SDK 연동 (`pip install "x402[fastapi,evm]"` + Base Sepolia 테스트넷)
- [ ] 영구 저장 (Vercel KV 또는 SQLite)
- [ ] @x402/paywall 프론트엔드 (실제 MetaMask 지갑 연결)

## 관련 문서

- 설계 스펙: `docs/superpowers/specs/2026-03-16-soul-store-design.md`
- 구현 계획: `docs/superpowers/plans/2026-03-16-soul-store.md`
- x402 리서치: `docs/x402-research.md`
