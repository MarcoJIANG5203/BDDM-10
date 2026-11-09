# Source-provenance correction and unresolved license metadata

Prepared 2026-11-03, Beijing time. This dated addendum supersedes the single-license description in the original full package's `sources/SOURCE_REGISTER.md` row S5 and its attribution paragraph. It does not replace the immutable source register or license bytes and does not change clinical data version full-r1.

Observed primary-source evidence:

| Source | Observed statement |
|---|---|
| [PhysioNet dataset landing page](https://physionet.org/content/challenge-2019/1.0.0/) | Access/License field names Creative Commons Attribution 4.0 |
| [Version1.0.0 LICENSE.txt](https://physionet.org/content/challenge-2019/1.0.0/LICENSE.txt) | File begins with ODC Open Database License (ODbL) |
| Preserved `sources/LICENSE.txt` and source acquisition checksum | The full package retains the ODbL text; its bytes are covered by the verified package manifest |

Both live source observations were checked on 2026-11-03. The original register's assertion that the linked LICENSE.txt is CC BY 4.0 is inaccurate. The landing-page/file discrepancy is real; this audit does not resolve it by choosing one license or silently relabeling the dataset. A/E should retain the original notices and this correction and clarify the intended redistribution metadata before formal data publication. No external contact was sent.

The source dataset is 2019, version 1.0.0, published 2019-08-05, DOI 10.13026/v64v-d857. Its companion journal article is 2020 Feb;48(2):210–217, DOI 10.1097/CCM.0000000000004145 ([PubMed](https://pubmed.ncbi.nlm.nih.gov/31939789/)). A 2019 manuscript upload or challenge title does not change the journal issue year.

Raw-file integrity in this review means matching the supplied per-file SHA256/MD5/byte inventory and raw-ZIP hashes. It is not a newly repeated 40336-object network download, a claim that PhysioNet publishes a root checksum for every clinical object, or independent clinical adjudication. Dataset hospitals are provenance identifiers, not an available cross-admission person-linkage key.
