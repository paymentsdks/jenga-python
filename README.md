# Jenga API SDK for Python

[![CI](https://github.com/paymentsdks/jenga-python/actions/workflows/ci.yml/badge.svg)](https://github.com/paymentsdks/jenga-python/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/paymentsdks-jenga.svg)](https://pypi.org/project/paymentsdks-jenga/)
[![PyPI downloads](https://img.shields.io/pypi/dm/paymentsdks-jenga.svg)](https://pypi.org/project/paymentsdks-jenga/)
[![Python versions](https://img.shields.io/pypi/pyversions/paymentsdks-jenga.svg)](https://pypi.org/project/paymentsdks-jenga/)
[![License](https://img.shields.io/pypi/l/paymentsdks-jenga.svg)](https://pypi.org/project/paymentsdks-jenga/)

A Python package for interacting with selected Jenga API endpoints.

- Reads configuration from environment variables
- Generates access tokens
- Signs request values with your RSA private key using `cryptography`
- Provides both Python and CLI usage

## 1. Installation

```bash
pip install paymentsdks-jenga
```

## 2. Configuration

The package reads configuration from environment variables. The required variables are:

```env
JENGA_API_KEY=
JENGA_MERCHANT_CODE=
JENGA_CONSUMER_SECRET=
JENGA_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nreplace-with-private-key\n-----END PRIVATE KEY-----"
JENGA_LIVE_MODE=false
```

Generate an RSA key pair with OpenSSL before setting `JENGA_PRIVATE_KEY`:

```bash
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:2048
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

- Save the contents of `private_key.pem` in `JENGA_PRIVATE_KEY`.
- Save the contents of `public_key.pem` in the Jenga dashboard under the Keys section.

> [!INFO]
> - `JENGA_LIVE_MODE=true` uses `https://api.finserve.africa` white `JENGA_LIVE_MODE=false` uses `https://uat.finserve.africa`
> - For PEM values, you can use either real multiline values or `\n`-escaped text in `.env` files.

If you are using a local `.env` file, load it into your shell before running commands:

## 3. Usage

### 3.1 Signature generation

Request signing is handled internally by `JengaClient` before protected endpoint calls are made.

If you need to generate a signature manually:

```python
from jenga import JengaClient

client = JengaClient.from_env()
signature = client.sign("KE", "1450160649886")
```

The data is signed in the order it is passed.

### 3.1 Python usage

Use the package directly in your application code.

```python
from jenga import JengaClient

client = JengaClient.from_env()

balance = client.account_balance(
    country_code="KE",
    account_id="1450160649886",
)

statement = client.mini_statement(
    country_code="KE",
    account_id="1450160649886",
)
```

## 4. Endpoint Coverage

### 4.1 Account Services

<details>

<summary><strong>4.1.1 Account Balance</strong></summary>

Python:

```python
from jenga import JengaClient

client = JengaClient.from_env()
result = client.account_balance(country_code="KE", account_id="1450160649886")
print(result)
```

CLI:

```bash
PYTHONPATH=src python3 -m jenga.cli account-balance --country-code KE --account-id 1450160649886
```

</details>

<details>

<summary><strong>4.1.2 Account Mini Statement</strong></summary>

Python:

```python
from jenga import JengaClient

client = JengaClient.from_env()
result = client.mini_statement(country_code="KE", account_id="1450160649886")
print(result)
```

CLI:

```bash
PYTHONPATH=src python3 -m jenga.cli mini-statement --country-code KE --account-id 1450160649886
```

</details>

- [ ] Account Full Statement
- [ ] Opening and Closing Account Balance
- [ ] Account Inquiry - Bank Accounts

### 4.2 Send Money

- [ ] Within Equity Bank
- [ ] To Mobile Wallets
- [ ] RTGS
- [ ] SWIFT
- [ ] Pesalink - To Bank Account
- [ ] Pesalink - To Mobile Number

### 4.3 Send Money - IMT

- [ ] IMT Within Equity Bank
- [ ] IMT to Mobile Wallets
- [ ] IMT Pesalink - To Bank Account
- [ ] IMT Pesalink - To Bank Mobile

### 4.4 Receive Money

- [ ] Receive Payments - Bill Payments
- [ ] Receive Payments - Merchant Payments
- [ ] Bill Validation

### 4.5 Receive Money Queries

- [ ] Get All EazzyPay Merchants
- [ ] Query Transaction Details
- [ ] Get All Billers

### 4.6 Airtime

- [ ] Purchase Airtime

### 4.7 Forex Rates

- [ ] Forex Exchange Rates

### 4.8 ID Search and Verification

- [ ] ID Search and Verification

### 4.9 MPGS Direct Integration

- [ ] MPGS Validate Payment
- [ ] MPGS Authenticate Payment
- [ ] MPGS Authorize Payment
- [ ] MPGS Query Payment
- [ ] MPGS Refund Payment

## 5. Testing

Run the automated tests:

```bash
python3 -m unittest discover -s tests
```

Run a real manual test with your local `.env`:

```bash
set -a
source .env
set +a
PYTHONPATH=src python3 -m jenga.cli account-balance --country-code KE --account-id 1450160649886
```

## 6. Notes

- This package currently focuses on a small subset of Jenga APIs.
- The README only documents endpoints that are actually implemented in this repository.
- Pending endpoints are listed for roadmap visibility only.
- See the [contribution guide](./CONTRIBUTING.md) for development and pull request workflow.

## 7. Releases

- Tagged releases matching `v*` trigger GitHub Actions to test, build, and publish the package to PyPI automatically.
- Example tag: `v0.1.1`
- PyPI trusted publishing must be configured once for this repository before the workflow can publish.

## 8. License

License: [MIT](./LICENSE)
