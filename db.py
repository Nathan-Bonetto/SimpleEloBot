import os
import mysql.connector

DB = "bdyp15g5rpr8g0unf1wb"
HOST = "bdyp15g5rpr8g0unf1wb-mysql.services.clever-cloud.com"
PASSWORD = "ity9sbnvO6CkGEJYFU5n"
USER = "ujktbixkwxiso6cl"

cnx = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, database=DB)
cursor = cnx.cursor()

def create_table(name):
    new_name = name.replace(" ", "_")
    create = (
        "CREATE TABLE IF NOT EXISTS " + new_name + " ("
        " _user_ VARCHAR(20),"
        " _rank_ SMALLINT,"
        " PRIMARY KEY (_user_)"
        ");"
    )
    cursor.execute(create)
    cnx.commit()

def addMember(name, db):
    new_db = db.replace(" ", "_")
    try:
        populate = "INSERT INTO " + new_db + " (_user_, _rank_) VALUES ('" + name + "', 500);"
        cursor.execute(populate)
        cnx.commit()
        return "You have successfully been registered! Your rank will now be tracked."
    except:
        return "You are already registered!"


def removeMember(name, db):
    new_db = db.replace(" ", "_")
    delete = "DELETE FROM " + new_db + " WHERE _user_ = '" + name + "';"
    outcome = cursor.execute(delete)
    cnx.commit()
    if outcome == None:
        return "You have successfully resigned!"

def printStandings(name):
    new_name = name.replace(" ", "_")
    cursor.execute("SELECT * FROM " + new_name + " ORDER BY _rank_ ASC;")
    result = cursor.fetchall()
    return result