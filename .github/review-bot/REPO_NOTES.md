# Repo notes - .github

Facts the review bot cannot infer from one pass over the diff. The philosophy, the finding categories, the workflow,
the scoring and the output format all live in the bot's base prompt; this file only refines them for this repo.

## What this repo is

What every greylocklabs repository shares: the organization's profile, the default community files, the reusable
workflows, and the shared repository settings.

| Path                                                                                     | What it is                                                                   |
| ---------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `.github/workflows/{commitlint,markdownlint,pages}.yml`                                  | Reusable workflows, which the other repos call by the `v1` tag.              |
| `.github/workflows/ci.yml`, `code-review.yml`                                            | This repo's own CI and review.                                               |
| `workflow-templates/`                                                                    | The starting CI workflow GitHub offers new repositories.                     |
| `settings/repos.json`, `scripts/repo-settings.py`                                        | Each repository's merge settings, security features and main-branch ruleset. |
| `profile/README.md`                                                                      | The organization's profile page.                                             |
| `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `FUNDING.yml`, `.github/ISSUE_TEMPLATE/` | The defaults for repositories without their own copy.                        |

## What to check

- **Reusable workflows are shared.** A change to one reaches every caller once `v1` moves to it. Renaming or removing an
  input, changing a default, or needing a permission the callers do not grant is breaking, and the PR should say so.
  New inputs need defaults that keep today's behavior.
- **Permissions.** A called workflow can never hold more permission than its caller, so a new permission needs the
  callers changed too. Third-party actions are pinned to a major version or a commit.
- **Settings are applied by hand.** `scripts/repo-settings.py --apply` changes every repository; the PR only changes
  what it would apply. A change that loosens a ruleset or a security feature is a finding unless the PR says why.
- **Community files** are what GitHub shows on repositories without their own, so they name no single app.
