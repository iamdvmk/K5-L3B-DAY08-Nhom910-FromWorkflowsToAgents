"""Shape B — one ReAct agent. Student work.

Use `lab8.runtime.run_react` with max_steps=8. `decide` may pick a read tool.
It must not call `issue_refund`. After the loop, the host validates the quote
and is the only writer.

A decide() that trusts ticket text over the order row will fail hidden claims
where the customer overstates the delay or cites a superseded clause.

Per-order cap: an order may already have been refunded by an earlier claim.
The read tool `lookup_refund_history` shows how much. The host still enforces
the cap, so pass the full quote to `durability.issue_refund`, not a net amount.

Caps: stop at 8 steps. Count model calls in the Budget so cost stays comparable.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

from lab8.db import connect
from lab8.durability import issue_refund
from lab8.mock_llm import complete
from lab8.runtime import run_react
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish
from lab8.tools import compute_compensation, get_claim_view, lookup_order, tool_cost
from lab8.trace import Trace


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    budget = Budget()
    trace = Trace(make_run_id("single", claim_id, seed))
    try:
        budget.add_tool(tool_cost())
        claim = get_claim_view(conn, claim_id)
        # Never put the raw ticket (which may contain PII) in the trace.
        trace.add("claim", {"found": claim["found"], "claim_id": claim_id})
        state = {}

        def decide(observation):
            last_tool = observation.get("last_tool")
            if last_tool:
                state[last_tool] = observation["last_result"]
                trace.add("read", {"tool": last_tool})

            complete(budget, seed=seed, purpose="decide", prompt=(
                f"claim={claim_id}; completed={','.join(state)}"
            ))
            if not claim["found"]:
                return {"final": {"status": "failed", "error_reason": "unknown_claim"}}
            if not claim.get("order_id"):
                return {"final": {"status": "needs_info", "error_reason": "missing_order_id"}}

            scope_args = {"order_id": claim["order_id"], "principal_id": claim["principal_id"]}
            if "lookup_order" not in state:
                return {"tool": "lookup_order", "args": scope_args}
            order_view = state["lookup_order"]
            if not order_view["visible"]:
                return {"final": {"status": "escalated", "error_reason": order_view["reason"]}}
            if "lookup_refund_history" not in state:
                return {"tool": "lookup_refund_history", "args": scope_args}
            if "compute_compensation" not in state:
                return {"tool": "compute_compensation", "args": {"order": order_view["order"]}}
            return {"final": {"quote": state["compute_compensation"]}}

        result = run_react(
            conn, budget, observation={"claim": claim}, decide=decide, max_steps=8,
            worker=True,
        )
        final = result["final"]
        proposal = 0
        status = final.get("status", "failed")
        error_reason = final.get("error_reason")
        if "quote" in final:
            # Independently validate against the scoped order and current policy.
            budget.add_tool(tool_cost())
            order_view = lookup_order(conn, claim["order_id"], claim["principal_id"])
            if not order_view["visible"]:
                status, error_reason = "escalated", order_view["reason"]
            else:
                budget.add_tool(tool_cost())
                quote = compute_compensation(conn, order_view["order"])
                proposal = int(quote["amount_vnd"])
                trace.add("quote", quote)
                if final["quote"] != quote:
                    status, error_reason = "failed", "quote_mismatch"
                elif proposal <= 0:
                    status, error_reason = "denied", quote["reason"]
                else:
                    budget.add_tool(tool_cost())
                    outcome = issue_refund(conn, claim_id, proposal, crash_at=crash_at)
                    trace.add("refund", {"ok": outcome["ok"], "reason": outcome["reason"]})
                    status = "resolved" if outcome["ok"] else (
                        "failed" if outcome["conflict"] else "denied"
                    )
                    error_reason = None if outcome["ok"] else outcome["reason"]
        trace.add("decision", {"status": status, "error_reason": error_reason})
        return finish(
            conn, shape="single", claim_id=claim_id, seed=seed, status=status,
            proposal_amount=proposal, budget=budget, trace=trace, error_reason=error_reason,
        )
    finally:
        conn.close()
