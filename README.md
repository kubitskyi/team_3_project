# PixnTalk v0.1.0

## SnakeHuntersTeam

### team_3_project
The final project of the Python Software Engineering course from GOIT.
Terms of reference for the creation of the PhotoShare application (REST API).
The main functionality for the REST API is implemented on FastAPI .

--Description of app--

##### How to run locally

1. Start virtual environment:
```
python -m venv .venv
```
(this command may be different for different OS)
```
source .venv/bin/activate
```
(this command may be different for different OS)

2. Instal dependencies:
```
poetry install
```

3. Create file .env and write credentials as it shown in .env.exam

4. In other terminal start docker compose containers:
```
docker compose up
```

5. Make alembic migrations:
```
alembic upgrade heads
```

6. Run application:
```
python start.py
```
(this command may be different for different OS)

7. Swagger documentation available on address:
http://localhost:8000/docs


##### To run on Koyeb:

Procfile is included, just add variables while configuring server.
Redis and PostgreSQL must be running separatelly.
