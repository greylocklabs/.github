# Contributing

Thanks for helping. This is the default guide for Greylock Labs repositories; an app's own
CONTRIBUTING.md, where it has one, adds its build steps, scopes and code style.

## Before you start

For anything bigger than a small fix, open an issue or a
[discussion](https://github.com/greylocklabs/discussions/discussions) first, so we can agree on the
change before you spend time on it.

## Commit messages

Every repository uses [Conventional Commits](https://www.conventionalcommits.org), checked by
commitlint in CI:

```text
<type>(<scope>): <subject>
```

- Types: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`,
  `test`. Each repository lists its own scopes in its `commitlint.config` file.
- The subject is lower case, in the imperative mood, with no trailing period.
- The header is at most 72 characters, and body lines wrap at 100.

To check messages locally too, run `npm install` and `git config core.hooksPath .githooks`.

## Pull requests

- Keep each pull request to one change, and describe the problem, the change, and how you
  checked it in a few sentences.
- Pull requests merge by rebase, so each commit lands on main as written.
- CI and an automated review run on every pull request; the review is advisory.
