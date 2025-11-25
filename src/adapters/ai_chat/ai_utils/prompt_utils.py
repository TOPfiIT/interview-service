from pathlib import Path

PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"

def load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Prompt file {path} not found")
    return path.read_text(encoding="utf-8")

if __name__ == "__main__":
    print(load_prompt("response_system_prompt.txt"))
    print(load_prompt("response_prompt.txt"))