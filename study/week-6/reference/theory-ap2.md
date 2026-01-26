# 에이전트 상거래의 미래와 Google AP2의 접근 방식

## 개요

에이전트 상거래(Agentic Commerce)는 AI 에이전트가 소비자 또는 기업을 대신하여 상품과 서비스를 연구, 협상, 구매하는 새로운 상거래 패러다임이다. Google의 AP2(Agent Payments Protocol)는 이러한 에이전트 주도 거래를 안전하고 검증 가능하게 만들기 위한 개방형 프로토콜로, 2025년 9월에 발표되었다.

---

## 1. 에이전트 상거래(Agentic Commerce)란?

### 1.1 정의와 개념

에이전트 상거래는 자율적인 AI 에이전트가 소비자를 대신하여 구매 관련 의사결정을 시작, 관리, 실행하는 상거래 모델이다. 핵심 특징은 다음과 같다:

- **자율적 의사결정**: 인간의 직접적인 개입 없이 AI가 구매 결정
- **대리 행위**: 사용자의 의도와 선호를 기반으로 에이전트가 대리 행동
- **지속적 학습**: 거래 패턴을 학습하여 점점 더 정교한 구매 결정

### 1.2 기존 전자상거래와의 차이점

| 구분 | 기존 전자상거래 | 에이전트 상거래 |
|------|----------------|----------------|
| **의사결정 주체** | 인간이 직접 클릭하여 구매 | AI 에이전트가 대리 구매 |
| **승인 시점** | 구매 시점에 인간이 승인 | 사전 조건 설정 후 자동 승인 가능 |
| **검색/비교** | 사용자가 직접 수행 | 에이전트가 자동으로 최적 상품 탐색 |
| **협상** | 제한적 또는 불가능 | 에이전트 간 실시간 협상 가능 |
| **결제 시점** | Point of Intent = Point of Checkout | 분리 가능 (의도 표현 vs 실제 결제) |

### 1.3 AI 에이전트가 주도하는 거래의 특징

**인간 존재(Human-Present) 시나리오**:
- 사용자가 실시간으로 최종 승인
- 장바구니 확인 후 결제 진행
- 기존 전자상거래와 유사한 흐름

**인간 부재(Human-Not-Present) 시나리오**:
- 사전 설정된 조건에 따라 자동 구매
- 예: "콘서트 티켓이 판매 시작되면 즉시 120달러 이하로 구매"
- 에이전트가 조건 충족 시 자율적으로 거래 완료

### 1.4 시장 전망

- 2030년까지 전 세계 전자상거래 거래 가치의 **30%**가 에이전트 AI의 영향을 받을 것으로 예상 (약 17.5조 달러)
- Morgan Stanley 예측: 2030년까지 온라인 쇼핑객의 절반이 AI 쇼핑 에이전트 사용
- IBM 연구: 소비자의 45%가 이미 구매 여정의 일부에서 AI 활용 (2026년)

---

## 2. Google AP2 (Agent Payments Protocol) 아키텍처

### 2.1 핵심 설계 원칙

AP2는 다음 세 가지 핵심 문제를 해결하기 위해 설계되었다:

1. **권한 부여(Authorization)**: 사용자가 에이전트에게 특정 구매에 대한 권한을 부여했음을 증명
2. **진정성(Authenticity)**: 에이전트의 요청이 사용자의 진정한 의도를 반영함을 보장
3. **책임 소재(Accountability)**: 사기 또는 오류 발생 시 책임 소재 명확화

**설계 철학**:
- 결제 방식에 구애받지 않음 (Payment-agnostic)
- 개방형 표준으로 상호 운용성 보장
- 암호화 기반의 부인 방지(Non-repudiation)

### 2.2 역할 기반 생태계

```
+------------------+     +-------------------+     +------------------+
|      User        |     |   Shopping Agent  |     |  Merchant Agent  |
|  (최종 권한자)    |<--->|    (UA/SA)        |<--->|      (ME)        |
+------------------+     +-------------------+     +------------------+
         |                       |                        |
         v                       v                        v
+------------------+     +-------------------+     +------------------+
| Credentials      |     |   A2A Protocol    |     | Merchant Payment |
| Provider (CP)    |<--->|   (통신 계층)      |<--->| Processor (MPP)  |
+------------------+     +-------------------+     +------------------+
                                 |
                                 v
                    +-------------------------+
                    |  Network / Issuer       |
                    |  (결제 인프라)           |
                    +-------------------------+
```

