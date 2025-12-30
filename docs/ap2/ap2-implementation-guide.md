# AP2 Protocol Implementation Guide

## 시작하기

AP2 프로토콜을 구현하려면 먼저 A2A 프로토콜에 대한 이해가 필요합니다. AP2는 A2A의 확장이기 때문입니다.

### 전제 조건

1. **A2A 프로토콜 이해**: [A2A Implementation Guide](../a2a/a2a-implementation-guide.md) 참고
2. **SDK 설치**: A2A SDK 설치 (Python, JavaScript 등)
3. **역할 선택**: merchant, shopper, credentials-provider, payment-processor 중 선택

## 역할별 구현 가이드

### 1. Merchant Agent 구현

판매자 에이전트는 제품을 판매하고 CartMandate를 생성합니다.

#### Agent Card 정의

```python
from python_a2a import AgentCard, AgentSkill

merchant_card = AgentCard(
    name="My Store Agent",
    description="Sales assistant for MyStore.com",
    url="https://mystore.com/agent",
    version="1.0.0",
    capabilities={
        "extensions": [
            {
                "description": "Supports AP2 payments",
                "required": True,
                "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
                "params": {
                    "roles": ["merchant"]
                }
            }
        ]
    },
    skills=[
        AgentSkill(
            name="Search Catalog",
            description="Search products in our catalog",
            tags=["search", "products", "catalog"]
        ),
        AgentSkill(
            name="Create Cart",
            description="Create a shopping cart",
            tags=["cart", "checkout"]
        )
    ]
)
```

#### CartMandate 생성

```python
import json
from datetime import datetime
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend

class MerchantAgent:
    def __init__(self, private_key):
        self.private_key = private_key

    def create_cart_mandate(self, cart_items, total_amount):
        """CartMandate 생성 및 서명"""

        # CartMandate 내용 생성
        cart_mandate = {
            "contents": {
                "id": f"cart_{datetime.now().timestamp()}",
                "user_signature_required": False,
                "payment_request": {
                    "method_data": [
                        {
                            "supported_methods": "CARD",
                            "data": {
                                "payment_processor_url": "https://mystore.com/pay"
                            }
                        }
                    ],
                    "details": {
                        "id": f"order_{datetime.now().timestamp()}",
                        "displayItems": cart_items,
                        "total": {
                            "label": "Total",
                            "amount": {
                                "currency": "USD",
                                "value": total_amount
                            }
                        }
                    },
                    "options": {
                        "requestShipping": True
                    }
                }
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # 서명 생성
        message = json.dumps(cart_mandate["contents"], sort_keys=True).encode()
        signature = self.private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        cart_mandate["merchant_signature"] = signature.hex()

        return cart_mandate

    def handle_search_catalog(self, query, max_price=None):
        """카탈로그 검색 스킬"""
        # 제품 검색 로직
        products = self.search_products(query, max_price)
        return products

    def handle_create_cart(self, product_ids):
        """장바구니 생성 스킬"""
        items = []
        total = 0

        for product_id in product_ids:
            product = self.get_product(product_id)
            items.append({
                "label": product["name"],
                "amount": {
                    "currency": "USD",
                    "value": product["price"]
                }
            })
            total += product["price"]

        # CartMandate 생성
        cart_mandate = self.create_cart_mandate(items, total)

        return cart_mandate
```

### 2. Shopping Agent 구현

쇼핑 에이전트는 사용자를 대신하여 구매를 진행합니다.

#### Agent Card 정의

```python
shopping_card = AgentCard(
    name="My Shopping Assistant",
    description="Personal shopping assistant",
    url="https://myshopper.com/agent",
    version="1.0.0",
    capabilities={
        "extensions": [
            {
                "description": "Supports AP2 payments",
                "required": True,
                "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
                "params": {
                    "roles": ["shopper"]
                }
            }
        ]
    },
    skills=[
        AgentSkill(
            name="Search Products",
            description="Search products across merchants",
            tags=["search", "shopping"]
        ),
        AgentSkill(
            name="Compare Prices",
            description="Compare prices across merchants",
            tags=["compare", "price"]
        )
    ]
)
```

