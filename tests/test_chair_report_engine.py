import pytest
from app.chair_report_engine import generate_chair_advising_report

def test_generate_chair_advising_report():
    report = generate_chair_advising_report()
    
    assert 'ref_number' in report
    assert 'report_date' in report
    assert 'advisor_name' in report
    assert 'addressee_title' in report
    assert 'subject' in report
    assert 'total_advisees' in report
    assert 'total_at_risk' in report
    assert 'counts' in report
    assert 'letter_text' in report
    
    # Check groups
    assert 'strict_probation' in report
    assert 'second_probation' in report
    assert 'first_probation' in report
    
    # Verify counts match records
    assert len(report['strict_probation']) == report['counts']['strict']
    assert len(report['second_probation']) == report['counts']['second']
    assert len(report['first_probation']) == report['counts']['first']
    
    # Verify letter text formatting
    text = report['letter_text']
    assert "DHOFAR UNIVERSITY" in text
    assert "Chairperson, Department of Computer Science" in text
    assert "Dr. Nasser Tabook" in text
    assert "Article 14" in text
    assert "Article 18" in text
    assert "Article 22" in text
    assert len(text) > 500

    # Test student record integrity
    if report['strict_probation']:
        sample = report['strict_probation'][0]
        assert 'id' in sample
        assert 'name' in sample
        assert 'degree_plan' in sample
        assert 'cgpa' in sample
        assert 'gpa_deficit' in sample
        assert 'rescue_actions' in sample
        assert 'chair_intervention' in sample
        assert len(sample['rescue_actions']) > 0
