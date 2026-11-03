"""Synthetic edge cases: these are tests, never research observations."""
import unittest
from prepare_day1 import HEADER, summarize_record

def example(first=None, n=30, age=50, future=999, start=1):
    lines=['|'.join(HEADER)]
    for h in range(start,start+n):
        v=['NaN']*41
        v[0]=str(70 if h<=12 else future)
        v[34]=str(age);v[35]='1';v[38]='-5';v[39]=str(h)
        v[40]=str(int(first is not None and h>=first))
        lines.append('|'.join(v))
    return '\n'.join(lines)

class ClinicalBoundaries(unittest.TestCase):
    def run_record(self,**kw):return summarize_record(example(**kw),'A','synthetic.psv')
    def test_onset_hour13_included_even_when_label_positive_before_landmark(self):
        q,p=self.run_record(first=7);self.assertEqual(q['outcome_12_24'],1);self.assertEqual(q['onset_proxy_hour'],13)
    def test_onset_hour24_is_positive(self):
        q,p=self.run_record(first=18);self.assertEqual(q['outcome_12_24'],1)
    def test_onset_hour25_is_negative(self):
        q,p=self.run_record(first=19);self.assertEqual(q['outcome_12_24'],0)
    def test_onset_hour12_excluded(self):
        q,p=self.run_record(first=6);self.assertEqual(q['eligibility_reason'],'onset_at_or_before_12h')
    def test_first_row_positive_is_left_censored(self):
        q,p=self.run_record(first=1);self.assertEqual(q['eligibility_reason'],'left_censored_onset');self.assertEqual(q['onset_proxy_hour'],'')
    def test_nonseptic_is_negative(self):
        q,p=self.run_record();self.assertEqual(q['outcome_12_24'],0)
    def test_followup_requirement_applies_to_both_classes(self):
        for first in [None,7]:
            q,p=self.run_record(first=first,n=23);self.assertEqual(q['eligibility_reason'],'insufficient_followup_24h')
    def test_future_predictors_cannot_change_X(self):
        q,a=self.run_record(first=18,future=999);q,b=self.run_record(first=18,future=-999)
        self.assertEqual(a,b);self.assertEqual(a['x']['HR'],70)
    def test_late_start_retained_with_leading_missing_hours(self):
        q,p=self.run_record(start=2);self.assertEqual(q['eligibility_reason'],'included');self.assertEqual(p['counts']['HR'],11)
    def test_actual_ICULOS_used_for_onset(self):
        q,p=self.run_record(start=5,first=7);self.assertEqual(q['onset_proxy_hour'],13);self.assertEqual(q['outcome_12_24'],1)
    def test_last_hour_not_row_count_defines_followup(self):
        q,p=self.run_record(start=5,n=20);self.assertEqual(q['eligibility_reason'],'included');self.assertEqual(q['last_observed_hour'],24)
    def test_gap_in_time_axis_excluded(self):
        text=example();lines=text.splitlines();v=lines[4].split('|');v[39]='5';lines[4]='|'.join(v)
        q,p=summarize_record('\n'.join(lines),'A','synthetic.psv');self.assertEqual(q['eligibility_reason'],'invalid_time_axis')
    def test_nonadult_excluded(self):
        q,p=self.run_record(age=17);self.assertEqual(q['eligibility_reason'],'nonadult_or_age_unknown')
    def test_missingness_retained(self):
        q,p=self.run_record();self.assertEqual(p['x']['Lactate'],'');self.assertEqual(p['mask']['Lactate'],1);self.assertEqual(p['counts']['Lactate'],0)
    def test_nonmonotone_labels_excluded(self):
        text=example(first=7);lines=text.splitlines();last=lines[-1].split('|');last[-1]='0';lines[-1]='|'.join(last)
        q,p=summarize_record('\n'.join(lines),'A','synthetic.psv');self.assertEqual(q['eligibility_reason'],'invalid_label_sequence')

if __name__=='__main__':unittest.main(verbosity=2)
