# HAZARDNET
# HazardNet

HazardNet — crowdsourced ocean hazard reporting & analytics.

## Quick start (dev)
### Backend
cd app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

### Frontend
cd web
npm install
npm run dev

## Contributing
See CONTRIBUTING.md
