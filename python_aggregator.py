import pandas as pd
import sqlalchemy


from sqlalchemy import create_engine
from sqlalchemy import text

source = "sqlite:///steam.db"
engine = create_engine(source)





