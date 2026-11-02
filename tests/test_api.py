import os

import pytest

from conftest import check_domain, random_domain

pytestmark = pytest.mark.api

NO_KEY_REASON = "New finding: API works without a key (docs say a key is required)"


@pytest.fixture(scope="module")
def google_response():
    # One call shared by API-01, API-03, API-04 and API-13.
    return check_domain("google.com")


@pytest.fixture(scope="module")
def clean_answer():
    # The answer for the clean form, used to compare the messy forms in E-02.
    response = check_domain("mybakery.com")
    assert response.status_code == 200
    return response.json()["availability"]["available"]


# ---------- Happy path and contract ----------

def test_api_01_taken_domain_is_not_available(google_response):
    assert google_response.status_code == 200
    assert google_response.json()["availability"]["available"] is False


def test_api_02_random_domain_is_available():
    response = check_domain(random_domain())
    assert response.status_code == 200
    assert response.json()["availability"]["available"] is True


def test_api_03_response_fields_and_types(google_response):
    availability = google_response.json()["availability"]
    assert isinstance(availability["domain"], str)
    assert isinstance(availability["available"], bool)
    assert isinstance(availability["premium"], bool)
    assert isinstance(availability["premiumType"], str)


def test_api_04_answer_is_for_the_domain_sent(google_response):
    assert google_response.json()["availability"]["domain"] == "google.com"


def test_api_13_one_call_is_under_5_seconds(google_response):
    assert google_response.elapsed.total_seconds() < 5


# ---------- Authentication (docs: an account-level API key is required) ----------

@pytest.mark.xfail(strict=True, reason=NO_KEY_REASON)
def test_api_05_no_authorization_header_is_rejected():
    headers = {"wix-account-id": os.environ["WIX_ACCOUNT_ID"]}
    response = check_domain("google.com", headers=headers)
    assert response.status_code != 200
    assert "availability" not in response.text


@pytest.mark.xfail(strict=True, reason=NO_KEY_REASON)
def test_api_06_wrong_key_is_rejected():
    headers = {"Authorization": "not-a-real-key", "wix-account-id": os.environ["WIX_ACCOUNT_ID"]}
    response = check_domain("google.com", headers=headers)
    assert response.status_code != 200
    assert "availability" not in response.text


@pytest.mark.xfail(strict=True, reason=NO_KEY_REASON)
def test_api_07_no_account_id_header_gives_clear_error():
    headers = {"Authorization": os.environ["WIX_API_KEY"]}
    response = check_domain("google.com", headers=headers)
    assert 400 <= response.status_code < 500
    assert response.json().get("message")


# ---------- Bad requests ----------

def test_api_08_no_domain_parameter():
    response = check_domain(None)
    assert response.status_code == 400
    assert response.json()["message"]


def test_api_09_empty_domain():
    response = check_domain("")
    assert response.status_code == 400
    assert response.json()["message"]


def test_api_10_tld_that_does_not_exist():
    response = check_domain("mybakery.notarealtld")
    assert response.status_code == 400
    assert "INVALID_DOMAIN" in response.text


@pytest.mark.parametrize("domain", [None, "", "mybakery.notarealtld"])
def test_api_11_errors_do_not_show_internal_details(domain):
    body = check_domain(domain).text.lower()
    for word in ["traceback", "exception", ".java", "at com.", "stack"]:
        assert word not in body


# ---------- E-02: bad or messy input ----------

@pytest.mark.parametrize("domain", [
    "MyBakery.com",
    " mybakery.com ",
    "www.mybakery.com",
    "https://mybakery.com",
])
def test_e02_messy_input_gives_error_or_same_answer(domain, clean_answer):
    response = check_domain(domain)
    if response.status_code == 400:
        assert response.json()["message"]
    else:
        assert response.status_code == 200
        assert response.json()["availability"]["available"] == clean_answer


@pytest.mark.parametrize("domain", [
    "mybakery",        # no TLD
    "-mybakery.com",   # hyphen at the start
    "mybakery-.com",   # hyphen at the end
    "my_bakery.com",   # "_" is not allowed
    "mybakery!.com",   # "!" is not allowed
    pytest.param(      # 64 characters, the docs allow 63 at most
        "a" * 60 + ".com",
        marks=pytest.mark.xfail(strict=True, reason="Docs say max 63 characters, the API accepts 64"),
    ),
])
def test_e02_impossible_name_gives_400(domain):
    response = check_domain(domain)
    assert response.status_code == 400
    assert response.json()["message"]


@pytest.mark.parametrize("domain", [
    "x.com",           # 1-letter name
    "a" * 59 + ".com", # 63 characters, the docs maximum
])
def test_e02_valid_edge_name_gets_an_answer(domain):
    response = check_domain(domain)
    assert response.status_code == 200
    assert isinstance(response.json()["availability"]["available"], bool)


# ---------- E-03: non-English names (IDN) ----------

def test_e03_punycode_gets_an_answer():
    # xn--4dbioaw1b is the ASCII (punycode) form of the Hebrew word for "bakery".
    response = check_domain("xn--4dbioaw1b.com")
    assert response.status_code == 200
    assert isinstance(response.json()["availability"]["available"], bool)


def test_e03_hebrew_form_gives_clear_400():
    # The docs say only alphanumeric characters, hyphens and dots are supported.
    response = check_domain("מאפייה.com")
    assert response.status_code == 400
    assert response.json()["message"]
