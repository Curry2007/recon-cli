import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from recon import get_title


def test_title_normal():
    assert get_title("<html><title>Hello</title></html>") == "Hello"


def test_title_with_space():
    assert get_title("<title>  空格两边  </title>") == "空格两边"


def test_title_uppercase_tag():
    assert get_title("<TITLE>大写</TITLE>") == "大写"


def test_title_missing():
    assert get_title("<html><body>no title</body></html>") == "(无 title)"


def test_title_with_attrs():
    assert get_title('<title lang="zh">带属性</title>') == "带属性"