from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .core import security
from .database import get_db

app = FastAPI(title="CMS Auth Service")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    # 1. Async DB lookup for user
    user = await db.get_user(form_data.username) 
    
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect credentials")
        
    token = security.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- OAuth2 Comparison Sample ---
@app.get("/auth-compare")
async def compare_auth_methods():
    return {
        "JWT_Internal": "Server signs a token. Fast, stateless, but hard to revoke.",
        "OAuth2_External": "User logs in via Google/GitHub. Secure, trusted, but relies on 3rd party."
    }