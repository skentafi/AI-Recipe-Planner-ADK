# Allow local scripts to run (safe for CurrentUser only)
# Set-ExecutionPolicy
# This is a one‑time setup per user.
# Once you allow local scripts (RemoteSigned for CurrentUser), you don’t need to run it again every time you open VS Code.
# Think of it as unlocking the ability to run .ps1 scripts.

# Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned -Force
# This must be run each time you start a new terminal session if you want to work inside that virtual environment.
# It sets up the correct Python interpreter and pip for that session.
# VS Code can auto‑detect the .venv and activate it for you if you select the interpreter in the bottom‑right corner (or via Ctrl+Shift+P → Python: Select Interpreter).
# Activate the virtual environment
. .\.venv\Scripts\Activate.ps1

# Show Python version
python -V

# Show which interpreter is active
python -c "import sys; print(sys.executable)"

# Show pip version
python -m pip --version

