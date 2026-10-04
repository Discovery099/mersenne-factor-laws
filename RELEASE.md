# P12 report release

Prepared for Chris Miki on 4 October 2026. Publication is authorized by the
user, but is not complete until the public repository, release and Zenodo
record can all be opened and checked. No DOI has been invented or reserved.

## Prepared contents

- Report: `output/pdf/P12_Chris_Miki.pdf`; editable source: `reports/P12_Chris_Miki.tex`.
- Full supplied region 1 review: `data/sources/REVIEW_VAULT_S1_L001.md`.
- Code licence: `LICENSE` (MIT); report licence: `LICENSE-REPORT.txt` (CC BY 4.0).
- Attribution and exceptions: `LICENSING.md`.
- Citation metadata: `CITATION.cff` and `.zenodo.json`, under Chris Miki's name.
- Complete tracked census outputs, certificates, predictions and run records.

After committing the reviewed artifacts, `python -m ops.package_release`
creates `output/release/<commit>/mersenne-factor-laws-reproducibility.zip`.
It contains a source ZIP, a full-history Git bundle, the report, a manifest
of checksums and restoration instructions. This command does not publish.

## Publication sequence

1. Authenticate the local GitHub CLI as the intended owner, `zoom12112`.
   Create the public `mersenne-factor-laws` repository without an initial
   README or licence commit, then push this branch with its full history.
   Do not squash or rebuild the preregistration history.
2. Record the verified public repository URL in the report, README and
   citation metadata. Commit it, regenerate the PDF and check the rendered pages.
3. Sign in to Zenodo, connect GitHub and enable this repository before the
   release. `.zenodo.json` takes precedence over `CITATION.cff` for the
   GitHub integration; the record is a report accompanied by software and data.
4. Prepare a tag and release using `release/NOTES.md`. A full-history Git
   bundle must accompany the source archive because `ops.vault_report` checks
   the original Git chronology. Verify that the archived record actually
   contains the history bundle; do not assume GitHub release attachments are
   automatically included in Zenodo's source archive. Upload the complete
   reproducibility package separately if necessary.
5. Wait for a successful Zenodo record and inspect its creator, title,
   version, licences, files and DOI. Record the actual DOI in Section 6 and
   citation metadata, rebuild and visually check the PDF. A changed PDF must
   be included in a subsequent archived version or an appropriate draft before
   publication; do not silently claim it is the unchanged PDF in an earlier
   immutable deposit.
6. Verify the public URLs, final report bytes, archive checksums, complete
   Git history and the saved-artifact audit. A replay of the censuses is not
   needed for this publication step.

## Current access status

The GitHub connector identifies `zoom12112` but exposes no repository-create,
release-create or full-history push operation. The local `gh` CLI reported
that it is not authenticated. The browser attempt to open GitHub's repository
creation page timed out; Zenodo sign-in navigation also did not complete.
Zenodo sign-in is required. These are access
dependencies, not requests for new publication permission.

## Official workflow references

- [Enable a GitHub repository in Zenodo](https://help.zenodo.org/docs/github/enable-repository/).
- [Zenodo metadata precedence](https://help.zenodo.org/docs/github/describe-software/).
- [Archive a release from GitHub](https://help.zenodo.org/docs/github/archive-software/github-upload/).
