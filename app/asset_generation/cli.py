from __future__ import annotations

import argparse
import json
from typing import Any

from app.config import load_config

from .service import make_asset_generation_service


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Backend CLI for generated asset candidates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("templates-list", help="List prompt templates.")

    templates_inspect = subparsers.add_parser("templates-inspect", help="Inspect one prompt template.")
    templates_inspect.add_argument("--template", required=True)

    context = subparsers.add_parser("context", help="Print generation context for an agent/CMS.")
    context.add_argument("--template", default="food.cutout.square")

    draft = subparsers.add_parser("draft", help="Build a prompt without calling a provider.")
    draft.add_argument("--template", default="food.cutout.square")
    draft.add_argument("--subject", required=True)
    draft.add_argument("--target-asset-key", default="")

    generate = subparsers.add_parser("generate", help="Generate and store candidate assets.")
    generate.add_argument("--template", default="food.cutout.square")
    generate.add_argument("--subject", required=True)
    generate.add_argument("--count", type=int, default=1)
    generate.add_argument("--target-asset-key", default="")
    generate.add_argument("--requested-by", default="cli")

    subparsers.add_parser("candidates-list", help="List stored candidates.")

    candidates_inspect = subparsers.add_parser("candidates-inspect", help="Inspect one stored candidate.")
    candidates_inspect.add_argument("candidate_id")

    approve = subparsers.add_parser("approve", help="Approve candidate into mounted approved storage.")
    approve.add_argument("candidate_id")
    approve.add_argument("--asset-key", required=True)
    approve.add_argument("--approved-by", default="cli")

    args = parser.parse_args(argv)
    service = make_asset_generation_service(load_config())

    if args.command == "templates-list":
        _print_json({"ok": True, "templates": service.list_templates()})
        return
    if args.command == "templates-inspect":
        _print_json({"ok": True, "context": service.generation_context(args.template)})
        return
    if args.command == "context":
        _print_json({"ok": True, "context": service.generation_context(args.template)})
        return
    if args.command == "draft":
        _print_json(
            {
                "ok": True,
                "draft": service.draft_prompt(
                    args.template,
                    args.subject,
                    target_asset_key=args.target_asset_key,
                ),
            }
        )
        return
    if args.command == "generate":
        _print_json(
            {
                "ok": True,
                "candidates": service.generate_candidates(
                    args.template,
                    args.subject,
                    count=args.count,
                    target_asset_key=args.target_asset_key,
                    requested_by=args.requested_by,
                ),
            }
        )
        return
    if args.command == "candidates-list":
        _print_json({"ok": True, "candidates": service.list_candidates()})
        return
    if args.command == "candidates-inspect":
        _print_json({"ok": True, "candidate": service.inspect_candidate(args.candidate_id)})
        return
    if args.command == "approve":
        _print_json(
            {
                "ok": True,
                "candidate": service.approve_candidate(
                    args.candidate_id,
                    args.asset_key,
                    approved_by=args.approved_by,
                ),
            }
        )
        return

    parser.error("Unknown command.")


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

