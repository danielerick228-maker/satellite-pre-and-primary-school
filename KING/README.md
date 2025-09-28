## Flask app

### Setup
- Create a virtual environment (PowerShell):
  - `py -m venv .venv`
  - `.venv\Scripts\Activate.ps1`
- Install dependencies:
  - `pip install -r requirements.txt`

### Run
- Option 1: `python app.py`
- Option 2: `flask --app app:create_app run --debug`

### Structure
- Templates in `templates/`
- Static assets in `static/` (`css/`, `images/`, `video/`)

