from datetime import datetime, timedelta

from sqlalchemy import create_engine, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column, func


engine = create_engine("sqlite://", echo=True)

Base = declarative_base()


class TimedBaseModel(Base):
    __abstract__ = True

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def as_dict(self) -> dict:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Item(TimedBaseModel):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    number = Column(Integer)

    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    order = relationship(
        "Order",
        backref=backref(
            "items",
            cascade="all, delete-orphan",
            passive_deletes=True,
            order_by="Item.updated_at.desc()",
        ),
    )

    def __repr__(self):
        return f"Item(n={self.number})"


class Order(TimedBaseModel):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"Order(name={self.name})"


Base.metadata.create_all(engine)


now = datetime.now()

order = Order(name="Hello World!")
item_1 = Item(number=5, order=order, updated_at=now)
item_2 = Item(number=1, order=order, updated_at=now - timedelta(minutes=1))
item_3 = Item(number=10, order=order, updated_at=now + timedelta(minutes=1))

Session = sessionmaker(bind=engine)
session = Session()

session.add(order)
session.add(item_1)
session.add(item_2)
session.add(item_3)
session.commit()

query = session.query(Order)
instance = query.first()

assert [i.number for i in order.items] == [10, 5, 1]  # desc
# assert [i.number for i in order.items] == [1, 5, 10]

for i in order.items:
    print(i.updated_at)
