"""
pytest 공통 설정

모든 데모 테스트에서 사용하는 공통 fixture를 정의합니다.
"""

import pytest
import sys
import os

# 각 데모 폴더를 Python 경로에 추가
DEMOS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DEMOS_DIR, "a2a-ap2"))
sys.path.insert(0, os.path.join(DEMOS_DIR, "ucp"))
sys.path.insert(0, os.path.join(DEMOS_DIR, "x402"))


@pytest.fixture
def sample_user_credentials():
    """테스트용 사용자 자격 증명"""
    return {
        "userId": "test_user_001",
        "name": "테스트 사용자",
        "email": "test@example.com",
        "paymentToken": "tok_test_4242424242424242"
    }


@pytest.fixture
def sample_product():
    """테스트용 상품 데이터"""
    return {
        "id": "test-product-001",
        "name": "Test Product",
        "price": 99.99,
        "currency": "USD"
    }


@pytest.fixture
def sample_wallet_address():
    """테스트용 지갑 주소"""
    return "0xTestWallet1234567890abcdef1234567890abcdef"
