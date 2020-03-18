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
                    Height       VARCHAR(6),
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
            WHERE "StatInfo".Type = 'Pts' AND GameId = %(int)s
            ) AS "A"
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Rebound
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Reb' AND GameId = %(int)s
            ) AS "B"
            ON "A".PlayerId = "B".PlayerId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Ast' AND GameId = %(int)s
            ) AS "C"
            ON "B".PlayerId = "C".PlayerId;
        ''', {'int': game[4:]})
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
            WHERE "StatInfo".Type = 'Pts' AND GameId = %(int)s
            ) AS "A"
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Rebound
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Reb' AND GameId = %(int)s
            ) AS "B"
            ON "A".PlayerId = "B".PlayerId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( "Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id )
                WHERE "StatInfo".Type = 'Ast' AND GameId = %(int)s
            ) AS "C"
            ON "B".PlayerId = "C".PlayerId;
        ''', {'int': game[4:]})
    rows = cursor.fetchall()
    return rows

def showSchedule():
    cursor.execute(
        '''
        SELECT "Game".Id, "HomeTeam".TeamName AS HomeTeam, "AwayTeam".TeamName AS AwayTeam, "Game".GameDate
        FROM "Game"
             LEFT JOIN "Team" AS "HomeTeam" ON ( "Game".HomeTeamId = "HomeTeam".Id )
             LEFT JOIN "Team" AS "AwayTeam" ON ( "Game".AwayTeamId = "AwayTeam".Id )
        ORDER BY GameDate;
        ''')
    schedules = cursor.fetchall()
    print(schedules)
    return schedules

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

def showStandings():
    cursor.execute(
        '''
        SELECT "Team".TeamName, Wins, Losses
        FROM "Team" 
             INNER JOIN (
                 SELECT "W".TeamName AS Winner, "L".TeamName AS Loser, Wins, Losses
                 FROM (
                     SELECT "Team".TeamName, COUNT("Game".WinnerId) AS Wins
                     FROM "Game"
                          RIGHT JOIN "Team" ON ( "Game".WinnerId = "Team".Id )
                     GROUP BY TeamName
                     ) AS "W"
                     INNER JOIN(
                         SELECT "Team".TeamName, COUNT("Game".LoserId) AS Losses
                         FROM "Game"
                              RIGHT JOIN "Team" ON ( "Game".LoserId = "Team".Id )
                         GROUP BY TeamName
                     ) AS "L" ON "W".TeamName = "L".TeamName
             ) AS "Final" ON ("Team".TeamName = "Final".Winner AND "Team".TeamName = "Final".Loser)
        ORDER BY WINS DESC;
        '''
    )
    standing = cursor.fetchall()
    return standing


def showTeamList():
    cursor.execute(
        '''
        SELECT "Team".TeamName
        FROM "Team";
        '''
    )
    teams = cursor.fetchall()
    return teams

def showTeamInfo(team):
    cursor.execute(
        '''
        SELECT FirstName, LastName, Age, Height, Weight
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
        WHERE "Team".Id = %s;
        ''', (team[4:]))
    teams = cursor.fetchall()
    return teams


# IF THE GAME HAS NOT BEEN PLAYED YET AND USER SEARCHES THE GAME, SHOW GAME TIME, HOME TEAM, AWAY TEAM
def gamePreview(game):
    cursor.execute(
        '''
        SELECT "Game".Id, "HomeTeam".TeamName AS HomeTeam, "AwayTeam".TeamName AS AwayTeam, "Game".GameDate
        FROM "Game"
             LEFT JOIN "Team" AS "HomeTeam" ON ( "Game".HomeTeamId = "HomeTeam".Id )
             LEFT JOIN "Team" AS "AwayTeam" ON ( "Game".AwayTeamId = "AwayTeam".Id )
             WHERE "Game".Id = 4;
        ''', (game[4:]))

    rows = cursor.fetchall()
    return rows

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
    cursor.execute(
            '''
            SELECT pg_get_serial_sequence('"Player"', 'id'); -- returns 'player_id_seq'
            '''
    )
    cursor.execute(
        '''
        -- reset the sequence, regardless whether table has rows or not:
        SELECT setval(pg_get_serial_sequence('"Player"', 'id'), coalesce(max(id) + 1,1), false) FROM "Player";
        '''
        )
    db.commit()
    schedule = showSchedule()
    return render_template("home.html", title='Home', schedules=schedule)

@app.route('/team', methods=['GET', 'POST'])
def team():
    if request.method == "POST":
        team = request.form['team']
        teams = showTeamList()
        print(team)
        teamInfo = showTeamInfo(team)
        return render_template("team.html", title='Team', teams=teams, teamInfo=teamInfo)
    teams = showTeamList()
    return render_template("team.html", title='Team', teams=teams)

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

@app.route('/standings')
def standing():
    standing = showStandings()
    print(standing)
    return render_template("standings.html", title="Standings", standings=standing)

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
        print(height)
        weight = request.form['weight']
        print(weight)
        age = request.form['age']
        print(age)
        teamname = request.form['teamname']
        print(teamname)
       
        cursor.execute('''
        INSERT INTO "Player"(Id, FirstName, LastName, Height, Weight, Age, TeamID) 
        VALUES (DEFAULT, %s, %s, %s, %s, %s, (SELECT Id FROM "Team" WHERE TeamName = %s));
        ''', (firstname, lastname, height, weight, age, teamname))
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
        cursor.execute(
            '''
            INSERT INTO "StatInfo"(Type) 
            VALUES (%s, %s, %s)
            ''', (points, rebounds, assists))
        db.commit()
    return render_template("insert_stat.html", title='Insert Stat')

if __name__ == "__main__":
    app.run(debug=True)