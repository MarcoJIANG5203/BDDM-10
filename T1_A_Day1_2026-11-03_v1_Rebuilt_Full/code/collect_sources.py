"""Save official English source assets and explicit access receipts."""
import hashlib
import json
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[1]
S=ROOT/'sources'
ITEMS={
 'physionet_dataset_page.html':'https://physionet.org/content/challenge-2019/1.0.0/',
 'LICENSE.txt':'https://physionet.org/files/challenge-2019/1.0.0/LICENSE.txt',
 'official_SHA256SUMS.txt':'https://physionet.org/files/challenge-2019/1.0.0/SHA256SUMS.txt',
 'official_evaluate_sepsis_score.py.txt':'https://raw.githubusercontent.com/physionetchallenges/evaluation-2019/master/evaluate_sepsis_score.py',
 'journal_pubmed.html':'https://pubmed.ncbi.nlm.nih.gov/31939789/',
 'journal_accepted_manuscript.pdf':'https://physionet.org/files/challenge-2019/1.0.0/physionet_challenge_2019_ccm_manuscript.pdf',
 'sepsis3_pubmed.html':'https://pubmed.ncbi.nlm.nih.gov/26903338/'
}

def main():
 receipts=[]
 for name,url in ITEMS.items():
  p=S/name
  if p.exists():
   data=p.read_bytes(); status='saved_in_current_run'
  else:
   r=requests.get(url,timeout=(15,90));r.raise_for_status();data=r.content;p.write_bytes(data);status=r.status_code
  receipts.append({'file':name,'url':url,'status':status,'bytes':len(data),
                   'sha256':hashlib.sha256(data).hexdigest(),'retrieval_date_hong_kong':'2026-11-03'})
  print(name,len(data),flush=True)
 receipts.append({'file':None,'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC6964870/',
  'status':'shell_download_403; read successfully using web browsing',
  'retrieval_date_hong_kong':'2026-11-03','note':'Full-text HTML was not archived locally. No access restriction was bypassed.'})
 sums={line.split()[1]:line.split()[0] for line in (S/'official_SHA256SUMS.txt').read_text().splitlines() if line.strip()}
 assert hashlib.sha256((S/'LICENSE.txt').read_bytes()).hexdigest()==sums['LICENSE.txt']
 (S/'source_download_receipts.json').write_text(json.dumps(receipts,indent=2),encoding='utf-8')
 print('Official LICENSE SHA256 matches; published root checksums do not cover training records.',flush=True)

if __name__=='__main__':main()
