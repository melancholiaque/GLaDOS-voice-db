from sqlalchemy import *

metadata = MetaData()
engine = create_engine('sqlite:///glados.sqlite')
glados = Table(
        'GLaDOS',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('url', String(256), unique=True),
        Column('text', String(1024), unique=True, index=True),
        Column('record', LargeBinary)
)
metadata.create_all(engine)
