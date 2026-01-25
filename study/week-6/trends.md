# 에이전트 상거래의 미래와 Google AP2의 접근 방식 - 최신 동향

## 요약

1. **Google AP2 정식 발표 (2025년 9월)**: 60개 이상 글로벌 파트너와 함께 에이전트 결제 표준 프로토콜 공개
2. **경쟁 프로토콜 부상**: OpenAI/Stripe의 ACP, Google의 AP2/A2A, Visa/Mastercard의 독자 솔루션이 병존
3. **대형 결제사 본격 참여**: Mastercard Agent Pay, Visa Intelligent Commerce, PayPal 다중 플랫폼 전략
4. **시장 규모 폭발적 성장 전망**: McKinsey는 2030년까지 글로벌 에이전트 상거래 시장 3~5조 달러 예측
5. **Agentic AI Foundation 출범**: OpenAI, Anthropic, Google, Microsoft 등이 Linux Foundation 하에 협력

---

## 1. 최신 뉴스 및 발표

### 1.1 Google AP2 (Agent Payments Protocol) 발표

**발표일**: 2025년 9월 16일

Google이 60개 이상의 글로벌 파트너와 함께 Agent Payments Protocol(AP2)을 공개했다. AP2는 AI 에이전트가 사용자를 대신하여 안전하게 결제를 수행할 수 있도록 하는 개방형 프로토콜이다.

**핵심 특징**:
- **Mandate 시스템**: Intent Mandate(의도 위임장), Cart Mandate(장바구니 위임장), Payment Mandate(결제 위임장)의 3단계 암호화 검증
- **결제 방식 무관성**: 신용카드, 직불카드, 실시간 은행이체, 스테이블코인 등 다양한 결제 수단 지원
- **A2A x402 확장**: Coinbase, Ethereum Foundation, MetaMask와 협력하여 암호화폐 결제 지원

**주요 파트너**:
- 결제 네트워크: Mastercard, American Express, Visa
- 결제 처리사: PayPal, Adyen, Worldpay, UnionPay
- 기술 기업: Salesforce, ServiceNow, Intuit, Shopify, Cloudflare, Etsy

> 출처: [Google Cloud Blog - Announcing Agent Payments Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)

---

### 1.2 OpenAI/Stripe Agentic Commerce Protocol (ACP)

OpenAI와 Stripe가 공동 개발한 Agentic Commerce Protocol(ACP)이 ChatGPT Instant Checkout 기능으로 구현되었다.

**주요 특징**:
- Apache 2.0 오픈소스 라이선스
- 물리적/디지털 상품, 구독, 비동기 구매 지원
- Shared Payment Token으로 결제 정보 보안

**첫 구현**: ChatGPT Instant Checkout
- 미국 내 Etsy 판매자와의 직접 거래 지원
- Shopify 판매자(Glossier, Vuori, Spanx, SKIMS 등) 100만개 이상 연동 예정

**파트너십**:
- Salesforce: ACP 기반 Instant Checkout 통합 발표
- commercetools: ACP 런치 파트너로 참여
- Microsoft Copilot, Anthropic, Perplexity, Vercel 등과 협력 중

