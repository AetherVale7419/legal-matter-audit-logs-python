from datetime import date

from src.legal_matter import MatterIntake, deadline_action


def test_matter_near_deadline_is_followed_up():
    matter = MatterIntake("matter-1", "client-1", date(2026, 11, 2), "signed-1")
    assert deadline_action(matter, date(2026, 10, 31)) == "follow_up_now"
    assert deadline_action(matter, date(2026, 10, 20)) == "wait_for_reply"
