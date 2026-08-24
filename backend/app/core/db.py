from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.core.permissions import Role
from app.models import User, UserCreate

engine = create_engine(str(settings.DATABASE_URL))

DEMO_USERS = (
    ("manager@example.com", Role.MANAGER),
    ("member@example.com", Role.MEMBER),
)


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    _create_user_if_missing(session, settings.FIRST_SUPERUSER, Role.ADMIN)

    # Demo accounts so every role can be exercised locally. Gated on FASTAPI_ENV
    # so a deployment only ever gets the admin above.
    if settings.FASTAPI_ENV == "development":
        for email, role in DEMO_USERS:
            _create_user_if_missing(session, email, role)


def _create_user_if_missing(session: Session, email: str, role: Role) -> None:
    """Seed a user, leaving an existing account with that email untouched."""
    if session.exec(select(User).where(User.email == email)).first():
        return
    crud.create_user(
        session=session,
        user_create=UserCreate(
            email=email, password=settings.FIRST_SUPERUSER_PASSWORD, role=role
        ),
    )