#### 구매 흐름 구현

```python
from python_a2a import A2AClient, Message, TextContent, MessageRole

class ShoppingAgent:
    def __init__(self):
        self.merchants = {}
        self.credentials_provider = None

    async def search_and_buy(self, user_query, max_price=None):
        """제품 검색 및 구매"""

        # 1. 판매자 에이전트에게 제품 검색
        merchant_client = A2AClient("https://merchant.com/agent")

        search_message = Message(
            content=TextContent(
                text=f"search_catalog: {user_query}, max_price: {max_price}"
            ),
            role=MessageRole.USER
        )

        products = await merchant_client.send_message(search_message)

        # 2. 사용자에게 제품 보여주기
        selected_product = self.present_to_user(products)

        # 3. 결제 방법 확인
        payment_methods = await self.get_payment_methods()
        selected_payment = self.select_payment_method(payment_methods)

        # 4. 장바구니 생성 요청
        cart_message = Message(
            content=TextContent(
                text=f"create_cart: [{selected_product['id']}]"
            ),
            role=MessageRole.USER
        )

        cart_mandate = await merchant_client.send_message(cart_message)

        # 5. CartMandate 검증
        if self.verify_cart_mandate(cart_mandate):
            # 6. 결제 처리
            payment_result = await self.process_payment(
                cart_mandate,
                selected_payment
            )

            if payment_result.success:
                # 7. 주문 확인
                order = await self.confirm_order(merchant_client, payment_result)
                return order

        return None

    async def get_payment_methods(self):
        """Credentials Provider에서 결제 방법 가져오기"""
        if not self.credentials_provider:
            self.credentials_provider = A2AClient("https://credentials.com/agent")

        message = Message(
            content=TextContent(text="get_eligible_payment_methods"),
            role=MessageRole.USER
        )

        methods = await self.credentials_provider.send_message(message)
        return methods

    def verify_cart_mandate(self, cart_mandate):
        """CartMandate 서명 검증"""
        # 판매자 서명 검증 로직
        # 가격, 항목 등 확인
        return True

    async def process_payment(self, cart_mandate, payment_method):
        """Payment Processor를 통해 결제 처리"""
        processor = A2AClient("https://processor.com/agent")

        message = Message(
            content=TextContent(
                text=json.dumps({
                    "cart_mandate": cart_mandate,
                    "payment_method": payment_method
                })
            ),
            role=MessageRole.USER
        )

        result = await processor.send_message(message)
        return result
```

### 3. Credentials Provider 구현

사용자의 결제 정보를 안전하게 관리합니다.

#### OAuth2 보안 설정

```python
credentials_card = AgentCard(
    name="Secure Wallet",
    description="Secure payment credentials storage",
    url="https://wallet.com/agent",
    version="1.0.0",
    capabilities={
        "extensions": [
            {
                "description": "Supports AP2 payments",
                "required": True,
                "uri": "https://google-a2a.github.io/A2A/ext/payments/v1",
                "params": {
                    "roles": ["credentials-provider"]
                }
            }
        ]
    },
    security=[
        {
            "oauth2": ["get_payment_methods", "get_shipping_address"]
        }
    ],
    securitySchemes={
        "oauth2": {
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "https://wallet.com/oauth/authorize",
                    "scopes": {
                        "get_payment_methods": "Access payment methods",
                        "get_shipping_address": "Access shipping address"
                    },
                    "tokenUrl": "https://wallet.com/oauth/token"
                }
            },
            "type": "oauth2"
        }
    },
    skills=[
        AgentSkill(
            name="Get Eligible Payment Methods",
            description="Get user's payment methods",
            tags=["payment", "methods"]
        ),
        AgentSkill(
            name="Get Shipping Address",
            description="Get user's shipping address",
            tags=["shipping", "address"]
        )
    ]
)
```

#### 결제 방법 관리

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

