import marshmallow
import pytest

class TestAlgorithm:
    def test_prepare_for_matlab_no_edit(self, algorithm):
        expected_data = data = {'id': 'imaging', 'type': 'MRI'}
        filtered_data = algorithm._prepare_for_matlab(data) # pylint: disable=protected-access

        assert filtered_data == expected_data

    def test_prepare_for_matlab_edit(self, algorithm):
        data = {'_id': 'imaging', 'type': 'MRI'}
        expected_data = {'id': 'imaging', 'type': 'MRI'}
        filtered_data = algorithm._prepare_for_matlab(data) # pylint: disable=protected-access

        assert filtered_data == expected_data

    def test_prepare_for_matlab_fail_on_conflict(self, algorithm):
        data = {'_id': 'imaging', 'id': 'imaging', 'type': 'MRI'}
        with pytest.raises(Exception) as err:
            algorithm._prepare_for_matlab(data) # pylint: disable=protected-access

        assert str(err.value) == 'Conflicting imaging fields with: _id'

    def test_compute_diagnosis(self, algorithm, example_imaging, example_diagnosis):
        diagnosis = algorithm.run(example_imaging)
        assert diagnosis == example_diagnosis

    def test_fail_partial_imaging(self, algorithm, bad_imaging):
        with pytest.raises(marshmallow.ValidationError):
            algorithm.run(bad_imaging)
