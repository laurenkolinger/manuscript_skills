import importlib.util, os
spec = importlib.util.spec_from_file_location(
    "gen", os.path.join(os.path.dirname(__file__), "generate_master_revision_list.py"))
gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)

def test_accepts_integer():
    assert gen.normalize_version("3") == "3"

def test_accepts_decimal():
    assert gen.normalize_version("3.1") == "3.1"

def test_rejects_garbage():
    import pytest
    with pytest.raises(Exception):
        gen.normalize_version("v3-x")
