# DextroSage Backend API Documentation

A simple, professional API documentation for web and mobile frontend developers (React, Angular, Vue, Flutter, Android, iOS) integrating with the **DextroSage FastAPI Backend**.

---

# Base URL

### create venv
```bash
python -m venv .dextro
```
# Start server

### create venv
```bash
fastapi dev main.py --port 3000
```


### Activate it
```bash
http://localhost:3000
```

### Run requirements.txt for modules
```bash
pip install -r requirements.txt
```


### Local Development
```bash
http://localhost:3000
```

### Interactive API Documentation (Swagger UI)
```bash
http://localhost:3000/docs
```

### Celery start code
```bash
celery -A celery_worker.celery_app:celery_app worker --pool=solo --loglevel=info
```

