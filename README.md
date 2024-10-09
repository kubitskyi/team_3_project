# PixnTalk v0.1.0

## SnakeHuntersTeam

### team_3_project
The final project of the Python Software Engineering course from GOIT.
Terms of reference for the creation of the PhotoShare application (REST API).
The main functionality for the REST API is implemented on FastAPI .

--Description of app--

##### How to run

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
pip install -r requirements.txt
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
python main.py
```
(this command may be different for different OS)

7. Swagger documentation available on address:
http://localhost:8000/docs


##### temporary_tec_info:
1. Cloudinary settings are in lifespan and can be reused.
2. get_db is in src.database.connect and can be reused.
3. auth_service.check_access - to check RBAC:
    - import to router:
    from src.services.auth import auth_service as auth_s

    - route example:
    @router.get("/route", response_model=Model)
    async def get_smth(current_user: User = Depends(auth_s.get_current_user)):
        owner_id = [id of the owner of resourse]
        check = await auth_s.check_access(current_user, owner_id)
        if check:
            return resourse

get_current_user gets user from token, check_access returns True if user is owner, moderator or admin or raises exception if not.

4. auth_service.check_admin - the same as check access? but gets access only to moders and admins.
    Usage is the same.
