from pathlib import Path
import re

import pytesseract
import pytest

from carbon.carbon import _create_carbon_url, create_code_image

CARBON_DOWNLOAD_FILE = Path("carbon.png")
ONE_LINE_SNIPPET = """print('hello world')"""
LONGER_CODE_SNIPPET = """
@pytest.fixture(scope="session")
def driver():
    driver = webdriver.Chrome()
    try:
        driver.get("http://localhost:8000/")
        yield driver
    except WebDriverException:
        raise RuntimeError("Cannot get to localhost:8000, did you start FastAPI?")
    finally:
        driver.quit()
"""


@pytest.fixture()
def python_kwargs() -> dict:
    return {
        "language": "python",
        "background": "#ABB8C3",
        "theme": "seti",
        "wt": "sharp",
        "driver_path": None,
    }


def test_create_image_for_one_liner(python_kwargs):
    create_code_image(ONE_LINE_SNIPPET, **python_kwargs)
    assert CARBON_DOWNLOAD_FILE.exists()
    image_text = pytesseract.image_to_string(CARBON_DOWNLOAD_FILE.name)
    # not sure why carbon.now.sh started to put stuff on a new line ...
    assert re.search(r"print.*hello", image_text, re.DOTALL)


def test_create_image_for_larger_snippet(python_kwargs):
    create_code_image(LONGER_CODE_SNIPPET, **python_kwargs)
    assert CARBON_DOWNLOAD_FILE.exists()
    image_text = pytesseract.image_to_string(CARBON_DOWNLOAD_FILE.name)
    # not getting full text, but at least some snippets which show it worked
    assert "fixture" in image_text
    assert "Chrome" in image_text
    assert "yield" in image_text


def test_storing_image_in_different_folder(tmpdir, python_kwargs):
    carbon_file = tmpdir / CARBON_DOWNLOAD_FILE
    assert not carbon_file.exists()
    create_code_image(ONE_LINE_SNIPPET, destination=tmpdir.strpath, **python_kwargs)
    assert carbon_file.exists()


@pytest.mark.parametrize(
    "code, kwargs, expected",
    [
        (
            "hello world",
            {
                "background": "#ABB8C3",
                "language": "python",
                "theme": "seti",
                "wt": "sharp",
            },
            "https://carbon.now.sh?l=python&code=hello+world&bg=%23ABB8C3&t=seti&wt=sharp",
        ),
        (
            "hello",
            {
                "background": "#ABB8C3",
                "language": "javascript",
                "theme": "seti",
                "wt": "sharp",
            },
            "https://carbon.now.sh?l=javascript&code=hello&bg=%23ABB8C3&t=seti&wt=sharp",
        ),
        (
            "hello",
            {
                "background": "#ABB8C3",
                "language": "python",
                "theme": "material",
                "wt": "sharp",
            },
            "https://carbon.now.sh?l=python&code=hello&bg=%23ABB8C3&t=material&wt=sharp",
        ),
        (
            "hello",
            {
                "background": "#C4F2FD",
                "language": "python",
                "theme": "seti",
                "wt": "sharp",
            },
            "https://carbon.now.sh?l=python&code=hello&bg=%23C4F2FD&t=seti&wt=sharp",
        ),
        (
            "hello",
            {
                "background": "#D7FFC5",
                "theme": "text",
                "language": "python",
                "wt": "bw",
            },
            "https://carbon.now.sh?l=python&code=hello&bg=%23D7FFC5&t=text&wt=bw",
        ),
    ],
)
def test_create_carbon_url(code, kwargs, expected):
    assert _create_carbon_url(code, **kwargs) == expected