**주요 참여자**:
- **사용자(User)**: 최종 재정 권한 보유자
- **쇼핑 에이전트(SA)**: 사용자와 상호작용, 상품 검색, 장바구니 구성
- **인증 제공자(CP)**: 결제 자격 증명 안전 관리
- **판매자 에이전트(ME)**: 판매자 대표, 장바구니 세부사항 협상
- **판매자 결제 처리자(MPP)**: 결제 승인 메시지 구성

### 2.3 Mandate(위임장) 시스템

AP2의 핵심은 **검증 가능한 디지털 자격 증명(VDC: Verifiable Digital Credentials)**인 Mandate이다.

#### Cart Mandate (장바구니 위임장)
- **용도**: Human-Present 시나리오
- **내용**: 최종 거래 상품, 배송지, 금액, 통화, 이행 조건
- **서명**: 판매자가 이행 보증을 위해 서명, 사용자가 승인을 위해 서명
- **특징**: 하드웨어 기반 키로 암호화 서명

#### Intent Mandate (의도 위임장)
- **용도**: Human-Not-Present 시나리오
- **내용**: AI 에이전트가 사용자를 대신해 구매할 수 있는 조건 정의
- **요소**: 승인된 결제 방법, 쇼핑 매개변수, 만료 시간(TTL)
- **특징**: 자연어로 표현된 사용자 의도를 에이전트가 해석

#### Payment Mandate (결제 위임장)
- **용도**: 결제 네트워크 및 발급사에 공유
- **기능**: AI 에이전트 개입 여부 및 사용자 존재 여부 신호 전달
- **목적**: 사기 방지 및 분쟁 해결 지원

### 2.4 결제 흐름 (Human-Present 시나리오)

```
1. 사용자 -> 쇼핑 에이전트: 쇼핑 프롬프트 제공
2. 쇼핑 에이전트 -> 인증 제공자: Intent Mandate 확인 요청
3. 쇼핑 에이전트 -> 인증 제공자: 결제 수단 조회
4. 쇼핑 에이전트 <-> 판매자 에이전트: 협상
5. 판매자 에이전트 -> 쇼핑 에이전트: Cart Mandate 생성 및 서명
6. 쇼핑 에이전트 -> 사용자: 신뢰할 수 있는 기기에서 최종 장바구니 제시
7. 사용자 -> Cart Mandate: 생체 인증/하드웨어 키로 서명
8. 쇼핑 에이전트: Payment Mandate 생성
9. 쇼핑 에이전트 -> 판매자: Payment Mandate와 함께 구매 제출
10. 판매자/PSP -> 발급사: AI 에이전트 존재 신호와 함께 거래 승인 요청
```

### 2.5 AP2와 A2A 프로토콜의 관계

```
+---------------------------+
|         MCP               |  <- 에이전트가 도구와 상호작용
+---------------------------+
|         A2A               |  <- 에이전트 간 통신 정의
+---------------------------+
|         AP2               |  <- 에이전트가 안전하게 거래
+---------------------------+
```

- **MCP (Model Context Protocol)**: 에이전트가 도구와 상호작용하는 방법 정의
- **A2A (Agent-to-Agent Protocol)**: 에이전트 간 통신 방법 정의
- **AP2**: 에이전트가 안전하게 금전 거래를 수행하는 메커니즘

AP2는 A2A를 기본 전송 메커니즘으로 사용하며, Agent Card에 AP2 지원을 다음과 같이 선언:

```json
{
  "extensions": [
    {
      "description": "Supports the A2A payments extension",
      "uri": "https://google-a2a.github.io/A2A/extensions/payments/v1"
    }
  ]
}
```

---

## 3. AP2의 기술적 접근 방식

### 3.1 결제 메커니즘 설계

**결제 방식 무관성 (Payment-Agnostic)**:
- 신용카드/직불카드 (Pull 결제)
- 실시간 은행 이체 (Push 결제)
- 스테이블코인 및 암호화폐
- 다양한 결제 방식 확장 가능

**동적 연결(Dynamic Linking)**:
- 거래 세부 정보를 결제 자격 증명에 암호화적으로 연결
- 결정론적 증명으로 에이전트 오류나 환각(hallucination) 위험 해소

### 3.2 보안 모델

#### 암호화 기반 신뢰
- **ECDSA 서명**: 모든 Mandate에 디지털 서명 필수
- **하드웨어 기반 키**: 기기 수준 증명을 통한 사용자 인증
- **페이로드 암호화**: 에이전트가 기능적으로 필요하지 않은 PCI/PII 데이터 접근 차단

#### 신뢰 모델
- 단기: 수동으로 관리되는 허용 목록(Allow Lists)
- 장기: HTTPS, DNS 소유권, 상호 TLS를 활용한 실시간 신원 보증

