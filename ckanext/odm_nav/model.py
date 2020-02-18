from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, Boolean, DateTime, Text
from sqlalchemy import func
import ckan.model as model
import logging

log = logging.getLogger(__name__)

Base = declarative_base()


class Taxonomy(Base):
    """
    All taxonomy is store here.
    taxonomy: all child taxonomy
    parent_taxonomy: corresponding parent taxonomy
    """
    __tablename__ = 'odm_taxonomy'
    _id = Column(Integer, primary_key=True)
    taxonomy = Column(Text, nullable=False)
    parent_taxonomy = Column(Text, nullable=False)
    time_updated = Column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def load_table(cls, data_dict):
        """
        Create a session. Load all the data if successful commit the session.
        :param data_dict: dict
        :return: None
        """
        model.Session.query(cls).delete()

        for _parent in data_dict:

            # Parent taxonomy = child taxonomy
            tx_model = cls()
            tx_model.taxonomy = _parent
            tx_model.parent_taxonomy = _parent
            model.Session.add(tx_model)

            # Add all children
            _children = data_dict.get(_parent)
            for _child in _children:
                tx_model = cls()
                tx_model.taxonomy = _child
                tx_model.parent_taxonomy = _parent
                model.Session.add(tx_model)

        try:
            # Commit and close the session
            model.Session.commit()
            model.Session.close()
        except Exception as e:
            # Rollback if any error
            model.Session.rollback()
            model.Session.close()
            print("Failed to load taxonomy")
            print(e)


def init_tables():
    """
    Initialise the taxonomy table
    :return:
    """
    Base.metadata.create_all(model.meta.engine)