from __future__ import annotations

import pytest


# def test_loading_filters():
#     file = toolreg.ToolFile("src/toolreg/resources/filters.toml")
#     assert isinstance(file.filters[0], toolreg.Tool)
#     assert file.filters_dict


# def test_loading_functions():
#     file = toolreg.ToolFile("src/toolreg/resources/functions.toml")
#     assert isinstance(file.functions[0], toolreg.Tool)
#     assert file.functions_dict


# def test_loading_tests():
#     file = toolreg.ToolFile("src/toolreg/resources/tests.toml")
#     assert isinstance(file.tests[0], toolreg.Tool)
#     assert file.tests_dict


# def test_loading_config():
#     file = toolreg.ToolFile("tests/testresources/testconfig.toml")


# def test_loading_loaders():
#     env = toolreg.Environment()
#     env.load_jinja_file("tests/testresources/testconfig.toml")
#     assert env.get_template("testfile.jinja").render()


if __name__ == "__main__":
    pytest.main([__file__])