app = FastAPI()

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://wallet.com/oauth/authorize",
    tokenUrl="https://wallet.com/oauth/token"
)

class CredentialsProvider:
    def __init__(self):
        self.payment_methods = {}  # user_id -> payment_methods
        self.shipping_addresses = {}  # user_id -> addresses

    async def get_payment_methods(self, user_id: str, token: str):
        """인증된 사용자의 결제 방법 반환"""
        # OAuth2 토큰 검증
        user = self.verify_token(token)
        if user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        methods = self.payment_methods.get(user_id, [])
        return methods

    async def get_shipping_address(self, user_id: str, token: str):
        """인증된 사용자의 배송 주소 반환"""
        user = self.verify_token(token)
        if user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        address = self.shipping_addresses.get(user_id)
        return address

@app.post("/agent/message")
async def handle_message(
    message: dict,
    token: str = Depends(oauth2_scheme)
):
    """A2A 메시지 처리"""
    provider = CredentialsProvider()

    skill = message.get("content", {}).get("text", "")

    if skill == "get_eligible_payment_methods":
        user = verify_token(token)
        methods = await provider.get_payment_methods(user["id"], token)
        return {"methods": methods}

    elif skill == "get_account_shipping_address":
        user = verify_token(token)
        address = await provider.get_shipping_address(user["id"], token)
        return {"address": address}

    return {"error": "Unknown skill"}
```

### 4. Payment Processor 구현

실제 결제를 처리합니다.

```python
class PaymentProcessor:
    def __init__(self, processor_api_key):
        self.api_key = processor_api_key

    async def process_payment(self, cart_mandate, payment_method):
        """결제 처리"""

        # 1. CartMandate 검증
        if not self.verify_mandate(cart_mandate):
            return {"success": False, "error": "Invalid mandate"}

        # 2. 결제 금액 추출
        total = cart_mandate["contents"]["payment_request"]["details"]["total"]
        amount = total["amount"]["value"]
        currency = total["amount"]["currency"]

        # 3. 결제 처리 (실제 결제 게이트웨이 호출)
        result = await self.charge_payment_method(
            payment_method,
            amount,
            currency
        )

        if result["status"] == "approved":
            # 4. 결제 증명 생성
            payment_proof = self.create_payment_proof(
                cart_mandate,
                result
            )

            return {
                "success": True,
                "transaction_id": result["transaction_id"],
                "proof": payment_proof
            }
        else:
            return {
                "success": False,
                "error": result.get("error_message")
            }

    def verify_mandate(self, cart_mandate):
        """CartMandate 서명 검증"""
        # 판매자 공개키로 서명 검증
        merchant_signature = cart_mandate["merchant_signature"]
        contents = cart_mandate["contents"]

        # 서명 검증 로직
        return True

    async def charge_payment_method(self, payment_method, amount, currency):
        """결제 게이트웨이를 통한 결제"""
        # Stripe, PayPal 등 실제 결제 API 호출
        # 예: Stripe API
        import stripe
        stripe.api_key = self.api_key

        try:
            charge = stripe.Charge.create(
                amount=int(amount * 100),  # cents
                currency=currency.lower(),
                source=payment_method["token"],
                description="AP2 Payment"
            )

            return {
                "status": "approved",
                "transaction_id": charge.id
            }
        except stripe.error.CardError as e:
            return {
                "status": "declined",
                "error_message": str(e)
            }
```

## 보안 구현

### 1. 암호화 서명

```python
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

# 키 쌍 생성
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

public_key = private_key.public_key()

# 서명 생성
def sign_data(data, private_key):
    message = json.dumps(data, sort_keys=True).encode()
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature.hex()

# 서명 검증
def verify_signature(data, signature_hex, public_key):
    message = json.dumps(data, sort_keys=True).encode()
    signature = bytes.fromhex(signature_hex)

    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except:
        return False
