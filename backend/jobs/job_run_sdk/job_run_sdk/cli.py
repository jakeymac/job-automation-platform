import argparse
import json
import logging
import sys

from .client import get_job_state, set_job_run_email_content, set_job_run_state

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


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
        logger.info("Job run state updated successfully")

    elif args.command == "get_state":
        state = get_job_state()
        logger.info(json.dumps(state))

    elif args.command == "email_content":
        set_job_run_email_content(args.text)
        logger.info("Email content updated successfully")


if __name__ == "__main__":
    main()
