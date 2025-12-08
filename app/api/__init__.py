"""
Re-export API routers so `from app.api import auth, users, ...` works.

This maps directly to the modules in `app.api.*`.
"""

from app.api.auth import router as auth  # noqa: F401
from app.api.users import router as users  # noqa: F401
from app.api.plants import router as plants  # noqa: F401
from app.api.orders import router as orders  # noqa: F401
from app.api.delivery import router as delivery  # noqa: F401
from app.api.admin import router as admin  # noqa: F401
from app.api.seller import router as seller  # noqa: F401
from app.api.cart import router as cart  # noqa: F401
from app.api.payments import router as payments  # noqa: F401
from app.api.reviews import router as reviews  # noqa: F401
from app.api.categories import router as categories  # noqa: F401
from app.api.notifications import router as notifications  # noqa: F401
from app.api.stores import router as stores  # noqa: F401
