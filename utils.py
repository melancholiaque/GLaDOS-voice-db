from sqlalchemy.event import listens_for
from sqlalchemy import select as select, func
from sqlalchemy.sql.selectable import Select
from database import glados, engine
from IPython import embed
from pydub import AudioSegment
from pydub.playback import play as _play
from io import BytesIO
import os

def play(id):
    with engine.connect() as cur:
        bytes = cur.execute(select([glados.c.record]).where(glados.c.id==id)).scalar()
    song = AudioSegment.from_file(BytesIO(bytes), format="wav")
    print('playing...')
    _play(song)
    print('done!')

def save(id):
    with engine.connect() as cur:
        bytes = cur.execute(select([glados.c.record]).where(glados.c.id==id)).scalar()

    path = input('where to save your file?\n')
    
    if os.path.exists(path):
        if input(f'file {path} exists, override? [yes/no]: ').lower() not in ['yes', 'y']:
            return

    if not path.endswith('.wav'):
        path+='.wav'

    with open(path, 'wb') as fd:
        fd.write(bytes)

def get_audio(words):
    with engine.connect() as cur:
        query = select([glados.c.text, glados.c.id])
        for word in words:
            query = query.where(glados.c.text.contains(word))
        data = cur.execute(query).fetchall()
    return [(d.text, d.id) for d in data]

@listens_for(engine, 'before_execute')
def _(__, statement, ___, ____):
    assert (isinstance(statement, Select) or statement.lower().startswith('select'))
