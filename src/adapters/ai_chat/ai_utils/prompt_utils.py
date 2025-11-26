from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(relative_path: str) -> str:
    """
    Load a prompt by relative path inside the prompts directory,
    e.g. 'system/response_system_prompt.txt' or 'user/response_prompt.txt'.
    """
    path = PROMPT_DIR / relative_path
    if not path.exists():
        raise FileNotFoundError(f"Prompt file {path} not found")
    return path.read_text(encoding="utf-8")


if __name__ == "__main__":
    print(load_prompt("system/response_system_prompt.txt"))
    print(load_prompt("user/response_prompt.txt"))
