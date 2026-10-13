from src.config.settings import PROMPTS_DIR

def build_prompt(selected: dict, subject) -> str:
    prompt = f"Treat the following subject: {subject}\n\n by sticking 100% to the following instructions:\n\n"
    for category, option in selected.items():
        with open(PROMPTS_DIR / category / f"{option}.md") as f:
            prompt += f.read() + "\n"
    return prompt
