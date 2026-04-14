import argparse
import json

from .client import set_job_run_email_content, set_job_run_state


def main():
    parser = argparse.ArgumentParser(
        prog="job_run", description="CLI for interacting with the Job Run API"
    )

    subparsers = parser.add_subparsers(dest="command")

    # state
    state_parser = subparsers.add_parser("state")
    state_parser.add_argument("data")

    # email_content
    email_content_parser = subparsers.add_parser("email_content")
    email_content_parser.add_argument("text")

    args = parser.parse_args()

    if args.command == "state":
        data = json.loads(args.data)
        set_job_run_state(data)

    elif args.command == "email_content":
        set_job_run_email_content(args.text)


if __name__ == "__main__":
    main()
