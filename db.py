from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import config

#Session factory to create sessions to speak with our database
Session = sessionmaker();

#Generates table and mapper for all classes that we create
Base = declarative_base()

class RandomTable(Base):
	__tablename__ = 'random_table'

	t_id = Column(Integer, primary_key=True)
	
#Command history table
class CommandHistory(Base):
	__tablename__ = 'command_history'

	command_id = Column(Integer, primary_key=True)
	command = Column(String(50))
	params = Column(String(50))
	discord_id = Column(String(50))

#User command entered count table
class UserCommandCount(Base):
	__tablename__ = 'user_command_count'

	user_id = Column(Integer, primary_key=True)
	command_name = Column(String(50))
	count = Column(Integer)

#Table for the amount
class Bank(Base):
	__tablename__ = 'bank'

	user_id = Column(Integer, primary_key=True)
	discord_id = Column(String(50))
	funds = Column(Integer)

#Create the database connection and configure the session to be
#binded to the database
def create_db_connection():
	database = create_engine(config.MYSQL_URL)
	Session.configure(bind=database)
	Base.metadata.create_all(bind=database)

def close_database():
	session = Session()
	session.close()

#Create a new bank account for a user if they're not already registered one
def create_new_bank_account(discord_id):
	session = Session()
	user_in_db = session.query(Bank).filter(Bank.discord_id == discord_id).first()
	
	if user_in_db:
		return False

	new_banker = Bank(discord_id=discord_id, funds=200)
	session.add(new_banker)
	session.commit()
	
	return True

#Get the users funds
def get_funds(discord_id):
	session = Session()
	user_in_db = session.query(Bank).filter(Bank.discord_id == discord_id).first()

	if not user_in_db:
		return -1
	else:
		session.close()
		return user_in_db.funds


def subtract_funds(discord_id, amount):
	session = Session()
	user_in_db = session.query(Bank).filter(Bank.discord_id == discord_id).first()

	if not user_in_db:
		return False

	user_in_db.funds -= amount
	session.commit()


def add_funds(discord_id, amount):
	session = Session()
	user_in_db = session.query(Bank).filter(Bank.discord_id == discord_id).first()

	if not user_in_db:
		return False

	user_in_db.funds += amount
	session.commit()

def add_to_user_command_count(command_name, author):
	session = Session()

#Add commands to our history
def add_command_to_history(command_name, parameters, discord_id):
	session = Session()
	command = CommandHistory(command=command_name, params=" ".join(parameters), discord_id=discord_id)
	session.add(command)
	session.commit()