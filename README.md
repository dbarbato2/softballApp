# softballApp
Version 1.1, 8/20/2022, Python 3.9
Author: Darrel Barbato

##Overview
This application is built in Streamlit and can be used to create a season schedule for any number of teams. While
the application was designed to create the schedule for Metrowest Grils Softball League (Spring, Summer, or Fall)
it is general enough to create a schedule for use in many different types of leagues that follow some basic principles.
###Principles
1. 'Towns' are used to distinguish groups of teams. In other words a team can be represented as 'Town Team #1' or Town Team #2'. 
If no such groups of teams are desired, users can simply specify one team per town.
2. The schedule defaults to the number of games and days of the week used by the Metrowest Softball League, however, the starting 
date for the season can be changed as needed. If a user does not want to use one of the patterns for days of the week in the 
app (i.e. games every Tuesday/Thursday for Majors in the Spring), then game days will have to be altered outside of the app.
3. Games on U.S. holidays and holiday weekends are avoided by default
4. Users can specify how to deal with byes. Byes are automatically dispersed equally if there is an uneven amount of teams, 
however, users can specify additional games/weeks in the schedule should be added to account for the presence of byes.
5. Rules such as avoiding duplicate match-ups, inter-town match-ups, and multiple home games for a town on the same day 
are built in with their own prioritization and can not be altered. The first priority is to even out byes, the second is to even
out home games, the third is avoid duplicate match-ups, and the fourth is to avoid inter-town match-ups.

##How it Works
Users can run the application once deployed or as a Python script by typing 'streamlit run main.py' once the streamlit package for
Python has been installed. In the sidebar on the left, users will need to select the following parameters:
1. The season (options include Spring, Summer, and Fall).
2. The number of games (this will default to 12 for the Spring and 6 for the Summer and Fall but can be modified).
3. Determine the length of the season. There are currently two options, one to select the number of game days (default). This will 
essentially limit the season to n or n+1 games (in the event of an odd number of teams), where n is the number of games parameter
selected above. The second option is to ensure that each team plays at least as many games, n, as specified in the number of games
parameter selected above. Note that this second option may potentially extend the season substantially.
4. An option to manually enter the season start date (turned off by default). Typically the spring season will start on the
last Monday in April, the summer season on the third Thursday in June, and the fall on the first Saturday in September. Spring and Summer
game days will be every Monday & Wednesday for the Minors and every Tuesday & Thursday for the Majors/Seniors. Fall game days will be
every Saturday for the Minors and every Sunday for the Majors/Seniors. All major U.S. holidays and holiday weekends are avoided by default.
5. The year for the season. This is used solely to calculate the dates correctly.
6. The league (options include Minors, Majors, and Seniors). For the Metrowest Softball League, Minors refers to our 3rd & 4th grade league
(U10), Majors refers to our 5th & 6th grade league (U12), and Seniors refers to our 7th & 8th grade league (U14). All implications of
this selection are discussed above.
7. The number of towns playing. Based on this selection, text boxes will appear for each town asking for the name of the town and the number 
of teams playing within each town. If x towns are selected, town names and number of teams must be selected for all x towns. Naming convention
in the schedule will be 'Town Name' Team #'i', where 'Town Name' is the text entered by the user and 'i' is the sequentially numbering of the team.
Currently, custom team names are not allowed, but could be created using 1 team per town and custom names for each town.

After all of the parameters have been selected, press the 'Calculate Schedule' button to build the schedule.
Once run, the application will return a Streamlit table that tracks a summary for each team that includes the number of home
games, the number of away games, the number of byes (should be 0 if there are an even number of teams), and a list containing 
each team they are playing on the schedule. It will also output a Streamlit table containing a row for each game on the schedule
along with the date of the game, the home team, and the away team. Game times are not specified.

_Note that each time the 'Calculate Schedule' button is pressed (if the debug indicator is 0) a new schedule is created._