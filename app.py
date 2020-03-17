from flask import Flask, render_template, request
import psycopg2
from psycopg2 import Error

app = Flask(__name__)

def connectToDB():
    try:
        return psycopg2.connect(host = "localhost", port = "5432", database = "test")
    except (Exception, psycopg2.Error) as error:
        print("Can't connect to database")
        print(error)

def createTables(cursor):
    try:
        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "Team" (
                    ID           SERIAL NOT NULL,
                    TeamName     VARCHAR(100) NOT NULL UNIQUE,

                    PRIMARY KEY (ID)
            );'''
        )
        print("Team: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "Player" (
                    ID           SERIAL NOT NULL,
                    FirstName    VARCHAR(30) NOT NULL,
                    LastName     VARCHAR(30) NOT NULL,
                    Height       VARCHAR(5),
                    Weight       INT,
                    Age          INT,
                    TeamId       INT NOT NULL,
                    
                    PRIMARY KEY (ID),
                    FOREIGN KEY (TeamId) REFERENCES "Team" (Id)
            );'''
        )
        print("Player: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "Season" (
                    Year         INT UNIQUE,

                    PRIMARY KEY (YEAR)
            ); '''
        )
        print("Season: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "Game" (
                    ID           SERIAL NOT NULL,
                    SeasonYear   INT NOT NULL,
                    HomeTeamId   INT NOT NULL,
                    AwayTeamId   INT NOT NULL,
                    WinnerId     INT,
                    LoserId      INT,
                    GameDate	 TIMESTAMPTZ,	

                    PRIMARY KEY (ID),
                    FOREIGN KEY (SeasonYear) REFERENCES "Season" (Year),
                    FOREIGN KEY (HomeTeamId) REFERENCES "Team" (Id),
                    FOREIGN KEY (AwayTeamId) REFERENCES "Team" (Id)
            ); '''
        )
        print("Game: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "StatType" (
                    ID           VARCHAR(5) NOT NULL,
                    Description  VARCHAR(30),

                    PRIMARY KEY (ID)
            );'''
        )
        print("StatType: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "StatInfo" (
                    ID           SERIAL NOT NULL,
                    PlayerID     INT NOT NULL,
                    GameID       INT NOT NULL,
                    Type         VARCHAR(5) NOT NULL,
                    StatValue    INT NOT NULL,
                    
                    PRIMARY KEY (ID),
                    FOREIGN KEY (PlayerId) REFERENCES "Player" (Id),
                    FOREIGN KEY (GameId) REFERENCES "Game" (Id),
                    FOREIGN KEY (Type) REFERENCES "StatType" (Id)
            );'''
        )
        print("StatInfo: Works")

        cursor.execute(
            ''' CREATE TABLE IF NOT EXISTS "TeamInSeason" (
                    SeasonId     INT NOT NULL,
                    TeamId       INT NOT NULL,
                    
                    PRIMARY KEY (SeasonId, TeamId),
                    FOREIGN KEY (SeasonId) REFERENCES "Season" (Year),
                    FOREIGN KEY (TeamId) REFERENCES "Team" (Id)
            );'''
        )
        print("TeamInSeason: Works")
        db.commit()


    except (Exception, psycopg2.DatabaseError) as error :
        print ("Error while creating PostgreSQL table", error)
        db.rollback()
    finally:
        #closing database connection.
            if(db):
                #cursor.close()
                # db.close()
                print("PostgreSQL connection is closed") 

def queryHomeTeam(game):
    cursor.execute(
        '''
        SELECT "C".FirstName, "C".LastName, "C".TeamName, "A".Points, "B".Rebound, "C".Assist
        FROM (
            SELECT "Player".Id AS PlayerId, "Game".Id AS GameId, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Points
            FROM "Player"
                 INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
                 INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
            WHERE "StatInfo".Type = 'Pts'
            ) AS "A"
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Rebound
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Reb'
            ) AS "B"
            ON "A".PlayerId = "B".PlayerId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Ast'
            ) AS "C"
            ON "B".PlayerId = "C".PlayerId
        WHERE "C".GameId = %s;
        ''', (game[4:]))
    rows = cursor.fetchall()
    return rows

