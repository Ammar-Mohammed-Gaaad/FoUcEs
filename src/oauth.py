"""
OAuth Social Login — Google, GitHub, Facebook, LinkedIn
Flow:
  1. GET /api/auth/login/{provider}    → redirect user to provider consent page
  2. GET /api/auth/callback/{provider} → exchange code for token, get profile,
                                         upsert User, issue JWT, redirect to frontend
"""
import httpx
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode
from sqlalchemy.orm import Session

from database import get_db
from models import User, LearningProfile
from utils import create_access_token
from config import settings

router = APIRouter(prefix="/api/auth", tags=["oauth"])

# ──────────────────────────────────────────────────────────────
# Provider configuration table
# ──────────────────────────────────────────────────────────────
def _cfg(provider: str):
    """Return (client_id, client_secret, auth_url, token_url, scope, userinfo_url)."""
    base = settings.base_url
    redirect = f"{base}/api/auth/callback/{provider}"

    if provider == "google":
        return {
            "client_id":     settings.google_client_id,
            "client_secret": settings.google_client_secret,
            "redirect_uri":  redirect,
            "auth_url":      "https://accounts.google.com/o/oauth2/v2/auth",
            "token_url":     "https://oauth2.googleapis.com/token",
            "scope":         "openid email profile",
            "userinfo_url":  "https://www.googleapis.com/oauth2/v3/userinfo",
        }
    if provider == "github":
        return {
            "client_id":     settings.github_client_id,
            "client_secret": settings.github_client_secret,
            "redirect_uri":  redirect,
            "auth_url":      "https://github.com/login/oauth/authorize",
            "token_url":     "https://github.com/login/oauth/access_token",
            "scope":         "read:user user:email",
            "userinfo_url":  "https://api.github.com/user",
        }
    if provider == "facebook":
        return {
            "client_id":     settings.facebook_client_id,
            "client_secret": settings.facebook_client_secret,
            "redirect_uri":  redirect,
            "auth_url":      "https://www.facebook.com/v18.0/dialog/oauth",
            "token_url":     "https://graph.facebook.com/v18.0/oauth/access_token",
            "scope":         "email,public_profile",
            "userinfo_url":  "https://graph.facebook.com/me?fields=id,name,email",
        }
    if provider == "linkedin":
        return {
            "client_id":     settings.linkedin_client_id,
            "client_secret": settings.linkedin_client_secret,
            "redirect_uri":  redirect,
            "auth_url":      "https://www.linkedin.com/oauth/v2/authorization",
            "token_url":     "https://www.linkedin.com/oauth/v2/accessToken",
            "scope":         "openid profile email",
            "userinfo_url":  "https://api.linkedin.com/v2/userinfo",
        }
    return None


def _frontend_error(msg: str) -> RedirectResponse:
    """Redirect to login page with an error message in the URL."""
    params = urlencode({"oauth_error": msg})
    return RedirectResponse(url=f"/login.html?{params}")


# ──────────────────────────────────────────────────────────────
# Step 1 — Redirect user to provider
# ──────────────────────────────────────────────────────────────
@router.get("/login/{provider}")
async def oauth_login(provider: str):
    cfg = _cfg(provider)
    if cfg is None:
        return _frontend_error(f"مزود غير مدعوم: {provider}")

    if not cfg["client_id"] or not cfg["client_secret"]:
        return _frontend_error(
            f"تسجيل الدخول عبر {provider.capitalize()} غير مفعّل بعد. "
            f"أضف {provider.upper()}_CLIENT_ID في ملف .env"
        )

    params = {
        "client_id":     cfg["client_id"],
        "redirect_uri":  cfg["redirect_uri"],
        "scope":         cfg["scope"],
        "response_type": "code",
    }
    # Google requires access_type=offline for refresh tokens (optional but good practice)
    if provider == "google":
        params["access_type"] = "offline"
        params["prompt"] = "select_account"

    url = cfg["auth_url"] + "?" + urlencode(params)
    return RedirectResponse(url=url)


