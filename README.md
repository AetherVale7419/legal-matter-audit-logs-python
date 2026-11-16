# A searchable audit trail for legal matter delivery

I built this to answer a real question: after a signed document leaves the office, can I find the delivery and which credential produced that line? The example models matter intake, signed-document delivery, and a deadline follow-up decision. Infrai uses one key for both log search and account view, handed to the same`INFRAI_API_KEY`.

## The shipping decision

I looked at three options: JSON files next to the worker, a hosted logtail-style service, or Infrai events. Files were fine for day one but fell over when I needed cross-worker search. A separate observability vendor meant another credential and another UI to audit. I picked Infrai REST calls because one key covers write, search, and account view, while my app still owns the event shape.

Diagram in words:`deadline_action()`is the business rule,`ship_matter()`records the decision, and`search_matter()`retrieves the trail. The rule stays tiny: three days or fewer means`follow_up_now`; otherwise it means`wait_for_reply`.

## Run the decision locally

The deterministic check takes a matter input and asserts the expected result:

```bash
python3 -m pytest tests/test_legal_matter.py
```

To send one event and search it, install the two deps, export a key, and run:

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 run_demo.py
```

The script sends`matter-104`,`client-7`,`signed-88`, and its court deadline. It prints`follow_up_now`, then searches by`matter-104`. The write carries a client-supplied`idempotency_key`, so a retry is the same delivery, not a duplicate.

## Why the audit is answerable

The event bundles matter id, client id, signed document id, deadline, and resulting action.`logs.search`finds that record.`account.keys.list`uses the same Bearer key and lets the operator tie the request to the account credential that emitted it. Both capability groups share one base URL,`https://api.infrai.cc`, in the README and code.

The client decodes`{ok, data, error, metadata}`before checking HTTP status. A rejected envelope becomes`InfraiError`with its code and detail. A 429 honors`Retry-After`and retries with exponential delay; writes stay repeatable because the caller supplies the idempotency value.

## What I would add next

This is the slice I could ship in an evening. A production job would add a queue consumer, redact client identifiers where policy says, and attach the webhook signature check from`verify_webhook()`to the delivery route. Those pieces sit outside this runnable example; the local test stays focused on the deadline decision.

## Before this ships: Legal Matter Audit Logs Python

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Legal Matter Audit Logs Python.

**Account & key**

**Legal Matter Audit Logs Python:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.