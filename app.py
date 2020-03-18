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

def queryTotalPoints(game):
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

def queryTotalRebounds(game):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, SUM(StatValue) AS Rebound
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
							OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Reb' AND "Game".Id = %s
        GROUP BY "Team".Id;
        ''', (game[4:]))
    rows = cursor.fetchall()
    return rows

def queryTotalAssists(game):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, SUM(StatValue) AS Rebound
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
							OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Ast' AND "Game".Id = %s
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

def showAveragePoints(team):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, ROUND((CAST(SUM(StatValue) AS DECIMAL) / 3), 1) AS PPG
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
							OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Pts' AND "Team".Id = %s
		GROUP BY "Team".TeamName;
        ''', (team[4:]))
    stat = cursor.fetchall()
    return stat

def showAverageRebounds(team):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, ROUND((CAST(SUM(StatValue) AS DECIMAL) / 3), 1) AS RPG
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
							OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Reb' AND "Team".Id = %s
		GROUP BY "Team".TeamName;
        ''', (team[4:]))
    stat = cursor.fetchall()
    return stat
		

def showAverageAssists(team):
    cursor.execute(
        '''
        SELECT "Team".TeamName AS TeamName, ROUND((CAST(SUM(StatValue) AS DECIMAL) / 3), 1) AS APG
        FROM "Player"
             INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
             INNER JOIN "Game" ON ( ("Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id) 
							OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
        WHERE "StatInfo".Type = 'Ast' AND "Team".Id = %s
		GROUP BY "Team".TeamName;
        ''', (team[4:]))
    stat = cursor.fetchall()
    return stat

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

def queryPlayerStat(firstname, lastname, teamname):
    cursor.execute(
        '''
        SELECT "D".GameDate, "A".Points, "B".Rebound, "C".Assist
        FROM (
            SELECT "Player".Id AS PlayerId, "Game".Id AS GameId, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Points, "Game".gamedate AS GameDate
            FROM "Player"
                 INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	             INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
                 INNER JOIN "Game" ON ( ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                                 OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
            WHERE "StatInfo".Type = 'Pts' 
            ) AS "A"
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Rebound, "Game".gamedate AS GameDate
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                                OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
                WHERE "StatInfo".Type = 'Reb' 
            ) AS "B"
            ON "A".PlayerId = "B".PlayerId AND "A".GameId = "B".GameId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist, "Game".gamedate AS GameDate
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                                OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
                WHERE "StatInfo".Type = 'Ast' 
            ) AS "C"            
            ON "B".PlayerId = "C".PlayerId AND "B".GameId = "C".GameId
            INNER JOIN (
                SELECT "Player".Id AS PlayerId, "Game".Id AS GameID, FirstName, LastName, "Team".TeamName AS TeamName, StatValue AS Assist, "Game".gamedate AS GameDate
                FROM "Player"
                     INNER JOIN "Team" ON ( "Player".TeamId = "Team".Id )
	                 INNER JOIN "StatInfo" ON ( "Player".Id = "StatInfo".PlayerId )
	                 INNER JOIN "Game" ON ( ( "Team".Id = "Game".HomeTeamId AND "StatInfo".GameId = "Game".Id )
                                OR  ("Team".Id = "Game".AwayTeamId AND "StatInfo".GameId = "Game".Id) )
                WHERE "StatInfo".Type = 'Ast' 
            ) AS "D"            
            ON "C".PlayerId = "D".PlayerId AND "C".GameId = "D".GameId
        WHERE "C".FirstName = %s AND "C".LastName = %s AND "C".TeamName = %s;
        ''', (firstname, lastname, teamname)) 
    rows = cursor.fetchall()

    return rows

def displayTeamsPlayed(game):
    cursor.execute(
        '''
        SELECT TeamName
        FROM "Team"
             INNER JOIN "Game" ON ( "Team".Id = "Game".HomeTeamId OR "Team".Id = "Game".AwayTeamId )
        WHERE "Game".Id = %s;
        ''', (game[4:]))
    teams = cursor.fetchall()
    return teams

def updateGameResult(winner, loser, game):
    print(winner)
    print(loser)
    print(game)
    cursor.execute(
        '''
        UPDATE "Game"
        SET WinnerId = (SELECT "Team".Id FROM "Team" WHERE TeamName ILIKE %s),
            LoserId = (SELECT "Team".Id FROM "Team" WHERE TeamName ILIKE %s)
        WHERE "Game".Id = %s;
        ''', (winner, loser, game[4:]))
    db.commit()

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
    cursor.execute(
            '''
            SELECT pg_get_serial_sequence('"StatInfo"', 'id'); 
            '''
    )
    cursor.execute(
        '''
        -- reset the sequence, regardless whether table has rows or not:
        SELECT setval(pg_get_serial_sequence('"StatInfo"', 'id'), coalesce(max(id) + 1,1), false) FROM "StatInfo";
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
        ppg = showAveragePoints(team)
        rpg = showAverageRebounds(team)
        apg = showAverageAssists(team)
        return render_template("team.html", title='Team', teams=teams, teamInfo=teamInfo, ppg=ppg, rpg=rpg, apg=apg)
    teams = showTeamList()
    return render_template("team.html", title='Team', teams=teams)

@app.route('/player_stats', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        firstname = request.form['firstname']
        print(firstname)
        lastname = request.form['lastname']
        print(lastname)
        teamname = request.form['teamname']
        print(teamname)

        playerStat = queryPlayerStat(firstname, lastname, teamname)
        print(playerStat)
        if firstname and lastname and teamname is not None:
            return render_template("player_stats.html", title='Player', playerStat = playerStat, 
                    firstname = firstname, lastname = lastname, teamname = teamname)
        #else()

    return render_template("player_stats.html", title='Player')

@app.route('/game_stats', methods=['GET', 'POST'])
def game():
    if request.method == "POST":
        game = request.form['game']
        print(game)
        homeTeam = queryHomeTeam(game)
        awayTeam = queryAwayTeam(game)
        totalPoints = queryTotalPoints(game)
        totalRebounds = queryTotalRebounds(game)
        totalAssists = queryTotalAssists(game)
        print(totalPoints)
        print(totalRebounds)
        print(totalAssists)
        if homeTeam and awayTeam is not None:
            return render_template("game_stats.html", title='Game', homeTeam=homeTeam, 
                   awayTeam=awayTeam, totalPoints=totalPoints, totalRebounds=totalRebounds, totalAssists=totalAssists)
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

@app.route('/update_game', methods=['GET', 'POST'])
def update_game():
    if request.method == "POST":
        game = request.form['game']
        teams = displayTeamsPlayed(game)
        winner = request.form['winner']
        loser = request.form['loser']
        updateGameResult(winner, loser, game)
        return render_template("update_game.html", title="Update Game", winner=winner, loser=loser, game=game)
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

        firstname =request.form['firstname']
        lastname =request.form['lastname']
        teamname = request.form['teamname']
        game = request.form['game']
        points = request.form['points']
        print(points)
        rebounds = request.form['rebounds']
        assists = request.form['assists']
        
        cursor.execute(
            '''
            INSERT INTO "StatInfo"(PlayerID, GameID, Type, StatValue) 
            VALUES ((SELECT "Player".Id FROM "Player" INNER JOIN "Team" ON ("Player".TeamId = "Team".Id) WHERE firstName = %s AND lastName = %s), %s, %s, %s)
            ''', (firstname, lastname, game[4:],'Pts', points))

        cursor.execute(
            '''
            INSERT INTO "StatInfo"(PlayerID, GameID, Type, StatValue) 
            VALUES ((SELECT "Player".Id FROM "Player" INNER JOIN "Team" ON ("Player".TeamId = "Team".Id) WHERE firstName = %s AND lastName = %s), %s, %s, %s)
            ''', (firstname, lastname, game[4:],'Reb', rebounds))

        cursor.execute(
            '''
            INSERT INTO "StatInfo"(PlayerID, GameID, Type, StatValue) 
            VALUES ((SELECT "Player".Id FROM "Player" INNER JOIN "Team" ON ("Player".TeamId = "Team".Id) WHERE firstName = %s AND lastName = %s), %s, %s, %s)
            ''', (firstname, lastname, game[4:],'Ast', assists))

        db.commit()
    return render_template("insert_stat.html", title='Insert Stat')

if __name__ == "__main__":
    app.run(debug=True)
