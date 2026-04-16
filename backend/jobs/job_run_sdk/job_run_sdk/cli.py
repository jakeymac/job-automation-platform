import argparse
import json

from .client import set_job_run_email_content, set_job_run_state, get_job_state


def main():
    parser = argparse.ArgumentParser(
        prog="job_run", description="CLI for interacting with the Job Run API"
    )

    subparsers = parser.add_subparsers(dest="command")

    # set_state
    set_state_parser = subparsers.add_parser("set_state")
    set_state_parser.add_argument("data")

    # get_state
    subparsers.add_parser("get_state")

    # email_content
    email_content_parser = subparsers.add_parser("email_content")
    email_content_parser.add_argument("text")

    args = parser.parse_args()

    if args.command == "set_state":
        data = json.loads(args.data)
        set_job_run_state(data)
        print("Job run state updated successfully")

    elif args.command == "get_state":
        state = get_job_state()
        print(json.dumps(state))

    elif args.command == "email_content":
        set_job_run_email_content(args.text)
        print("Email content updated successfully")


if __name__ == "__main__":
    main()