```

### 2. Risk Data 수집

```python
def collect_risk_data(request):
    """거래 위험 데이터 수집"""
    risk_data = {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "device_fingerprint": request.headers.get("x-device-id"),
        "timestamp": datetime.utcnow().isoformat(),
        "geolocation": get_geolocation(request.client.host),
        "transaction_amount": request.json().get("amount"),
        "merchant_id": request.json().get("merchant_id")
    }

    # 사기 점수 계산
    risk_data["fraud_score"] = calculate_fraud_score(risk_data)

    return risk_data
```

## 테스팅

### 단위 테스트

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def merchant_agent():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return MerchantAgent(private_key)

def test_create_cart_mandate(merchant_agent):
    """CartMandate 생성 테스트"""
    items = [
        {
            "label": "Test Product",
            "amount": {"currency": "USD", "value": 99.99}
        }
    ]

    mandate = merchant_agent.create_cart_mandate(items, 99.99)

    assert mandate is not None
    assert "contents" in mandate
    assert "merchant_signature" in mandate
    assert mandate["contents"]["payment_request"]["details"]["total"]["amount"]["value"] == 99.99

def test_verify_cart_mandate():
    """CartMandate 검증 테스트"""
    # 유효한 mandate
    valid_mandate = create_test_mandate()
    assert verify_cart_mandate(valid_mandate) == True

    # 변조된 mandate
    tampered_mandate = valid_mandate.copy()
    tampered_mandate["contents"]["payment_request"]["details"]["total"]["amount"]["value"] = 1000
    assert verify_cart_mandate(tampered_mandate) == False
```

### 통합 테스트

```python
@pytest.mark.asyncio
async def test_full_payment_flow():
    """전체 결제 흐름 통합 테스트"""

    # 1. Shopping Agent가 제품 검색
    shopping_agent = ShoppingAgent()
    products = await shopping_agent.search_products("shoes")
    assert len(products) > 0

    # 2. 결제 방법 가져오기
    payment_methods = await shopping_agent.get_payment_methods()
    assert len(payment_methods) > 0

    # 3. CartMandate 생성
    cart_mandate = await shopping_agent.create_cart(products[0]["id"])
    assert cart_mandate is not None

    # 4. 결제 처리
    payment_result = await shopping_agent.process_payment(
        cart_mandate,
        payment_methods[0]
    )
    assert payment_result["success"] == True
```

## 배포

### Docker 컨테이너화

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 앱 코드 복사
COPY . .

# 환경 변수
ENV AP2_PRIVATE_KEY_PATH=/app/keys/private_key.pem
ENV AP2_PUBLIC_KEY_PATH=/app/keys/public_key.pem

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes 배포

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: merchant-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: merchant-agent
  template:
    metadata:
      labels:
        app: merchant-agent
    spec:
      containers:
      - name: agent
        image: myregistry/merchant-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: AP2_ROLE
          value: "merchant"
        - name: PRIVATE_KEY
          valueFrom:
            secretKeyRef:
              name: ap2-keys
              key: private-key
        volumeMounts:
        - name: keys
          mountPath: /app/keys
          readOnly: true
      volumes:
      - name: keys
        secret:
          secretName: ap2-keys
```

## 모범 사례

1. **항상 HTTPS 사용**: 프로덕션 환경에서는 반드시 HTTPS
2. **서명 검증**: 모든 CartMandate 서명 검증
3. **OAuth2 인증**: Credentials Provider는 반드시 OAuth2 사용
4. **Risk Data 수집**: 모든 거래에 대해 위험 데이터 수집
5. **로깅**: 모든 거래에 대한 감사 로그 유지
6. **에러 처리**: 명확한 에러 메시지 및 적절한 HTTP 상태 코드
7. **Rate Limiting**: API 호출 제한으로 남용 방지
8. **모니터링**: 거래 성공률, 응답 시간 등 모니터링

## 다음 단계

- [AP2 Examples](./ap2-examples.md) - 실전 예제 및 사용 사례
- [AP2 Architecture](./ap2-architecture.md) - 아키텍처 상세
- [A2A Implementation Guide](../a2a/a2a-implementation-guide.md) - A2A 구현 가이드