#### 인증 메커니즘 지원
- 3DS2 (3D Secure 2.0)
- OTP (일회용 비밀번호)
- 단계별 인증(Step-up Authentication)

#### 식별된 취약점 및 완화 방안

| 취약점 | 완화 방안 |
|--------|----------|
| Mandate 스푸핑 | 하드웨어 기반 키 관리 |
| 에이전트 강제(Coercion) | 분산형 허용 목록 |
| 결제 데이터 노출 | 토큰화 및 암호화 |

### 3.3 확장성 고려사항

**생태계 파트너십**:
- 60개 이상 조직 참여
- American Express, Mastercard, PayPal, Visa, Coinbase, Etsy, Salesforce, ServiceNow 등

**기업 사용 사례**:
- B2B 자율 조달
- 실시간 수요에 따른 소프트웨어 라이선스 자동 확장
- Google Cloud Marketplace를 통한 파트너 솔루션 자동 구매

### 3.4 다른 결제 프로토콜과의 비교

#### AP2 vs x402 비교

| 구분 | AP2 | x402 |
|------|-----|------|
| **주요 지지자** | Google, Mastercard, Visa, PayPal | Coinbase, Cloudflare |
| **결제 방식** | 다양한 결제 방식 지원 (카드, 은행, 암호화폐) | 스테이블코인 (USDC) 중심 |
| **핵심 메커니즘** | 암호화 서명된 Mandate | HTTP 402 상태 코드 활용 |
| **결제 정산** | 기존 결제 네트워크 활용 | 온체인 직접 정산 |
| **정산 시간** | 기존 카드 네트워크 의존 | 2초 미만 |
| **프로토콜 수수료** | 기존 결제 수수료 적용 | 제로 프로토콜 수수료 |
| **적합 용도** | 고가치 B2C 거래, 소비자 보호 필요 시 | 고빈도 저가치 M2M 거래, API 수익화 |

#### 상호 보완적 관계

AP2와 x402는 경쟁이 아닌 상호 보완 관계이다:
- **A2A x402 확장**: Google이 Coinbase와 협력하여 개발
- x402는 AP2 프레임워크 내에서 스테이블코인 결제 레일로 동작
- AP2가 신뢰 프레임워크(Mandate) 제공, x402가 실제 정산 처리

**"Mullet Economy" 개념**:
- **앞면(B2C)**: AP2/ACP로 고가치 소비자 거래, 환불 보호 필요
- **뒷면(B2B/M2M)**: x402로 백엔드 자동화, API 수익화, 마이크로서비스

---

## 4. 에이전트 상거래의 미래 전망

### 4.1 예상되는 사용 사례

**소비자 영역**:
- 실시간 가격 모니터링 및 자동 구매
- 개인화된 쇼핑 에이전트
- 여행 예약 및 이벤트 티켓 자동 구매
- 정기 구독 최적화 및 자동 갱신

**기업 영역**:
- 자율 조달(Autonomous Procurement)
- ERP 에이전트 간 실시간 협상
- 클라우드 리소스 자동 스케일링 및 결제
- 공급망 자동화

**B2B/M2M 영역**:
- API 호출당 마이크로페이먼트
- 데이터 라이선싱 자동화
- IoT 기기 간 결제
- AI 서비스 간 실시간 정산

### 4.2 도전 과제

#### 기술적 도전
- **사기 탐지 시스템 적응**: 기존 사기 탐지 시스템이 에이전트 행동을 봇으로 오인할 수 있음
- **에이전트 환각(Hallucination)**: 잘못된 상품 선택 또는 가격 오류
- **상호 운용성**: 다양한 에이전트 플랫폼 간 호환성

#### 신뢰 구축
- **KYA (Know Your Agent)**: 에이전트 신원 확인 체계 필요
- **에이전트 vs 봇 구분**: Visa의 Trusted Agent Protocol 등 개발 중
- **감사 추적**: 모든 거래에 대한 추적 가능한 로그 필요

#### 소비자 우려
- IBM 연구: 소비자의 83%가 프라이버시, 데이터 오용, 원치 않는 마케팅에 대해 우려

### 4.3 규제 및 법적 고려사항

#### 현재 규제 공백

에이전트 결제 관련 규제는 아직 정의되지 않은 상태이다. 기업들은 기존 프레임워크의 해석에 의존하여 컴플라이언스 전략을 수립해야 한다.

#### 주요 법적 이슈