> 출처:
> - [Stripe Blog - Developing an open standard for agentic commerce](https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce)
> - [GitHub - Agentic Commerce Protocol](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol)
> - [OpenAI Commerce Developers](https://developers.openai.com/commerce/guides/get-started/)

---

### 1.3 A2A (Agent-to-Agent) 프로토콜 업데이트

**Linux Foundation 이관** (2025년 6월 23일):
- Google이 개발한 A2A 프로토콜이 Linux Foundation 산하 프로젝트로 이관
- 100개 이상 기술 기업 지원

**Version 0.3 출시** (2025년 7월 31일):
- gRPC 지원 추가
- Security Card 서명 기능
- Python SDK 클라이언트 측 지원 확장
- 150개 이상 조직으로 생태계 확대

**기업 적용 사례**:
- Tyson Foods와 Gordon Food Service: A2A 기반 공급망 에이전트 시스템 도입

> 출처:
> - [Google Cloud Blog - Agent2Agent protocol is getting an upgrade](https://cloud.google.com/blog/products/ai-machine-learning/agent2agent-protocol-is-getting-an-upgrade)
> - [Linux Foundation - A2A Project Launch](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)

---

### 1.4 주요 결제사 동향

#### Mastercard Agent Pay
- **2025년 4월**: Agentic Payments Program 발표
- **2025년 9월 29일**: 최초의 실제 에이전틱 결제 거래 완료
- **Mastercard Agentic Tokens**: 기존 토큰화 기술 기반의 에이전트 전용 토큰

> 출처: [Mastercard News - Agentic Commerce Standards](https://www.mastercard.com/global/en/news-and-trends/stories/2026/agentic-commerce-standards.html)

#### Visa Intelligent Commerce
- **2025년 4월 30일**: Intelligent Commerce 프로그램 발표
- **파트너**: Anthropic, IBM, Microsoft, Mistral AI, OpenAI, Perplexity, Samsung, Stripe
- **Agent Token**: 에이전트 ID와 세분화된 지출 제어 기능 포함
- **Trusted Agent Protocol**: Cloudflare와 공동 개발, 실시간 에이전트 신원 검증
- **상용화 시점**: 2026년 Q1 예상

> 출처:
> - [Digital Commerce 360 - Visa Mastercard launch agentic AI payments tools](https://www.digitalcommerce360.com/2025/10/16/visa-mastercard-both-launch-agentic-ai-payments-tools/)
> - [CNBC - Payment giants preparing for AI agents](https://www.cnbc.com/2025/12/29/ai-agentic-shopping-price-discounts-cheap-sales-commerce-visa-mastercard-chatbots.html)

#### PayPal 다중 플랫폼 전략
- **Mastercard 파트너십** (2025년 10월): Agent Pay를 PayPal 지갑에 통합
- **ChatGPT 통합**: 2026년부터 PayPal을 통한 ChatGPT 내 구매 지원
- **Perplexity Instant Buy** (2025년 11월 25일): 6,000개 이상 판매자 지원

> 출처:
> - [PayPal Newsroom - Mastercard Partnership](https://newsroom.paypal-corp.com/2025-10-27-Mastercard-and-PayPal-Join-Forces-To-Accelerate-Secure-Global-Agentic-Commerce)
> - [PYMNTS - Visa Mastercard PayPal Fuel Agentic AI Commerce](https://www.pymnts.com/news/artificial-intelligence/2025/visa-mastercard-paypal-fuel-agentic-ai-commerce-boom/)

---

### 1.5 Agentic AI Foundation (AAIF) 출범

Linux Foundation 산하에 Agentic AI Foundation이 출범하여 업계 표준화를 추진한다.

**공동 설립자**: OpenAI, Anthropic, Block

**참여 기업**: Amazon Web Services, Google, Microsoft, Cisco, IBM, Oracle, Salesforce, SAP, Snowflake, Hugging Face 등

**핵심 프로젝트**:
1. **Model Context Protocol (MCP)**: Anthropic 기증, 10,000개 이상 MCP 서버 배포
2. **AGENTS.md**: 2025년 8월 출시 이후 60,000개 이상 오픈소스 프로젝트 채택
3. **Goose**: Block이 개발한 로컬 실행 AI 에이전트

> 출처:
> - [OpenAI - Agentic AI Foundation](https://openai.com/index/agentic-ai-foundation/)
> - [Block - Agentic AI Foundation Launch](https://block.xyz/inside/block-anthropic-and-openai-launch-the-agentic-ai-foundation)
> - [Tom's Hardware - Agentic AI Alliance](https://www.tomshardware.com/tech-industry/artificial-intelligence/microsoft-google-openai-and-anthropic-join-forces-to-form-agentic-ai-alliance-according-to-report-organization-backed-by-the-linux-foundation-is-set-to-create-open-source-standards-for-ai-agents)

---

## 2. 업계 반응 및 분석

### 2.1 개발자 커뮤니티 반응

#### 긍정적 반응
- **표준화 기대**: 업계 전반에서 상호운용성 있는 표준의 필요성 공감
- **오픈소스 접근**: AP2, ACP 모두 오픈소스로 공개되어 개발자 접근성 확보
- **SDK 지원**: Python, TypeScript 등 다양한 언어 SDK 제공

#### 우려 사항
- **프로토콜 파편화**: AP2, ACP, x402 등 복수의 프로토콜이 병존하여 판매자 부담 증가
- **"각 프로토콜은 판매자에게 부담이다"** - 스타트업 창업자 의견
- **MCP로의 통합 추세**: A2A 개발이 다소 정체되고, MCP 중심으로 생태계 통합 진행 중

#### 스타트업 대응
- **Firmly**: 판매자가 단일 인터페이스로 복수의 프로토콜에 연결할 수 있는 솔루션 개발

> 출처:
> - [Modern Retail - AI Shopping Agent Wars](https://www.modernretail.co/technology/why-the-ai-shopping-agent-wars-will-heat-up-in-2026/)
> - [fka.dev - What happened to Google's A2A](https://blog.fka.dev/blog/2025-09-11-what-happened-to-googles-a2a/)

---

### 2.2 기술 블로그 및 분석

#### 주요 분석 관점

**Everest Group**:
- AP2를 "에이전틱 상거래의 새로운 장"으로 평가
- Mandate 시스템을 통한 신뢰 구축 메커니즘 긍정적 평가

**Orium**:
- ACP, AP2, x402 세 프로토콜의 비교 분석 제공
- **ACP**: OpenAI/Stripe 중심, 소비자 상거래 최적화
- **AP2**: Google 중심, 결제 방식 무관성 강조
- **x402**: Coinbase 중심, 암호화폐 마이크로페이먼트 특화

**Cloud Security Alliance**:
- AP2의 보안 프레임워크 분석
- Mandate 스푸핑, 에이전트 강제, 결제 데이터 노출 등 취약점과 완화 방안 제시

> 출처:
> - [Everest Group - Google's AP2](https://www.everestgrp.com/googles-agent-payments-protocol-ap2-a-new-chapter-in-agentic-commerce-blog/)
> - [Orium - Agentic Payments ACP AP2 x402](https://orium.com/blog/agentic-payments-acp-ap2-x402)
> - [Cloud Security Alliance - Secure Use of AP2](https://cloudsecurityalliance.org/blog/2025/10/06/secure-use-of-the-agent-payments-protocol-ap2-a-framework-for-trustworthy-ai-driven-transactions)

---

### 2.3 경쟁사 움직임

#### Anthropic
- **Agent Skills 표준 공개**: 엔터프라이즈 AI 에이전트를 위한 개방형 표준
- **MCP 기증**: Agentic AI Foundation에 Model Context Protocol 기증
- **파트너 Skills 디렉토리**: Atlassian, Figma, Canva, Stripe, Notion, Zapier 등 참여

> 출처: [VentureBeat - Anthropic launches enterprise Agent Skills](https://venturebeat.com/technology/anthropic-launches-enterprise-agent-skills-and-opens-the-standard)

#### Microsoft
- **Agent Skills 통합**: VS Code에 Agent Skills 기능 내장
- **NRF 2025 발표** (2025년 1월): 리테일용 에이전틱 AI 솔루션 공개
  - Shopify 판매자용 Brand Agents
  - Copilot Studio 개인화 쇼핑 에이전트 템플릿
- **Visa Intelligent Commerce 파트너**

> 출처: [Microsoft Source - Agentic AI Retail Capabilities](https://news.microsoft.com/source/2026/01/08/microsoft-propels-retail-forward-with-agentic-ai-capabilities-that-power-intelligent-automation-for-every-retail-function/)

#### Amazon
- **Rufus AI 쇼핑 어시스턴트**: "Auto Buy" 버튼 도입
- 사용자가 목표 가격 또는 할인율 설정 시 자동 구매 실행

> 출처: [CNBC - Payment giants preparing for AI agents](https://www.cnbc.com/2025/12/29/ai-agentic-shopping-price-discounts-cheap-sales-commerce-visa-mastercard-chatbots.html)

---

## 3. 관련 프로젝트 및 구현 사례

### 3.1 AP2/A2A 관련 오픈소스 프로젝트

#### A2A x402 Extension
- **저장소**: [github.com/google-agentic-commerce/a2a-x402](https://github.com/google-agentic-commerce/a2a-x402)
- **기능**: A2A 프로토콜에 암호화폐 결제 기능 추가
- **아키텍처**: Functional Core + Imperative Shell
- **파트너**: Coinbase, Ethereum Foundation, MetaMask

#### AP2 공식 저장소
- **저장소**: [github.com/google-agentic-commerce/AP2](https://github.com/google-agentic-commerce/AP2)
- **내용**: 기술 스펙, 문서, 레퍼런스 구현
- **샘플**: Android 및 Python 시나리오 예제

#### TypeScript 구현체
- **저장소**: [github.com/dabit3/a2a-x402-typescript](https://github.com/dabit3/a2a-x402-typescript)
- **기능**: Python x402 결제 프로토콜의 TypeScript 버전
- **용도**: AI 에이전트의 암호화폐 결제 요청, 검증, 정산

#### x402 Protocol (Coinbase)
- **저장소**: [github.com/coinbase/x402](https://github.com/coinbase/x402)
- **설명**: HTTP 네이티브 결제를 위한 개방형 표준
- **지원**: 암호화폐 및 법정화폐 모두 지원 목표

#### awesome-x402
- **저장소**: [github.com/xpaysh/awesome-x402](https://github.com/xpaysh/awesome-x402)
- **내용**: x402 관련 리소스 큐레이션
- **포함**: SDK(TypeScript, Python, Rust), Facilitator(Coinbase, Cloudflare), MCP 통합 예제

> 출처:
> - [GitHub - A2A x402](https://github.com/google-agentic-commerce/a2a-x402)
> - [GitHub - Coinbase x402](https://github.com/coinbase/x402)
> - [GitHub - AP2](https://github.com/google-agentic-commerce/AP2)

---

### 3.2 에이전트 상거래 스타트업

#### Sierra (고객 서비스 AI)
- **창업자**: Bret Taylor (전 Salesforce 공동 CEO)
- **펀딩**: 2025년 9월 $350M 투자 유치, 기업가치 $10B 이상
- **투자자**: Greenoaks Capital

#### Decagon (고객 서비스 AI 에이전트)
- **펀딩**: Series C $131M, 기업가치 $15억
- **투자자**: Accel, Andreessen Horowitz

#### Parallel (AI 에이전트용 웹 인프라)
- **펀딩**: 2025년 11월 Series A $100M
- **투자자**: Index Ventures, Kleiner Perkins

#### OmniAgentPay
- **저장소**: [github.com/omniagentpay/omniagentpay](https://github.com/omniagentpay/omniagentpay)
- **기능**: x402, UCP, AP2 등 결제 프로토콜의 실행 로직, 안전 제어, 개발자 경험 제공

> 출처:
> - [TechCrunch - 49 US AI startups that raised $100M+ in 2025](https://techcrunch.com/2025/11/26/here-are-the-49-us-ai-startups-that-have-raised-100m-or-more-in-2025/)
> - [AI Funding Tracker - Top 50 AI Startups](https://aifundingtracker.com/top-50-ai-startups/)

---

### 3.3 기업 적용 사례

#### 리테일
- **Etsy**: ChatGPT Instant Checkout 첫 번째 파트너
- **Shopify**: ACP 기반 100만+ 판매자 연동 예정

#### 식품 공급망
- **Tyson Foods, Gordon Food Service**: A2A 기반 에이전트 시스템으로 제품 데이터 및 리드 실시간 공유

#### 엔터프라이즈
- **Salesforce**: ACP 지원 발표, Stripe와 협력
- **commercetools**: ACP 런치 파트너
- **PwC**: Stripe와 에이전틱 상거래 전략 컨설팅 협력

---

## 4. 시장 전망

### 4.1 시장 규모 예측

#### AI 에이전트 시장 전체

| 조사 기관 | 2025년 | 2030년 | CAGR |
|----------|--------|--------|------|
| MarketsandMarkets | $78.4억 | $526.2억 | 46.3% |
| Grand View Research | - | $503.1억 | 45.8% |
| BCC Research | $80억 | $483억 | 43.3% |
| MarkNtel Advisors | $53.2억 | $427억 | 41.5% |

#### 에이전틱 상거래 시장

| 조사 기관 | 2025년 | 2030년 |
|----------|--------|--------|
| Edgar Dunn & Co | $1,360억 거래량 | $1.7조 |
| McKinsey & Company | - | 미국 $1조, 글로벌 $3~5조 |
| Bain & Company | - | 미국 $3,000~5,000억 (e-commerce의 15~25%) |

#### 소비자 채택률
- AI 쇼핑 플랫폼의 2026년 전체 리테일 e-commerce 비중: **1.5%** ($209억)
- 2025년 대비 약 4배 성장

> 출처:
> - [MarketsandMarkets - AI Agents Market](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp)
> - [Digital Commerce 360 - McKinsey forecast](https://www.digitalcommerce360.com/2025/10/20/mckinsey-forecast-5-trillion-agentic-commerce-sales-2030/)
> - [Bain & Company - Agentic AI Retail Forecast](https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/)

---

### 4.2 주요 플레이어 전략

#### Google
- **수직 통합 전략**: A2A(에이전트 통신) + AP2(에이전트 결제) + MCP 호환성
- **오픈 표준 주도**: Linux Foundation 협력, 150개 이상 파트너
- **크로스 플랫폼**: Gemini, Google Cloud Marketplace 연동

#### OpenAI/Stripe
- **소비자 직접 접점**: ChatGPT Instant Checkout으로 사용자 경험 장악
- **ACP 표준화**: 오픈소스 프로토콜로 생태계 확장
- **판매자 네트워크**: Shopify, Etsy 등 대형 판매 플랫폼 확보

#### Visa/Mastercard
- **결제 인프라 장악**: 기존 토큰화 기술 기반 에이전트 토큰 개발
- **신뢰 프로토콜**: Trusted Agent Protocol (Visa), Agent Pay (Mastercard)
- **금융기관 파트너십**: 발급사/인수사 네트워크 활용

#### Amazon
- **e-commerce 플랫폼 통합**: Rufus AI로 자체 생태계 내 에이전트 쇼핑
- **Auto Buy 기능**: 조건부 자동 구매 선점

---

### 4.3 투자 동향

#### 2025년 AI 투자 현황
- **북미 스타트업 총 투자**: $2,800억 (전년 대비 46% 증가)
- **AI 관련 투자**: $1,680억 (전체의 약 60%)
- **AI 에이전트 스타트업**: 2025년 ~$28억 투자, 연말까지 $67억 예상

#### 대형 투자 라운드 (2025년)
| 기업 | 투자액 | 기업가치 | 주요 투자자 |
|-----|-------|---------|-----------|
| OpenAI | $400억 | $3,000억 | SoftBank, Thrive Capital, Microsoft |
| Anthropic | $130억 (Series F) | $1,830억 | Iconiq, Fidelity, Lightspeed |
| Anysphere (Cursor) | $23억 | $293억 | - |
| Thinking Machines Lab | $20억 (Seed) | $100억 | Andreessen Horowitz |
| Sierra | $3.5억 | $100억+ | Greenoaks Capital |

> 출처:
> - [Crunchbase - North American Startup Funding 2025](https://news.crunchbase.com/venture/north-american-startup-funding-2025-data-ai-us-investment/)
> - [AI Certs - 33 US Startups Cross $100M+](https://www.aicerts.ai/news/ai-funding-33-us-startups-cross-100m-investment-in-2025/)
> - [Finro - AI Agents Valuation Multiples](https://www.finrofca.com/news/ai-agents-valuation-2025)

---

## 5. 보안 및 규제 이슈

### 5.1 보안 위협

#### Visa 보고서 주요 내용
- **다크웹 AI Agent 관련 게시물**: 지난 6개월간 **450% 이상 급증**
- **악성 봇 거래**: 글로벌 **25% 증가**
- **새로운 위협**: "Compromised Agent-as-a-Service" - 단일 탈취된 프로필이 수십 개 상점에서 사기 구매 가능

#### 주요 공격 벡터
- 합법적으로 보이는 웹사이트, 위조 컴플라이언스 문서, 가짜 기업 신원 생성
- 에이전트 조작을 통한 자동화된 사기
- "인간 결정 포인트" 부재로 인한 엔드투엔드 사기 자동화

> 출처:
> - [Visa - Threats Landscape of Agentic Commerce](https://corporate.visa.com/en/sites/visa-perspectives/security-trust/the-threats-landscape-of-agentic-commerce.html)
> - [Digital Commerce 360 - Visa flags fraud risks](https://www.digitalcommerce360.com/2025/11/21/visa-flags-fraud-risks-agentic-commerce/)

---

### 5.2 책임 소재 문제

#### 핵심 질문
- AI 에이전트 오류 시 누가 책임지는가?
- 에이전트 개발사? 사용자? 판매자?
- "카드 미제시(Card-Not-Present)"에서 "인간 미존재(Person-Not-Present)"로 전환

#### 환불 및 분쟁 증가 전망
- 사용자가 거래 뒤의 판매자를 인식하지 못하는 경우 증가
- "친선 사기(Friendly Fraud)" 증가 예상
- 판매자 입증 책임 복잡화: 에이전트가 시작한 거래의 적절한 인증 증명 방법?

> 출처:
> - [Chargeback Gurus - Agentic Commerce Chargebacks](https://www.chargebackgurus.com/blog/agentic-commerce-chargebacks)
> - [The Paypers - Fraud in the age of agentic](https://thepaypers.com/fraud-and-fincrime/expert-views/fraud-in-the-age-of-agentic-who-bears-the-risk)

---

### 5.3 규제 동향

#### EU 규제
- **EU AI Act**: 미준수 시 벌금 및 법적 책임
- **EU 제조물 책임 지침** (2026년 12월 시행): AI를 "제품"으로 명시, 결함 시 엄격 책임

#### 2026년 예상 표준화 항목
- 투명한 동의 흐름
- 세분화된 사용자 권한
- 에이전트 행동 로그
- 안전한 결제 승인
- 오버라이드 메커니즘
- 정책 기반 가드레일

#### 새로운 개념
- **KYA (Know Your Agent)**: FIS가 2026년 Q1까지 제공 예정
- **TRiSM 스택**: Trust, Risk, Security Management

---

## 6. 시사점

### 6.1 발표/학습 활용 포인트

1. **프로토콜 경쟁 구도 이해**
   - AP2 (Google) vs ACP (OpenAI/Stripe) vs 기존 결제사 솔루션
   - 단일 표준보다 상호운용성이 핵심

2. **Mandate 시스템의 중요성**
   - Intent/Cart/Payment Mandate의 3단계 검증이 신뢰의 기반
   - 암호화 서명 기반 부인 방지

3. **기술 스택 구성**
   - MCP (도구 연결) + A2A (에이전트 통신) + AP2/x402 (결제)
   - 레이어별 역할 분리

4. **보안 고려사항**
   - 에이전트 신원 검증 (KYA)
   - 사기 탐지 시스템 적응
   - 책임 소재 명확화

5. **시장 기회**
   - 2030년 조 단위 시장 규모 예상
   - 결제 인프라 vs 플랫폼 vs 에이전트 레이어 진입점 선택

### 6.2 추가 연구 주제

- AP2 Mandate 생성/검증 구현 실습
- x402를 활용한 마이크로페이먼트 데모
- MCP + A2A + AP2 통합 아키텍처 설계
- 에이전트 상거래 보안 모델 심층 분석

---

## 참고 자료 전체 목록

### 공식 문서 및 발표
- [Google Cloud Blog - Announcing Agent Payments Protocol](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [TechCrunch - Google launches new protocol for agent-driven purchases](https://techcrunch.com/2025/09/16/google-launches-new-protocol-for-agent-driven-purchases/)
- [Stripe Blog - Developing an open standard for agentic commerce](https://stripe.com/blog/developing-an-open-standard-for-agentic-commerce)
- [OpenAI - Agentic AI Foundation](https://openai.com/index/agentic-ai-foundation/)
- [Linux Foundation - A2A Project Launch](https://www.linuxfoundation.org/press/linux-foundation-launches-the-agent2agent-protocol-project-to-enable-secure-intelligent-communication-between-ai-agents)

### 분석 및 블로그
- [Everest Group - Google's AP2](https://www.everestgrp.com/googles-agent-payments-protocol-ap2-a-new-chapter-in-agentic-commerce-blog/)
- [Orium - Agentic Payments ACP AP2 x402](https://orium.com/blog/agentic-payments-acp-ap2-x402)
- [Vellum - Google's AP2 Protocol](https://www.vellum.ai/blog/googles-ap2-a-new-protocol-for-ai-agent-payments)
- [CMSWire - Google Pushes Standards for Agentic AI Commerce](https://www.cmswire.com/digital-experience/google-pushes-standards-for-agentic-ai-commerce-with-ap2/)

### 시장 전망
- [MarketsandMarkets - AI Agents Market](https://www.marketsandmarkets.com/PressReleases/ai-agents.asp)
- [McKinsey - Agentic Commerce Forecast](https://www.digitalcommerce360.com/2025/10/20/mckinsey-forecast-5-trillion-agentic-commerce-sales-2030/)
- [Bain & Company - Agentic AI Retail Forecast](https://www.bain.com/insights/2030-forecast-how-agentic-ai-will-reshape-us-retail-snap-chart/)
- [Commercetools - 7 AI Trends Shaping Agentic Commerce](https://commercetools.com/blog/ai-trends-shaping-agentic-commerce)

### 투자 및 스타트업
- [Crunchbase - North American Startup Funding 2025](https://news.crunchbase.com/venture/north-american-startup-funding-2025-data-ai-us-investment/)
- [TechCrunch - 49 US AI startups that raised $100M+](https://techcrunch.com/2025/11/26/here-are-the-49-us-ai-startups-that-have-raised-100m-or-more-in-2025/)
- [Finro - AI Agents Valuation Multiples](https://www.finrofca.com/news/ai-agents-valuation-2025)

### 보안 및 규제
- [Visa - Threats Landscape of Agentic Commerce](https://corporate.visa.com/en/sites/visa-perspectives/security-trust/the-threats-landscape-of-agentic-commerce.html)
- [Cloud Security Alliance - Secure Use of AP2](https://cloudsecurityalliance.org/blog/2025/10/06/secure-use-of-the-agent-payments-protocol-ap2-a-framework-for-trustworthy-ai-driven-transactions)
- [Mastercard - Agentic Commerce Standards](https://www.mastercard.com/global/en/news-and-trends/stories/2026/agentic-commerce-standards.html)

### GitHub 저장소
- [AP2 공식 저장소](https://github.com/google-agentic-commerce/AP2)
- [A2A x402 Extension](https://github.com/google-agentic-commerce/a2a-x402)
- [Coinbase x402](https://github.com/coinbase/x402)
- [Agentic Commerce Protocol (ACP)](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol)
- [awesome-x402](https://github.com/xpaysh/awesome-x402)

---

*작성일: 2026-01-25*
*Week 6 최신 동향 조사*
