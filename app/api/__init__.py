# Route modules re-exported from app.api.routes to maintain stable imports
from app.api.routes.auth import router as auth  # noqa: F401
from app.api.routes.users import router as users  # noqa: F401
from app.api.routes.plants import router as plants  # noqa: F401
from app.api.routes.orders import router as orders  # noqa: F401
from app.api.routes.delivery import router as delivery  # noqa: F401
from app.api.routes.admin import router as admin  # noqa: F401
from app.api.routes.seller import router as seller  # noqa: F401
from app.api.routes.cart import router as cart  # noqa: F401
from app.api.routes.payments import router as payments  # noqa: F401
from app.api.routes.reviews import router as reviews  # noqa: F401
from app.api.routes.categories import router as categories  # noqa: F401
from app.api.routes.notifications import router as notifications  # noqa: F401
