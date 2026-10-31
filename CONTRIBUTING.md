# Contributing to RogueGuard

Thanks for your interest in improving RogueGuard.

## Development setup

```bash
git clone https://github.com/Ayush-Iyer1611/RogueGuard.git
cd RogueGuard
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Before submitting changes

1. Keep the application feature scope and simulation boundaries explicit.
2. Do not add real credentials, personal data, or production endpoints.
3. Add or update tests for behavioural changes.
4. Run the test suite:

   ```bash
   python -m unittest discover -s tests -v
   ```

5. Update documentation when behaviour, assumptions, or limitations change.
6. Use clear, focused commit messages.

## Pull request expectations

A pull request should explain the problem, proposed change, test evidence, and any security implications. Clearly distinguish implemented behaviour from proposed future work.

## Suggested commit style

- `feat: add ...`
- `fix: prevent ...`
- `test: cover ...`
- `docs: clarify ...`
- `ci: configure ...`
