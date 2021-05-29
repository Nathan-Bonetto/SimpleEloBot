import mysql.connector

DB = ""
HOST = ""
PASSWORD = ""
USER = ""

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
    cursor.execute("SELECT * FROM " + new_name + " ORDER BY _rank_ DESC;")
    result = cursor.fetchall()
    return result

def updateRank(name1, name2, scored, lost, db):
    new_db = db.replace(" ", "_")
    cursor.execute("SELECT _rank_ FROM " + new_db + " WHERE _user_ = '" + name1 + "';")
    player = cursor.fetchone()
    player1 = player[0]
    player1 = int(player1)
    cursor.execute("SELECT _rank_ FROM " + new_db + " WHERE _user_ = '" + name2 + "';")
    player = cursor.fetchone()
    player2 = player[0]
    player2 = int(player2)

    scored = int(scored)
    lost = int(lost)

    # Testing points
    print("Winners rank before change")
    print(player1)
    print("Losers rank before change")
    print(player2)
    # Testing points

    k = 100
    HGA = 2
    s = 40
    aOutcome = scored / (scored + lost)
    eOutcome = 1 / (1 + 10**((player2 - player1 - HGA) / s))

    new_rank1 = player1 + abs((k * (aOutcome - eOutcome)))
    new_rank2 = player2 - abs((k * (aOutcome - eOutcome)))

    new_rank1 = round(new_rank1)
    new_rank2 = round(new_rank2)

    # Testing points
    print("Winner's gained rank after change")
    print(new_rank1 - player1)
    print("Loser's lost rank after change")
    print(new_rank2 - player2)
    print("------------------------------------------------")
    # Testing points

    cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(new_rank1) + "' WHERE _user_ = '" + name1 + "';")

    cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(new_rank2) + "' WHERE _user_ = '" + name2 + "';")
    cnx.commit()

    return name1 + " beat " + name2 + " and won " + str(new_rank1 - player1) + " points"