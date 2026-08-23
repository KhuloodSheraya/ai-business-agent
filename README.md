# AI Business Agent

Complete local AI business agent demo.

## Stack
Python · FastAPI · Ollama/Qwen · Tool Calling · HTML/CSS/JavaScript

## Architecture
User → Browser UI → FastAPI → Ollama → Tool Selection → Business Tool → Result → UI

## Ports
- Backend: http://127.0.0.1:8001
- Frontend: http://127.0.0.1:5500

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

Make sure Ollama is running with a model such as:

```powershell
ollama run qwen3:8b
```

Start backend:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Start frontend in another terminal:

```powershell
cd frontend
python -m http.server 5500
```

Then open:

http://127.0.0.1:5500

## Example prompts
- Show me all invoices
- Show overdue invoices
- Look up invoice INV-1001
- What is the total of overdue invoices?
- اعرض كل الفواتير
- اعرض الفواتير المتأخرة
- اعرض تفاصيل الفاتورة INV-1001
- كم مجموع الفواتير المتأخرة؟
