"""Orchestrate sending the shortlist review email."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from src.email_templates import review_id_from_generated_at, shortlist_email
from src.gmail_client import send_message
from src.review_state import load_shortlist, save_review


def send_shortlist_review() -> dict:
    shortlist = load_shortlist()
    review_id = review_id_from_generated_at(shortlist["generated_at"])
    subject, body = shortlist_email(review_id, shortlist)

    to_email = os.environ["REVIEW_TO_EMAIL"]
    sent = send_message(to_email, subject, body)

    state = {
        "review_id": review_id,
        "status": "pending_review",
        "generated_at": shortlist["generated_at"],
        "shortlist": shortlist,
        "gmail_message_id": sent["id"],
        "gmail_thread_id": sent["threadId"],
        "sent_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "to": to_email,
        "subject": subject,
        "processed_inbound_ids": [],
    }
    save_review(state)
    return state