def queryAwayTeam(game):
    cursor.execute(
        '''
        SELECT "C".FirstName, "C".LastName, "C".TeamName, "A".Points, "B".Rebound, "C".Assist
        FROM (
            SELECT "Player".Id AS PlayerId, "Game".Id AS GameId, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Points
            FROM "Player"
                 INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
                 INNER JOIN "Game" ON ( "Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id )
            WHERE "StatInfo".Type = 'Pts'
            ) AS "A"
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Rebound
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Reb'
            ) AS "B"
            ON "A".PlayerId = "B".PlayerId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Ast'
            ) AS "C"
            ON "B".PlayerId = "C".PlayerId
        WHERE "C".GameId = %s;
        ''', (game[4:]))
    rows = cursor.fetchall()
    return rows

def queryGameResult(game):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, SUM(StatValue) AS Points
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
            INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
            INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
						   OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Pts' AND "Game".Id = %s
        GROUP BY "Team".Id;
        ''', (game[4:]))
    rows = cursor.fetchall()
    return rows

"""
# NEED TO WORK ON STANDINGS
def showStandings():
    cursor.execute(
        '''
        SELECT TeamName, COUNT(WinnerID), COUNT(LoserID)
        FROM "Game"
             INNER JOIN "Team" ON ( "Game".HomeTeamID = "Team".ID AND "Game".AwayTeamID = "Team".ID )
        GROUP BY TeamName;
        '''
    )
    standing = cursor.fetchall()
    return standing

# IF THE GAME HAS NOT BEEN PLAYED YET AND USER SEARCHES THE GAME, SHOW GAME TIME, HOME TEAM, AWAY TEAM
def gamePreview(game):
    cursor.execute(
        '''
        SELECT TeamName, GameDate
        FROM "Game"
             INNER JOIN "Team" ON ( "Game".HomeTeamID = "Team".ID )
             INNER JOIN "Team" ON ( "Game".AwayTeamID = "Team".ID )
        WHERE "Game".Id = %s;
        ''', (game[4:]))
    
    rows = cursor.fetchall()
    return rows
"""

# def insert_stat(points, rebounds, assists):
#     cursor.execute(
#         '''
#         INSERT INTO "StatInfo"(Type)
#         VALUES (points);
#         FROM "Player"
#              INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
#             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
#             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
# 						   OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
#         WHERE "StatInfo".Type = 'Pts' AND "Game".Id = %s
#         GROUP BY "Team".Id;
#         ''', (ga[4:]))
#     rows = cursor.fetchall()
#     return rows



db = connectToDB()
cursor = db.cursor()
#createTables(cursor)

@app.route('/')
@app.route('/home')
def home():
    #standing = showStandings()
    return render_template("home.html", title='Home')

@app.route('/player_stats')
def player():
    return render_template("player_stats.html", title='Player')

@app.route('/game_stats', methods=['GET', 'POST'])
def game():
    if request.method == "POST":
        game = request.form['game']
        print(game)
        homeTeam = queryHomeTeam(game)
        awayTeam = queryAwayTeam(game)
        gameResult = queryGameResult(game)
        if homeTeam and awayTeam is not None:
            return render_template("game_stats.html", title='Game', homeTeam=homeTeam, 
                   awayTeam=awayTeam, gameResult=gameResult)
        else:
            gameInfo = gamePreview(game)
            print(gameInfo)
            return render_template("game_stats.html", title='Game', gameInfo = gameInfo)
    return render_template("game_stats.html", title='Game')

@app.route('/standing')
def standing():
    return render_template("standing.html", title="Standing")

@app.route('/update_game')
def update_game():
    return render_template("update_game.html", title="Update Game")

@app.route('/insert_player', methods=['GET', 'POST'])
def insert_player():
    if request.method == 'POST':

        firstname = request.form['firstname']
        print(firstname)
        lastname = request.form['lastname']
        print(lastname)
        height = request.form['height']
        weight = request.form['weight']
        age = request.form['age']
        teamID = request.form['teamid']
       
        cursor.execute('''
        INSERT INTO "Player"(FirstName, LastName, Height, Weight, Age, TeamID) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ''', (firstname, lastname, height, weight, age, teamID))
        db.commit()
    return render_template("insert_player.html", title='Insert Player')

@app.route('/insert_stat', methods=['GET','POST'])
def insert_stat():
    if request.method == 'POST':
        points = request.form['points']
        print(points)
        rebounds = request.form['rebounds']
        print(rebounds)
        assists = request.form['assists']
        print(assists)
        cursor.execute('''
        INSERT INTO "StatInfo"(Type) 
        VALUES (%s, %s, %s)
        ''', (points, rebounds, assists))
        db.commit()
    return render_template("insert_stat.html", title='Insert Stat')

if __name__ == "__main__":
    app.run(debug=True)