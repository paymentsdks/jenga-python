from __future__ import annotations

import argparse
import json
import sys

from .client import JengaClient
from .exceptions import JengaError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI for Jenga API operations")
    subparsers = parser.add_subparsers(dest="command", required=True)

    balance_parser = subparsers.add_parser("account-balance", help="Fetch account balance")
    balance_parser.add_argument("--country-code", required=True)
    balance_parser.add_argument("--account-id", required=True)

    statement_parser = subparsers.add_parser("mini-statement", help="Fetch mini statement")
    statement_parser.add_argument("--country-code", required=True)
    statement_parser.add_argument("--account-id", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        client = JengaClient.from_env()

        if args.command == "account-balance":
            result = client.account_balance(country_code=args.country_code, account_id=args.account_id)
        else:
            result = client.mini_statement(country_code=args.country_code, account_id=args.account_id)
    except JengaError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