| 영역 | 과제 |
|------|------|
| **데이터 동의** | 각 거래별 명시적 인간 승인 없이 AI 에이전트의 개인정보 처리 권한 |
| **계약 형성** | AI 에이전트의 오류 구매나 환각 시 책임 소재 |
| **사기 방지** | AI 에이전트 조작에 대한 보안 (25% 취약률 보고) |
| **알고리즘 투명성** | 에이전트의 상품 선택 방식 소비자 이해 보장 |

#### EU 규제 동향
- **GDPR**: 에이전트의 개인정보 처리에 대한 명확한 가이드 부재
- **EU AI Act**: 준수하지 않을 경우 벌금 및 법적 책임
- **EU 제조물 책임 지침** (2026년 12월 시행): 소프트웨어와 AI를 "제품"으로 명시적 포함, AI 시스템이 "결함"으로 판명되면 엄격 책임 적용

#### 결제 네트워크 규정
- **PCI 준수**: 에이전트 개입 시에도 결제 데이터 처리, 토큰 사용, 저장 모델 준수 필요
- **AML (자금세탁방지)**: 에이전트의 자율성이 기존 AML 프로그램의 가정에 도전
- **환불 및 분쟁**: 에이전트가 결제를 시작해도 판매자가 사기, 환불, 컴플라이언스에 대한 책임 유지

#### 산업 대응 동향

**2026년 표준화 예상 항목**:
- 투명한 동의 흐름
- 세분화된 사용자 권한
- 에이전트 행동 로그
- 안전한 결제 승인
- 오버라이드 메커니즘
- 정책 기반 가드레일

**새로운 개념 도입**:
- **TRiSM 스택**: Trust(신뢰), Risk(위험), Security Management(보안 관리)
- **설명 가능성**: 소비자 권리로 부상, 감사 가능한 로그가 규제 요건화 전망
- **KYA (Know Your Agent)**: FIS가 2026년 Q1 말까지 제공 예정

---

## 참고 자료

### 공식 문서
- [Google Cloud Blog - AP2 발표](https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol)
- [AP2 공식 문서](https://ap2-protocol.org/)
- [AP2 스펙 문서](https://ap2-protocol.org/specification/)
- [AP2 GitHub 저장소](https://github.com/google-agentic-commerce/AP2)
- [A2A x402 Extension GitHub](https://github.com/google-agentic-commerce/a2a-x402)

### 분석 및 해설
- [McKinsey - The Agentic Commerce Opportunity](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-agentic-commerce-opportunity-how-ai-agents-are-ushering-in-a-new-era-for-consumers-and-merchants)
- [IBM - What Is Agentic Commerce?](https://www.ibm.com/think/topics/agentic-commerce)
- [Everest Group - Google's AP2: A New Chapter in Agentic Commerce](https://www.everestgrp.com/googles-agent-payments-protocol-ap2-a-new-chapter-in-agentic-commerce-blog/)
- [Cloud Security Alliance - Secure Use of AP2](https://cloudsecurityalliance.org/blog/2025/10/06/secure-use-of-the-agent-payments-protocol-ap2-a-framework-for-trustworthy-ai-driven-transactions)

### 프로토콜 비교
- [Medium - AI Agents and Autonomous Payments: x402 vs AP2](https://medium.com/@gwrx2005/ai-agents-and-autonomous-payments-a-comparative-study-of-x402-and-ap2-protocols-e71b572d9838)
- [AP2 공식 문서 - AP2 and x402](https://ap2-protocol.org/topics/ap2-and-x402/)
- [Orium - Agentic Payments: ACP, AP2, and x402](https://orium.com/blog/agentic-payments-acp-ap2-x402)

### 규제 및 법률
- [TLT - Agentic Commerce: The Next Legal Frontier](https://www.tlt.com/insights-and-events/insight/agentic-commerce---the-next-legal-frontier-in-ai-powered-shopping)
- [Mastercard - Trusting AI to Buy: Agentic Commerce Standards](https://www.mastercard.com/global/en/news-and-trends/stories/2026/agentic-commerce-standards.html)
- [Crowe - Agentic Commerce: Risk Management Challenges](https://www.crowe.com/insights/fincrime-in-context/agentic-commerce-risk-management-challenges)

### 시장 전망
- [Commercetools - 7 AI Trends Shaping Agentic Commerce in 2026](https://commercetools.com/blog/ai-trends-shaping-agentic-commerce)
- [Visa - Secure AI Transactions Milestone](https://usa.visa.com/about-visa/newsroom/press-releases.releaseId.21961.html)

---

*작성일: 2026-01-25*
*Week 6 이론 정리*
