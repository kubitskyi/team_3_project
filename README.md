# team_3_project
The final project of the Python Software Engineering course from GOIT. Terms of reference for the creation of the PhotoShare application (REST API). The main functionality for the REST API is implemented on FastAPI .

temporary_tec_info:
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
