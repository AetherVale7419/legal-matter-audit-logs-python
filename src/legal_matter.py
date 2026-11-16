from dataclasses import dataclass
from datetime import date
from typing import Any

from src.infrai_client import InfraiClient


@dataclass(frozen=True)
class MatterIntake:
    matter_id: str
    client_id: str
    court_deadline: date
    signed_document_id: str


def deadline_action(matter: MatterIntake, today: date) -> str:
    days_left = (matter.court_deadline - today).days
    return "follow_up_now" if days_left <= 3 else "wait_for_reply"


def ship_matter(client: InfraiClient, matter: MatterIntake, today: date) -> str:
    action = deadline_action(matter, today)
    event = {
        "message": f"Matter {matter.matter_id} delivery decision: {action}",
        "matter_id": matter.matter_id,
        "client_id": matter.client_id,
        "signed_document_id": matter.signed_document_id,
        "court_deadline": matter.court_deadline.isoformat(),
        "action": action,
    }
    client.ingest_log(event, idempotency_key=f"matter:{matter.matter_id}:delivery")
    return action


def search_matter(client: InfraiClient, matter_id: str) -> dict[str, Any]:
    return client.search_logs(matter_id)


def main() -> None:
    matter = MatterIntake("matter-104", "client-7", date(2026, 11, 2), "signed-88")
    client = InfraiClient()
    action = ship_matter(client, matter, date(2026, 10, 31))
    print(f"{matter.matter_id}: {action}")
    print(search_matter(client, matter.matter_id))
    print("The same key can list the account keys that produced the audit line.")
    print(client.list_keys())


if __name__ == "__main__":
    main()
