# Verified finite census ledger

No published record is claimed; prior overlap is recorded in SOURCE.md.

| Inclusive p range | K | Factors | Census SHA-256 |
|---|---:|---:|---|
| 10000–20000 | 1000 | 520 | `ec51f40e56e125c65a1107f8147af63e6633752d34dec4cb5fc3320eee77a9ce` |
| 1000–3000 | 20000 | 215 | `d0e00ccf55de45e684dcb44dfde662e959a9d4a93ef43cc09949e329bdfbe943` |
| 200001–210000 | 1000 | 312 | `28029a76b0985fc978acda2baeee8c66dcdeeb58ffdc56ae668333c2cfd6f7cd` |
| 3–100000 | 10000 | 5773 | `6de6b2ac9a1b8c3d3b36ae90dc04f4c3973dc62d920183a6f4071c3041a8b2ec` |
| 3–200 | 10000 | 46 | `4c37caf1201fe83d3c9b44d05b9c2770b9e09c9c8ef631c4d957ceb6bf182d6c` |

## Immutable certificate fingerprints

* `certificates/census_10000_20000_1000_ec51f40e56e1.json` — `d26fc0a4f468e19b798434a25b03557c847d0cc0d445d4bcf5d6607a42d57161`
* `certificates/census_1000_3000_20000_d0e00ccf55de.json` — `361e16f8a2fa0ffe06f9b2fddb27ac52da1efa5ae072358f171bd0650662cb3b`
* `certificates/census_200001_210000_1000_28029a76b098.json` — `e9760905e371156c85afc13431982d212b0ada48ea884f2bc0abbe61e4f721de`
* `certificates/census_3_100000_10000_6de6b2ac9a1b.json` — `5dada6ab06e9d33eb80536d6a5d3ca7f44530d1bf6acc85401839b49b2d9a79f`
* `certificates/census_3_200_10000_4c37caf1201f.json` — `ee6c9cc02036c34aff3e2d07f577d45bca0736d5abcfff613076724ff194815a`

## v0.4 committed Vault-S design

| Scope | Inclusive p range | K | Factors | Census SHA-256 |
|---|---|---:|---:|---|
| sealed_region_2 | 10000001–20000000 | 10000 | 250,614 | `4cd1542dbe1264ef0510b43bc165cc1a761ef24b3e42ba65118406e65bde5415` |
| extension | 20000001–30000000 | 10000 | 236,411 | `57e1388a33a8e248154ffedbc83ce229cb5fba90c35729fcad6d7783716f7c94` |
| enlarged_design | 10000001–30000000 | 10000 | 487,025 | `478aef5d3b6d09952fddef0189dc985ecec117f7ddff41c3769307ff8e9c577b` |

The union row overlaps both regional rows; do not add all three counts.

* `certificates/census_10000001_30000000_10000_478aef5d3b6d.json` — `8fdaa6ff532d1728a8b8993872a3c10f4e9664845336faa1c9def27fa595386f`
* `certificates/census_20000001_30000000_10000_57e1388a33a8.json` — `4888c4af1047272db9da21303319b643a294b4fe64fd32b6c5ac34165603bedc`
* `certificates/census_10000001_20000000_10000_4cd1542dbe12.json` — `24e1b0ff1af4a3de4caa6064fe39c5afb99852e51be957392ff9f2d7c2ca1b1b`
