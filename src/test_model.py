import pytest
import random
import requests.exceptions
from model import get_models, query_model

# get_models tests


def test_get_models_sucess():
    result = get_models(model_config="https://storage.googleapis.com/sum-exported/example.config")
    assert result == {'this-model-does-not-exist': False, 'xsum': True}


def test_get_models_noserver():
    result = get_models(model_url="http://0.0.0.0/",
                        model_config="https://storage.googleapis.com/sum-exported/example.config")
    assert result == {'this-model-does-not-exist': False, 'xsum': False}


def test_get_models_badconfig():
    with pytest.raises(RuntimeError):
        get_models(model_config="https://storage.googleapis.com/sum-exported/non-existent.config")

# query_model tests


def test_query_models_sucess():
    available_models = get_models()
    model = random.choice([m for m in available_models if available_models[m]])

    result = query_model(model, "The quick brown fox jumps over the lazy dog")
    assert "outputs" in result and result["outputs"], "No outputs were given in return payload"
    assert "inputs" in result and result["inputs"], "No inputs were given in return payload"


def test_query_models_noserver():
    available_models = get_models()
    model = random.choice([m for m in available_models if available_models[m]])

    with pytest.raises(requests.exceptions.ConnectionError):
        query_model(
            model,
            "The quick brown fox jumps over the lazy dog",
            model_url="http://0.0.0.0/")


def test_query_models_badmodel():
    with pytest.raises(RuntimeError):
        query_model("this-model-does-not-exist", "The quick brown fox jumps over the lazy dog")