# ──────────────────────────────────────────────────────────────
# Step 2 — Provider redirects back here with ?code=
# ──────────────────────────────────────────────────────────────
@router.get("/callback/{provider}")
async def oauth_callback(provider: str, request: Request, db: Session = Depends(get_db)):
    cfg = _cfg(provider)
    if cfg is None:
        return _frontend_error(f"مزود غير مدعوم: {provider}")

    code = request.query_params.get("code")
    error = request.query_params.get("error")

    if error:
        return _frontend_error(f"رفض المستخدم الإذن من {provider.capitalize()}")
    if not code:
        return _frontend_error("لم يتم استلام كود التحقق من المزود")

    # ── Exchange code for access token ─────────────────────────
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_params = {
                "client_id":     cfg["client_id"],
                "client_secret": cfg["client_secret"],
                "code":          code,
                "redirect_uri":  cfg["redirect_uri"],
                "grant_type":    "authorization_code",
            }
            headers = {"Accept": "application/json"}
            token_resp = await client.post(cfg["token_url"], data=token_params, headers=headers)
            token_data = token_resp.json()

        access_token = token_data.get("access_token")
        if not access_token:
            return _frontend_error("فشل في الحصول على رمز الوصول من المزود")

        # ── Fetch user profile ──────────────────────────────────
        async with httpx.AsyncClient(timeout=15) as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            if provider == "github":
                headers["Accept"] = "application/vnd.github.v3+json"
            profile_resp = await client.get(cfg["userinfo_url"], headers=headers)
            profile = profile_resp.json()

        # ── Normalise profile across providers ─────────────────
        if provider == "google":
            oauth_id = profile.get("sub")
            email    = profile.get("email", "")
            name     = profile.get("name", email.split("@")[0])

        elif provider == "github":
            oauth_id = str(profile.get("id", ""))
            email    = profile.get("email") or ""
            name     = profile.get("name") or profile.get("login", "GitHub User")
            # GitHub may return email=None → fetch primary email separately
            if not email:
                async with httpx.AsyncClient(timeout=10) as client:
                    emails_resp = await client.get(
                        "https://api.github.com/user/emails",
                        headers={"Authorization": f"Bearer {access_token}",
                                 "Accept": "application/vnd.github.v3+json"}
                    )
                    emails = emails_resp.json()
                    for e in emails:
                        if isinstance(e, dict) and e.get("primary") and e.get("verified"):
                            email = e["email"]
                            break

        elif provider == "facebook":
            oauth_id = str(profile.get("id", ""))
            email    = profile.get("email", "")
            name     = profile.get("name", "Facebook User")

        elif provider == "linkedin":
            oauth_id = profile.get("sub") or str(profile.get("id", ""))
            email    = profile.get("email", "")
            name     = profile.get("name", "") or \
                       f"{profile.get('given_name','')} {profile.get('family_name','')}".strip()

        else:
            return _frontend_error("مزود غير معروف")

        if not oauth_id:
            return _frontend_error("لم يتم استلام معرّف المستخدم من المزود")

        # If email is empty → generate a placeholder (GitHub without public email)
        if not email:
            email = f"{provider}_{oauth_id}@oauth.fakarni.app"

    except Exception as e:
        print(f"OAuth error [{provider}]: {e}")
        return _frontend_error("حدث خطأ أثناء التحقق، حاول مرة أخرى")

    # ── Find or create user ────────────────────────────────────
    user = db.query(User).filter(
        User.oauth_provider == provider,
        User.oauth_id == oauth_id
    ).first()

    if not user:
        # Maybe the email already exists from a regular signup
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Link existing account to this OAuth provider
            user.oauth_provider = provider
            user.oauth_id       = oauth_id
            db.commit()
        else:
            # Brand-new user
            user = User(
                email          = email,
                full_name      = name,
                hashed_password= None,
                oauth_provider = provider,
                oauth_id       = oauth_id,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            # Create learning profile
            learning_profile = LearningProfile(user_id=user.id)
            db.add(learning_profile)
            db.commit()

    db.refresh(user)

    # ── Issue JWT ──────────────────────────────────────────────
    jwt_token = create_access_token(data={"sub": str(user.id)})

    # ── Redirect to frontend with token ───────────────────────
    params = urlencode({
        "token":   jwt_token,
        "name":    user.full_name or name,
        "email":   user.email,
        "user_id": user.id,
    })
    # New OAuth users → learning interview; existing → home
    is_new = not user.learning_profile or not user.learning_profile.completed_interview
    dest = "/learning-interview.html" if is_new else "/home.html"
    return RedirectResponse(url=f"/login.html?{params}&dest={dest}")
