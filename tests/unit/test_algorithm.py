import marshmallow
import pytest

class TestAlgorithm:
    def test_compute_diagnosis(self, algorithm, example_imaging, example_diagnosis):
        diagnosis = algorithm.run(example_imaging)
        assert diagnosis == example_diagnosis

    def test_fail_partial_imaging(self, algorithm, bad_imaging):
        with pytest.raises(marshmallow.ValidationError):
            algorithm.run(bad_imaging)
