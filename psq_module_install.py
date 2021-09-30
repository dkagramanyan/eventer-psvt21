
from create import engine
from sqlalchemy.orm import sessionmaker, Session


def session() -> Session:
    """The function of getting a connection to the db.

    :return: connected session to db
    :rtype: Session
    """

    return sessionmaker(bind=engine)()

ssn = session()

row = ssn.execute("CREATE EXTENSION fuzzystrmatch;")