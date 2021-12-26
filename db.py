import mysql.connector

from datetime import datetime, timedelta

DB = ""
HOST = ""
PASSWORD = ""
USER = ""

cnx = None

def init_db():
    return mysql.connector.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        database=DB)

def get_cursor(cnx):
    try:
        cnx.ping(reconnect=True, attempts=3, delay=5)
    except mysql.connector.Error as err:
        # reconnect cursor
        cnx = init_db()
        print("Reconnected to database")
    return cnx.cursor()

cnx = init_db()
cursor = get_cursor(cnx)

def create_table(name):
    cursor = get_cursor(cnx)
    new_name = name.replace(" ", "_")
    create = (
        "CREATE TABLE IF NOT EXISTS " + new_name + " ("
        " _user_ VARCHAR(20),"
        " _rank_ SMALLINT,"
        " _date_ DATE,"
        " PRIMARY KEY (_user_)"
        ");"
    )
    cursor.execute(create)
    cnx.commit()

def addMember(name, db):
    cursor = get_cursor(cnx)
    new_db = db.replace(" ", "_")
    try:
        populate = "INSERT INTO " + new_db + " (_user_, _rank_, _date_) VALUES ('" + name + "', 500, '" + datetime.now().strftime("%Y-%m-%d") + "');"
        cursor.execute(populate)
        cnx.commit()
        return "You have successfully been registered! Your rank will now be tracked."
    except:
        reply = "There was an error trying to register " + str(name) + ", please make sure the name has no spaces and uses only letters and numbers"
        return reply


def removeMember(name, db):
    cursor = get_cursor(cnx)
    new_db = db.replace(" ", "_")
    delete = "DELETE FROM " + new_db + " WHERE _user_ = '" + name + "';"
    outcome = cursor.execute(delete)
    cnx.commit()
    if outcome == None:
        return "You have successfully resigned **" + name + "**!"

def printStandings(name):
    cursor = get_cursor(cnx)
    new_name = name.replace(" ", "_")
    cursor.execute("SELECT _user_, _rank_ FROM " + new_name + " ORDER BY _rank_ DESC;")
    result = cursor.fetchall()
    return result

def updateRank(name1, scored, name2, lost, db):
    cursor = get_cursor(cnx)
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

    # Could use an Actual Outcome value for a Best Of X series
    k = 100
    s = 400
    eOutcomeW = 1 / (1 + 10**((player2 - player1) / s))
    eOutcomeL = 1 / (1 + 10**((player1 - player2) / s))



    new_rank1 = player1 + abs((k * (1 - eOutcomeW)))
    new_rank2 = player2 + abs((k * (0 - eOutcomeL)))

    new_rank1 = round(new_rank1)
    new_rank2 = round(new_rank2)

    # Testing points
    print("Winner's gained rank after change")
    print(new_rank1 - player1)
    print("Loser's lost rank after change")
    print(new_rank2 - player2)
    print("------------------------------------------------")
    # Testing points

    if new_rank1 <= 0:
        cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(0) + "' WHERE _user_ = '" + name1 + "';")
    else:
        cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(new_rank1) + "' WHERE _user_ = '" + name1 + "';")

    if new_rank2 <= 0:
        cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(0) + "' WHERE _user_ = '" + name2 + "';")
    else:
        cursor.execute("UPDATE " + new_db + " SET _rank_ = '" + str(new_rank2) + "' WHERE _user_ = '" + name2 + "';")

    cursor.execute("UPDATE " + new_db + " SET _date_ = '" + datetime.now().strftime("%Y-%m-%d") + "' WHERE _user_ = '" + name1 + "';")

    cursor.execute("UPDATE " + new_db + " SET _date_ = '" + datetime.now().strftime("%Y-%m-%d") + "' WHERE _user_ = '" + name2 + "';")

    cnx.commit()

    return "**" + name1 + "**" + " beat " +  "**" + name2 + "** " + "``" +  str(scored) + "-" +  str(lost) + "``" +  " and won " + str(new_rank1 - player1) + " points"

def decay():
    cursor = get_cursor(cnx)
    cursor.execute("SHOW TABLES;")
    servers = cursor.fetchall()
    servers = str(servers)
    servers = servers.replace("[", "").replace("(", "").replace("'", "").replace(",", "").replace(")", "").replace("]", "")
    array = []

    while servers.find(" ") != -1:
        serverName = servers[0 : servers.find(" ")]
        array.append(serverName)
        servers = servers[servers.find(" ") + 1 : len(servers)]

    serverName = servers
    array.append(serverName)

    for i in array:
        dt = datetime.now()
        td = timedelta(days=14)
        dt = dt - td
        dt = dt.strftime("%Y-%m-%d")
        cursor.execute("SELECT _user_ FROM " + str(i) + " WHERE _date_ < '" + dt + "';")
        decayNames = cursor.fetchall()
        if len(decayNames) > 0:
            decayNames = str(decayNames)
            decayNames = decayNames.replace("[", "").replace("(", "").replace("'", "").replace(",", "").replace(")", "").replace("]", "")
            decayNamesArray = []
            while decayNames.find(" ") != -1:
                name = decayNames[0 : decayNames.find(" ")]
                decayNamesArray.append(name)
                decayNames = decayNames[decayNames.find(" ") + 1: len(decayNames)]

            name = decayNames
            decayNamesArray.append(name)

            for j in decayNamesArray:
                cursor.execute("SELECT _rank_ FROM " + str(i) + " WHERE _user_ = '" + str(j) + "';")
                check = cursor.fetchall()
                check = str(check)
                check = check.replace("[", "").replace("(", "").replace("'", "").replace(",", "").replace(")","").replace("]", "")
                check = int(check)

                if check - 20 <= 0:
                    cursor.execute("UPDATE " + str(i) + " SET _rank_ = " + str(0) + " WHERE _user_ = '" + str(j) + "';")
                else:
                    cursor.execute("UPDATE " + str(i) + " SET _rank_ = _rank_ - " + str(20) + " WHERE _user_ = '" + str(j) + "';")

    cnx.commit()



def delete_table(table_name):
    cursor = get_cursor(cnx)
    new_table_name = table_name.replace(" ", "_")
    cursor.execute("DROP TABLE " + new_table_name + ";")
    cnx.commit()