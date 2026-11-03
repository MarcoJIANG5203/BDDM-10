# Source Register and Year Verification

Checked on 2026-11-03, Hong Kong time. All listed source documents are in English. Sources were chosen for provenance and relevance; original release/definition years are retained rather than replaced with recent-looking years.

| ID | Source / year or version | What it supports | Official channel |
| --- | --- | --- | --- |
| S1 | Reyna et al., dataset, 2019, v1.0.0; published 2019-08-05 | Release identity, schema, six-hour label offset, release counts, open access, license and documented S3 acquisition channel | [PhysioNet](https://physionet.org/content/challenge-2019/1.0.0/); [DOI](https://doi.org/10.13026/v64v-d857) |
| S2 | Reyna et al., journal article, 2020; Critical Care Medicine 48(2):210–217 | Hospital identities, collection context, record truncation and challenge methodology | [PubMed](https://pubmed.ncbi.nlm.nih.gov/31939789/); [PMC full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC6964870/); [publisher DOI](https://doi.org/10.1097/CCM.0000000000004145) |
| S3 | PhysioNet Challenges, evaluation-2019 repository; retrieved 2026-11-03 | Code uses first positive label index plus six for its onset reference; supports offset interpretation, not independent clinical adjudication | [Official GitHub code](https://github.com/physionetchallenges/evaluation-2019/blob/master/evaluate_sepsis_score.py) |
| S4 | Singer et al., 2016; JAMA 315(8):801–810 | Original Sepsis-3 clinical definition, not the newly constructed fixed-landmark endpoint | [PubMed](https://pubmed.ncbi.nlm.nih.gov/26903338/); [DOI](https://doi.org/10.1001/jama.2016.0287) |
| S5 | Dataset license, CC BY 4.0 | Attribution and source-data reuse terms | [Official license](https://physionet.org/files/challenge-2019/1.0.0/LICENSE.txt) |
| S6 | Official training directories and PhysioNet Open S3 objects; snapshot 2026-11-03 | Actual acquired records, inventory sizes and ETag integrity observations | [Training directory](https://physionet.org/files/challenge-2019/1.0.0/training/); [S3 inventory endpoint](https://physionet-open.s3.amazonaws.com/?list-type=2&prefix=challenge-2019%2F1.0.0%2Ftraining%2F) |

## Year discrepancy and correction

The dataset citation is **2019**. The accompanying journal article is **2020**, February issue, volume 48, issue 2, pages 210–217. The PhysioNet page contains an older line labeling the original article 2019, while PubMed, PMC issue metadata and the publisher identify the journal issue as 2020. The article's copyright year and a repository manuscript upload in 2019 must not replace its journal publication year. The title still contains “Challenge 2019”; that is the challenge name, not the journal publication year.

The stored journal_accepted_manuscript.pdf is the official repository manuscript asset uploaded in 2019, not a claim to be the final publisher-layout PDF. The bibliography identifies the final journal reference separately. S3 object LastModified dates are infrastructure metadata, not data collection or dataset publication years. The source article describes data accumulated over the preceding decade; exact per-record calendar dates are not supplied in these files and have not been invented.

## Local evidence and access limits

Source assets and retrieval receipts are stored beside this register. The source collector obtained the PhysioNet page, license, published root checksum file, official evaluation code, PubMed records and official accepted manuscript. PMC HTML returned HTTP 403 to the shell collector; its full text was read through the browsing tool, but no local full-text HTML copy is claimed. The accepted manuscript provides an additional official English asset.

The old archive-download link on the dataset page returned HTTP 404. Acquisition instead used the official, publicly documented PhysioNet Open S3 bucket. No third-party dataset mirror, Kaggle copy, unofficial Chinese translation, credentials or patient-data upload was used.

## Attribution and transformations

Source dataset: Reyna et al. (2019), PhysioNet, version 1.0.0, DOI 10.13026/v64v-d857, CC BY 4.0. See [license text](LICENSE.txt). The raw files retain their original bytes. The local ZIP containers, filtered candidate cohort, label-derived endpoint, aggregated inputs, masks, split manifest and reports are new transformations produced on 2026-11-03. Preserve this attribution and the transformation notice when sharing.

## Reference-ready records

[1] M. Reyna, C. Josef, R. Jeter, S. Shashikumar, B. Moody, M. B. Westover, A. Sharma, S. Nemati, and G. D. Clifford, “Early Prediction of Sepsis from Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019,” PhysioNet, version 1.0.0, 2019, doi: 10.13026/v64v-d857.

[2] M. A. Reyna, C. S. Josef, R. Jeter, S. P. Shashikumar, M. B. Westover, S. Nemati, G. D. Clifford, and A. Sharma, “Early Prediction of Sepsis From Clinical Data: The PhysioNet/Computing in Cardiology Challenge 2019,” Critical Care Medicine, vol. 48, no. 2, pp. 210–217, 2020, doi: 10.1097/CCM.0000000000004145.

[3] M. Singer et al., “The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3),” JAMA, vol. 315, no. 8, pp. 801–810, 2016, doi: 10.1001/jama.2016.0287.

Full author fields are preserved in references.bib. These are data-preparation references, not a comprehensive literature review. Final venue style, submission deadline and EI indexing have not been verified in this A data-preparation task; no publication or indexing guarantee is made.
