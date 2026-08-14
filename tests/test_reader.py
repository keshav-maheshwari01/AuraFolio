import pytest
from pathlib import Path
from src.resume.reader import ResumeReader

def t_placeholder():
    pass

def test_reader_success(tmp_path):

    d = tmp_path / "data"
    d.mkdir()
    file_path= d/"resume.txt"
    file_path.write_text("John Doe - Senior Software Engineer\nPython, Flask, AI", encoding="utf-8")
    content = ResumeReader.read_resume(str(file_path))

    assert "John Doe" in content
    assert "Python, Flask, AI" in content

def test_reader_file_not_found():
    with pytest.raises(FileNotFoundError):
        ResumeReader.read_resume("non_existent_file_path_12345.txt")

