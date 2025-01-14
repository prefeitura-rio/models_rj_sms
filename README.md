# models_rj_sms

- A API to serve the models of NEDTec/SMS.

## Run the project

#### 1. Create .env file

- Use the .env.example file as a reference and create your own .env file.

#### 2. Run the project

- Use Docker Compose:

```bash
docker compose up -d
```

- Use FastAPI:

```bash
uvicorn app.main:app --reload
```

