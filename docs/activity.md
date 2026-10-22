# Profile activity and visual assets

## What the cards measure

The contribution card shows the current calendar year through the UTC date printed on the card. Counts come from the unauthenticated, public GitHub contribution calendar for AugereAbove. The generator reads the numeric tooltip for every day, not a color level. Missing days or tooltips cause a failure instead of invented zeroes. Future dates are excluded.

The narrow-screen version aggregates those same daily counts by month. It replaces the heatmap through a picture source; it is not a second dataset.

The repository overview counts public repositories owned by AugereAbove, excluding forks. Stars and forks are the totals received by those repositories. Archived repositories and the profile repository are included. No private repository names, metrics, or authenticated-only activity are published.

The language chart counts each included repository once using GitHub's primary language field. Unclassified means GitHub reports no primary language, often for repositories without source code. This is not a measurement of code volume, proficiency, or time spent using a language.

The contribution calendar follows GitHub's contribution rules. It is not a complete commit count or a measure of engineering quality. Profile maintenance commits may count when GitHub includes them. Zero stars and forks remain zero; no counters are estimated or padded.

`assets/activity/snapshot.json` stores the public aggregate inputs and daily counts used for the SVGs. GitHub may take time to update public activity after a commit. The displayed date records the observation date, not a claim of real-time updates.

## Automation

`.github/workflows/profile-summary-cards.yml` runs daily at 07:23 UTC, accepts manual dispatch, and runs when its generator, tests, or workflow change on main. It tests the generator, fetches public data, generates four SVG variants and the snapshot, and commits changed activity files only.

The workflow uses GitHub's repository token, not a personal access token. The repository list is explicitly filtered to public, owned, nonfork repositories. Calendar requests never send authorization headers. Only the refresh job requests `contents: write`, which is needed to commit the generated files. There are no pull request triggers, approval permissions, or unrelated repository writes.

The sole external action is the official `actions/checkout` release v7.0.1, pinned to verified commit `3d3c42e5aac5ba805825da76410c181273ba90b1`. The generator uses Python's standard library and the GitHub CLI supplied by the hosted runner; no third-party statistics action or service runs with the token. Checkout does not persist credentials. Push authentication is configured only for the final push step.

Both author and committer are configured as AugereAbove with the account's GitHub noreply email. Automatic commits use `Refresh public GitHub activity`. Pushes use normal fast-forward behavior. If another update wins a race, the push fails rather than overwriting it; rerun the workflow after reviewing the failure.

To run locally with an authenticated GitHub CLI:

```bash
python -m unittest discover -s tests -v
python scripts/build_activity.py --user AugereAbove
```

If GitHub changes its public calendar markup or an API rate limit is reached, the workflow fails and preserves previously committed cards. Check the workflow logs and update the parser before rerunning. GitHub can disable scheduled workflows after extended repository inactivity; a manual run or re-enabling the workflow may be required.

## Sources and attribution

- Public contribution calendar: https://github.com/users/AugereAbove/contributions
- Public repository metadata: https://api.github.com/users/AugereAbove/repos
- GitHub's contribution rules: https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-contributions/missing-contributions
- Colorful technology icons: [Skill Icons](https://skillicons.dev), by [tandpfun/skill-icons](https://github.com/tandpfun/skill-icons), used under its MIT license. A copy of the license is stored beside the vendored SVGs in `assets/toolbox/LICENSE`.

- pytest and Playwright symbols: [Devicon](https://github.com/devicons/devicon), used under its MIT license, with a local tile background for visual consistency. The license is stored in `assets/toolbox/DEVICON-LICENSE`.

The navigation badges, activity cards, and their generator are maintained in this repository. The visual assets contain no scripts, tracking pixels, or external fonts. README images are served from this repository rather than depending on a live statistics endpoint.
