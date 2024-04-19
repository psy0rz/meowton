from peewee import Model, ForeignKeyField

from cat import Cat
from db import db


class CatSession(Model):

    # fields definition
    cat = ForeignKeyField(Cat, backref='cat_session')

    class Meta:
        database=db


db.create_tables([CatSession])
