#!/usr/bin/env python3
"""Reports, or with --apply fixes, how each repository differs from settings/repos.json.

Covers merge settings, private vulnerability reporting, Dependabot security updates and the
main-branch ruleset. Needs the gh CLI, signed in as an organization owner.
"""
import argparse
import json
import pathlib
import subprocess
import sys

OWNER = "greylocklabs"
SETTINGS = json.loads((pathlib.Path(__file__).parent.parent / "settings/repos.json").read_text())


def gh(method, path, body=None):
    args = ["gh", "api", "-X", method, path]
    if body is not None:
        args += ["--input", "-"]
    out = subprocess.run(args, input=json.dumps(body) if body is not None else None,
                         capture_output=True, text=True)
    if out.returncode != 0:
        return None, out.stdout or out.stderr
    return (json.loads(out.stdout) if out.stdout.strip() else {}), None


def wanted_ruleset(repo):
    ruleset = json.loads(json.dumps(SETTINGS["ruleset"]))
    ruleset["rules"].append({
        "type": "required_status_checks",
        "parameters": {
            "strict_required_status_checks_policy": repo["strict"],
            "required_status_checks": [{"context": c} for c in repo["checks"]],
        },
    })
    return ruleset


def comparable(ruleset):
    """The parts of a ruleset this script manages, in a form that compares equal when they match."""
    rules = {}
    for rule in ruleset.get("rules", []):
        params = dict(rule.get("parameters") or {})
        if rule["type"] == "pull_request":
            params = {k: params.get(k) for k in SETTINGS["ruleset"]["rules"][3]["parameters"]}
        if rule["type"] == "required_status_checks":
            params = {
                "strict": params.get("strict_required_status_checks_policy"),
                "checks": sorted(c["context"] for c in params.get("required_status_checks", [])),
            }
        rules[rule["type"]] = params
    return {
        "name": ruleset.get("name"),
        "enforcement": ruleset.get("enforcement"),
        "include": ruleset.get("conditions", {}).get("ref_name", {}).get("include"),
        "bypass": sorted((a["actor_type"], a["actor_id"], a["bypass_mode"])
                         for a in ruleset.get("bypass_actors", [])),
        "rules": rules,
    }


def main_ruleset(name):
    """The repository's own ruleset for its default branch, if it has one."""
    listed, _ = gh("GET", f"repos/{OWNER}/{name}/rulesets?includes_parents=false")
    for summary in listed or []:
        if summary.get("source_type") != "Repository" or summary.get("target") != "branch":
            continue
        ruleset, _ = gh("GET", f"repos/{OWNER}/{name}/rulesets/{summary['id']}")
        if "~DEFAULT_BRANCH" in ruleset.get("conditions", {}).get("ref_name", {}).get("include", []):
            return ruleset
    return None


def check(name, repo, apply):
    problems = []

    current, error = gh("GET", f"repos/{OWNER}/{name}")
    if error:
        return [f"cannot read the repository: {error.strip()}"]
    wrong = {k: v for k, v in SETTINGS["repository"].items() if current.get(k) != v}
    if wrong:
        problems.append("merge settings: " + ", ".join(f"{k} should be {v}" for k, v in wrong.items()))
        if apply:
            gh("PATCH", f"repos/{OWNER}/{name}", wrong)

    reporting, _ = gh("GET", f"repos/{OWNER}/{name}/private-vulnerability-reporting")
    if not (reporting or {}).get("enabled"):
        problems.append("private vulnerability reporting is off")
        if apply:
            gh("PUT", f"repos/{OWNER}/{name}/private-vulnerability-reporting")

    _, error = gh("GET", f"repos/{OWNER}/{name}/vulnerability-alerts")
    if error:
        problems.append("Dependabot alerts are off")
        if apply:
            gh("PUT", f"repos/{OWNER}/{name}/vulnerability-alerts")
    fixes, _ = gh("GET", f"repos/{OWNER}/{name}/automated-security-fixes")
    if not (fixes or {}).get("enabled"):
        problems.append("Dependabot security updates are off")
        if apply:
            gh("PUT", f"repos/{OWNER}/{name}/automated-security-fixes")

    want = wanted_ruleset(repo)
    have = main_ruleset(name)
    if have is None:
        problems.append("no ruleset protects the default branch")
        if apply:
            _, error = gh("POST", f"repos/{OWNER}/{name}/rulesets", want)
            if error:
                problems.append(f"creating the ruleset failed: {error.strip()}")
    elif comparable(have) != comparable(want):
        a, b = comparable(have), comparable(want)
        differ = [k for k in b if a.get(k) != b.get(k)]
        if a["rules"] != b["rules"]:
            differ.remove("rules")
            differ += [f"rule {t}" for t in sorted(set(a["rules"]) | set(b["rules"]))
                       if a["rules"].get(t) != b["rules"].get(t)]
        problems.append("ruleset differs: " + ", ".join(differ))
        if apply:
            _, error = gh("PUT", f"repos/{OWNER}/{name}/rulesets/{have['id']}", want)
            if error:
                problems.append(f"updating the ruleset failed: {error.strip()}")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true", help="change repositories to match")
    parser.add_argument("repos", nargs="*", help="only these repositories")
    args = parser.parse_args()

    names = args.repos or list(SETTINGS["repos"])
    unknown = [n for n in names if n not in SETTINGS["repos"]]
    if unknown:
        sys.exit(f"not in settings/repos.json: {', '.join(unknown)}")

    differs = False
    for name in names:
        problems = check(name, SETTINGS["repos"][name], args.apply)
        differs |= bool(problems)
        print(f"{name}: " + ("matches" if not problems else ("fixed: " if args.apply else "")
                              + "; ".join(problems)))
    sys.exit(1 if differs and not args.apply else 0)


if __name__ == "__main__":
    main()
