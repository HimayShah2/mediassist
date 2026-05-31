import pytest
from scoring.clinical_tools import (
    calculate_phq9,
    calculate_gcs,
    calculate_apgar,
    calculate_sofa
)

def test_calculate_phq9():
    result = calculate_phq9([3, 3, 3, 3, 3, 3, 2, 0, 0])
    assert result["score"] == 20
    assert result["interpretation"] == "Severe depression"
    
    result = calculate_phq9([0] * 9)
    assert result["score"] == 0
    assert result["interpretation"] == "Minimal depression"
    
    with pytest.raises(ValueError):
        calculate_phq9([0] * 8)
        
    with pytest.raises(ValueError):
        calculate_phq9([4] * 9)

def test_calculate_gcs():
    result = calculate_gcs(4, 5, 6)
    assert result["score"] == 15
    assert result["interpretation"] == "Mild brain injury"
    
    result = calculate_gcs(1, 1, 1)
    assert result["score"] == 3
    assert result["interpretation"] == "Severe brain injury"
    
    with pytest.raises(ValueError):
        calculate_gcs(5, 5, 6)

def test_calculate_apgar():
    result = calculate_apgar(2, 2, 2, 2, 2)
    assert result["score"] == 10
    assert result["interpretation"] == "Normal"
    
    result = calculate_apgar(0, 1, 0, 1, 1)
    assert result["score"] == 3
    assert result["interpretation"] == "Critically low"
    
    with pytest.raises(ValueError):
        calculate_apgar(3, 2, 2, 2, 2)

def test_calculate_sofa():
    result = calculate_sofa(4, 4, 4, 4, 4, 4)
    assert result["score"] == 24
    assert result["interpretation"] == "Extremely high risk"
    
    result = calculate_sofa(0, 1, 0, 1, 0, 1)
    assert result["score"] == 3
    assert result["interpretation"] == "Low risk"
    
    with pytest.raises(ValueError):
        calculate_sofa(5, 0, 0, 0, 0, 0)
