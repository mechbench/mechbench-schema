from typing import get_args

import pytest

from mechbench_schema import EndpointProvider, EndpointRef


@pytest.mark.parametrize("provider", get_args(EndpointProvider))
def test_each_provider_validates_as_an_endpoint_ref(provider):
    ref = EndpointRef.model_validate({"provider": provider, "model": "m"})
    assert ref.provider == provider


def test_deepseek_is_a_provider():
    assert "deepseek" in get_args(EndpointProvider)


def test_an_unknown_provider_is_refused():
    with pytest.raises(ValueError):
        EndpointRef.model_validate({"provider": "nobody", "model": "m"})
