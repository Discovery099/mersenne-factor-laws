# P12 public release

Author: Chris Miki. Published 4 October 2026.

- Repository: https://github.com/Discovery099/mersenne-factor-laws
- Release: https://github.com/Discovery099/mersenne-factor-laws/releases/tag/p12-report-2026-10-04
- Version DOI: https://doi.org/10.5281/zenodo.23129695
- All-versions DOI: https://doi.org/10.5281/zenodo.23129694

The release tag identifies commit `b09ef3038253d5b6d1dc8096dab3c959bb560106`.
Zenodo's GitHub integration archived that exact source snapshot. The original
tag is retained. A subsequent citation update inserts the assigned DOI into
the report and citation metadata; no research model, prediction, census or
score changes. The separate PDF and complete reproducibility package identify
that citation update through the package manifest and Git history. The
original GitHub source ZIP remains identifiable as the earlier snapshot.

## Contents and licences

The release contains the report, editable LaTeX, code, frozen predictions,
complete census outputs, certificates and external operator reviews. Original
code is MIT-licensed; the report and its LaTeX source are CC BY 4.0. Vendored
GNU mini-gmp and third-party source material keep their own terms. See
`LICENSING.md`, `LICENSE` and `LICENSE-REPORT.txt`.

The region 1 review in `data/sources/REVIEW_VAULT_S1_L001.md` is a transcription
of the user-supplied text, fingerprinted in `SOURCE.md`. It is attributed
external evidence. Region 1 was not rerun for publication.

## Reproducibility package

After committing reviewed artifacts, `python -m ops.package_release` creates
`output/release/<commit>/mersenne-factor-laws-reproducibility.zip`, containing
a full-history Git bundle, source ZIP, report, SHA-256 manifest and restoration
instructions. This local packaging command does not publish anything.

GitHub's automatic source ZIP omits Git history. Use a full clone or restore
the included bundle before running `python -m ops.vault_report`. This audit
checks the saved experiment and frozen scores without enumerating factors.
Full replay commands in `README.md` are separate and substantially more work.

## Publication checks

GitHub CLI publication used the user's `Discovery099` account. Zenodo's
repository switch was enabled before the release. The public Zenodo record
was checked for the title, Chris Miki as creator, report type, open access,
CC BY 4.0 and the exact release source snapshot.

The DOI update and complete history package are supplementary files to the
original archived snapshot. Verify the final deposit's file list and compare
checksums with the package manifest; a DOI alone does not prove an attachment
has been deposited. Local verification records accompany the prepared package.

Publication now supplies a public timestamp for this release. It does not
retroactively supply the missing external pre-run prediction receipt for
the region 2 experiment.

## Official workflow references

- https://help.zenodo.org/docs/github/enable-repository/
- https://help.zenodo.org/docs/github/archive-software/github-upload/
- https://help.zenodo.org/docs/deposit/manage-files/
