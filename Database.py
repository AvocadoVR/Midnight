import datetime
from enum import Enum
from typing import List, Optional
import aiomysql

from sqlmodel import SQLModel, Field, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import delete, Column, BIGINT, BigInteger

# ---------- Async Engine ----------
DATABASE_URL = "mysql+aiomysql://u185315_XCxGOyxbwo:HWnQGDDK5HZLpsb20=g7dx.n@db-dtx-03.sparkedhost.us:3306/s185315_DatabaseV2"

async_engine = create_async_engine(DATABASE_URL, echo=False)


# ---------- Models ----------

class VerifiedUser(SQLModel, table=True):
    discordId: int = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True)
    )
    vrchatId: str
    change_account: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.utcnow() + datetime.timedelta(days=90)
    )


class SyncedEvent(SQLModel, table=True):
    discordEventId: int = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True)
    )
    vrchatEventId: int


class Invite(SQLModel, table=True):
    discordId: int = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True)
    )
    vrchatId: str
    requestedAt: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class PendingVerification(SQLModel, table=True):
    discordId: int = Field(
        default=None,
        sa_column=Column(BigInteger, primary_key=True)
    )
    vrchatId: str
    code: str
    expires: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    )


# ---------- Setup ----------
async def setup_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    print("Database Setup Complete")


# ---------- Create ----------
async def create_invite(discordId: int, vrchatId: str):
    invite = Invite(discordId=discordId, vrchatId=vrchatId)
    async with AsyncSession(async_engine) as session:
        session.add(invite)
        await session.commit()
        await session.refresh(invite)


async def add_verified_user(discordId: int, vrchatId: str):
    verified_user = VerifiedUser(discordId=discordId, vrchatId=vrchatId)
    async with AsyncSession(async_engine) as session:
        session.add(verified_user)
        await session.commit()
        await session.refresh(verified_user)


async def create_pending_verification(discordId: int, vrchatId: str, code: str):
    pending = PendingVerification(discordId=discordId, vrchatId=vrchatId, code=code)
    async with AsyncSession(async_engine) as session:
        session.add(pending)
        await session.commit()
        await session.refresh(pending)

async def add_synced_event(id: int):
    event = SyncedEvent(eventId=id)
    async with AsyncSession(async_engine) as session:
        session.add(event)
        await session.commit()
        await session.refresh(event)


# ---------- Get ----------
async def get_invite(discordId: int) -> Optional[Invite]:
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(Invite).where(Invite.discordId == discordId))
        return result.scalars().first()


async def get_invite_list() -> List[Invite]:
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(Invite).order_by(Invite.id))
        return result.scalars().all()


async def get_verified_user(discordId: int) -> Optional[VerifiedUser]:
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(VerifiedUser).where(VerifiedUser.discordId == discordId))
        return result.scalars().first()


async def get_pending_verification(discordId: int) -> Optional[PendingVerification]:
    async with AsyncSession(async_engine) as session:
        result = await session.execute(
            select(PendingVerification).where(PendingVerification.discordId == discordId)
        )
        return result.scalars().first()

async def get_scheduled_events() -> List[SyncedEvent]:
    async with AsyncSession(async_engine) as session:
        result = await session.execute(select(SyncedEvent.eventId))
        return result.scalars().all()

# ---------- Remove ----------
async def remove_invite(discordId: int):
    async with AsyncSession(async_engine) as session:
        await session.execute(delete(Invite).where(Invite.discordId == discordId))
        await session.commit()


async def remove_verified_user(discordId: int):
    async with AsyncSession(async_engine) as session:
        await session.execute(delete(VerifiedUser).where(VerifiedUser.discordId == discordId))
        await session.commit()


async def remove_pending_verification(discordId: int):
    async with AsyncSession(async_engine) as session:
        await session.execute(delete(PendingVerification).where(PendingVerification.discordId == discordId))
        await session.commit()


async def remove_expired_verifications():
    async with AsyncSession(async_engine) as session:
        await session.execute(
            delete(PendingVerification).where(PendingVerification.expires < datetime.datetime.utcnow())
        )
        await session.commit()
    print("Removed Expired Verifications")

async def remove_synced_event(discordEventId: int, vrchatEventId: int):
    async with AsyncSession(async_engine) as session:
        await session.execute(
            delete(SyncedEvent).where().or_(
                SyncedEvent.discordEventId == discordEventId,
                SyncedEvent.vrchatEventId == vrchatEventId,
            )
        )
        await session.commit()