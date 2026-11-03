"""Full-delivery entry point: formal v1, not the historical candidate."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.build_a_cohort_v1 import build
if __name__=='__main__':
    build(ROOT/'sources/protocol_snapshot',ROOT/'raw',ROOT)
