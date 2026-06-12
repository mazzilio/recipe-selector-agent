"""Send the weekly shortlist review email via Gmail."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv

load_dotenv()

from src.review_workflow import send_shortlist_review


def main() -> None:
    state = send_shortlist_review()
    print(f"Sent shortlist review to {state['to']}")
    print(f"Review ID: {state['review_id']}")
    print(f"Thread ID: {state['gmail_thread_id']}")
    print(f"State saved to data/reviews/{state['review_id']}.json")


if __name__ == "__main__":
    main()
