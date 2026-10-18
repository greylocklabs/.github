# greylocklabs/.github

> Things that every @greylocklabs project shares

---

- `profile/README.md` is the organization's profile on
  [github.com/greylocklabs](https://github.com/greylocklabs).
- `CONTRIBUTING.md`, `SECURITY.md`, `SUPPORT.md`, `FUNDING.yml` and `.github/ISSUE_TEMPLATE/` are the
  defaults GitHub shows for any repository without its own copy.
- `.github/workflows/` holds reusable workflows, called by tag:

  ```yaml
  jobs:
    commitlint:
      uses: greylocklabs/.github/.github/workflows/commitlint.yml@v1
  ```

  - `commitlint.yml` checks a pull request's or push's commit messages. Input `config`, the
    commitlint config file, defaults to `commitlint.config.mjs`.
  - `markdownlint.yml` lints Markdown with the repository's own `.markdownlint-cli2.yaml`, like
    the one here, which skips files git ignores. Input `version` pins markdownlint-cli2.
  - `pages.yml` publishes a folder to GitHub Pages. Input `path` defaults to `www`; the caller
    grants `pages: write` and `id-token: write`.

- `workflow-templates/` offers a starting CI workflow when creating a workflow in a new repository.
- `settings/repos.json` and `scripts/repo-settings.py` keep every repository's merge settings,
  security features and main-branch ruleset the same:

  ```sh
  scripts/repo-settings.py          # report what differs, change nothing
  scripts/repo-settings.py --apply  # make each repository match
  ```

  The free plan has no organization rulesets, so each repository gets its own ruleset from the
  shared definition. It lets repository admins bypass it, so a release can push its commit and
  tag.

Commit messages follow the same conventional style as the apps, with a scope always required.
Run `npm install` and `git config core.hooksPath .githooks` to check them locally, and
`npm run lint:md` to lint the Markdown.
