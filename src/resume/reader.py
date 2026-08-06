from pathlib import Path


class ResumeReader:

    @staticmethod
    def read_resume(file_path: str = "data/resume.txt") -> str:
        path = Path(file_path)

       
        if not path.exists():
            raise FileNotFoundError(f"Resume file not found: {path.resolve()}")

        try:
            with path.open("r", encoding="utf-8") as file:
                content = file.read().strip()

        except UnicodeDecodeError:
            raise ValueError("Resume file must be UTF-8 encoded.")

        
        if not content:
            raise ValueError("Resume file is empty.")

        return content