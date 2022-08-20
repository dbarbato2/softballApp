# App for creating the schedule for the Metrowest Mass girls Minors & Majors softball league
##########Backlog Items##############
# 1. Format the tables that output the schedule
# 2. Functionality to limit the number of home games on a single day per town

import datetime as dt
import math
from random import sample
import holidays
import pandas as pd
import streamlit as st
import re
import random

# Title the app
st.title('Softball Scheduling - Metrowest League')
us_holidays = holidays.UnitedStates()


# Function for creating the schedule
def makeSchedule(seas, yr, leag, sd, ng, gm, rs):
    #### First, create the array of team names
    teamList = []
    for i in range(0, len(teams)):
        counter = 1
        for j in range(0, teamCnt[i]):
            teamList.append(teams[i] + " Team #" + str(counter))
            counter = counter + 1
    totalTeams = len(teamList)
    #### Next, calculate the start day if it wasn't entered
    if sd == "":
        if seas == "Spring":
            ##### Season starts on the last Monday in April
            firstDay = dt.date(yr, 4, 1)
            wd = firstDay.weekday()
            firstMonday = firstDay + dt.timedelta(days=((7 - wd) % 7))
            startDay = firstMonday + dt.timedelta(days=21)
        if seas == "Summer":
            ##### Season starts on the third Thursday in June
            firstDay = dt.date(yr, 6, 1)
            wd = firstDay.weekday()
            firstMonday = firstDay + dt.timedelta(days=((7 - wd) % 7))
            firstThursday = firstMonday + dt.timedelta(days=3)
            startDay = firstThursday + dt.timedelta(days=14)
        if seas == "Fall":
            ##### Season starts on the first Saturday in September
            firstDay = dt.date(yr, 9, 1)
            wd = firstDay.weekday()
            firstMonday = firstDay + dt.timedelta(days=((7 - wd) % 7))
            firstSaturday = firstMonday + dt.timedelta(days=5)
            startDay = firstSaturday
    else:
        if seas == "Spring":
            ##### Check that it is a Monday and throw an error if not
            if (sd.weekday() != 0):
                st.error("Error: The starting date of the season is not on a Monday")
        if seas == "Summer":
            ##### Check that it is a Thursday and throw an error if not
            if (sd.weekday() != 3):
                st.error("Error: The starting date of the season is not on a Thursday")
        if seas == "Fall":
            ##### Check that it is a Saturday and throw an error if not
            if (sd.weekday() != 5):
                st.error("Error: The starting date of the season is not on a Saturday")
    gamesPerGameDay = math.floor(totalTeams / 2)
    #### If there's an odd number of teams, an extra week is needed to get closer to playing the desired number of games for each team
    if gm == 'Number of Game Days (Limits the Season Length & Allows for 1 Additional Game for a Bye)':
        schedGames = ng + (totalTeams % 2)
    else:
        if (totalTeams % 2 == 1):
            schedGames = ng + math.ceil(ng / totalTeams)
        else:
            schedGames = ng
    #### The schedOutput dataframe tracks the schedule and returns it
    column_names = ["date", "homeTeam", "awayTeam"]
    leagueSched = pd.DataFrame(columns=column_names)
    column_names2 = ["team", "homeGames", "awayGames", "byeCount", "playedTeams"]
    teamTrack = pd.DataFrame(columns=column_names2)
    for j in range(0, totalTeams):
        teamTrack.loc[j, 'team'] = teamList[j]
        teamTrack.loc[j, 'homeGames'] = 0
        teamTrack.loc[j, 'awayGames'] = 0
        teamTrack.loc[j, 'byeCount'] = 0
        teamTrack.loc[j, 'playedTeams'] = ""
    #### The Majors generally start the day after the Minors leagues start
    if (leag == 'Majors' or leag == 'Seniors'):
        gameDay = startDay + dt.timedelta(days=1)
    else:
        gameDay = startDay

    #### sub-function to choose the teams with the least amount of byes
    def byeTeamFunc(teamstoChooseFrom=""):
        if teamstoChooseFrom == "":
            teamswMinByeGames = teamTrack[teamTrack['byeCount'] == min(teamTrack['byeCount'])].team
        else:
            teamswMinByeGames = teamstoChooseFrom
        if (totalTeams % 2 == 1):
            byeTm = teamswMinByeGames.sample(n=1, random_state=rs)
        else:
            byeTm = ""
        return byeTm

    #### End byeTeamFunc function
    #### sub-function to choose the teams who have played the least or highest amount of home games
    def homeGameFunc(teamstoChooseFrom, minOrMax):
        if teamstoChooseFrom.empty:
            if minOrMax == 'min':
                teamswHomeGames = teamTrack[teamTrack['homeGames'] == min(teamTrack['homeGames'])]
            else:
                teamswHomeGames = teamTrack[teamTrack['homeGames'] == max(teamTrack['homeGames'])]
        else:
            teamswHomeGames = teamTrack[teamTrack['team'].isin(teamstoChooseFrom.values.tolist())]
        if minOrMax == 'min':
            teamsChosen = teamswHomeGames[teamTrack['homeGames'] == min(teamTrack['homeGames'])].team
        else:
            teamsChosen = teamswHomeGames[teamTrack['homeGames'] == max(teamTrack['homeGames'])].team
        return teamsChosen

    #### End homeGameFunc function

    for i in range(1, (schedGames + 1)):
        startIndex = (gamesPerGameDay * (i - 1)) + 1
        endIndex = gamesPerGameDay * i
        for j in range(startIndex, endIndex + 1):
            leagueSched.loc[j - 1, 'date'] = gameDay
        ##### First, select the bye team, users can not adjust this preference
        byeTeams = byeTeamFunc()
        ##### Second, let's make sure home games are evened out as much as possible when choosing home teams this week
        if (totalTeams % 2 == 1):
            teamswMinHomeGames = homeGameFunc(teamTrack[teamTrack['team'] != byeTeams.values[0]].team, 'min')
            firstChoiceTeams = set([x for x in teamList if x not in byeTeams.values]).intersection(
                teamswMinHomeGames.values)
        else:
            teamswMinHomeGames = homeGameFunc(teamTrack['team'], 'min')
            firstChoiceTeams = [x for x in teamList if x in teamswMinHomeGames.values]
        if (len(firstChoiceTeams) < gamesPerGameDay):
            ##### find how many more home teams need to be chosen for this date
            homeGameDiff = gamesPerGameDay - len(firstChoiceTeams)
            ##### Third, choose from among the remaining teams, those who have not played the most home games
            teamswMaxHomeGames = homeGameFunc(teamTrack['team'], 'max')
            sct = set([y for y in teamList if y not in byeTeams.values])
            sct2 = set([y2 for y2 in sct if y2 not in firstChoiceTeams])
            secondChoiceTeams = set([y3 for y3 in sct2 if y3 not in teamswMaxHomeGames])
            if (len(secondChoiceTeams) < homeGameDiff):
                ##### find how many more home teams need to be chosen for this date
                homeGameDiff2 = gamesPerGameDay - len(firstChoiceTeams) - len(secondChoiceTeams)
                ##### Last, choose randomly from among the remaining teams
                tct = set([y for y in teamList if y not in byeTeams.values])
                tct2 = set([y2 for y2 in tct if y2 not in firstChoiceTeams])
                thirdChoiceTeams = set([y3 for y3 in tct2 if y3 not in secondChoiceTeams])
                tiTemp = set(
                    pd.DataFrame(thirdChoiceTeams).sample(n=homeGameDiff2, random_state=rs, replace=False).squeeze(
                        axis=1))
                tiTemp2 = tiTemp.union(secondChoiceTeams)
                teamsIncluded = pd.DataFrame(tiTemp2.union(firstChoiceTeams))
            else:
                # st.write("pd.DataFrame(secondChoiceTeams) = ", pd.DataFrame(secondChoiceTeams).sample(n=homeGameDiff, random_state=rs, replace=False))
                tiTemp = set(
                    pd.DataFrame(secondChoiceTeams).sample(n=homeGameDiff, random_state=rs, replace=False).squeeze(
                        axis=1))
                teamsIncluded = pd.DataFrame(tiTemp.union(firstChoiceTeams))
        else:
            teamsIncluded = ''
            teamsIncluded = pd.DataFrame(firstChoiceTeams).sample(n=gamesPerGameDay, random_state=rs, replace=False)
        homeTeams = teamsIncluded
        ##### Now, choose opponents, try and avoid duplicate matches and inter-town matches if possible
        if (totalTeams % 2 == 1):
            # awayTeams = set([z for z in teamList if z not in byeTeams.values]).difference(set(homeTeams))
            awt = set([z for z in teamList if z not in byeTeams.values])
            awayTeams = set([z2 for z2 in awt if z2 not in set(homeTeams.squeeze(axis=1))])
        else:
            awayTeams = set([z for z in list(teamList) if z not in set(homeTeams.squeeze(axis=1))])
        ##### Convert the home teams and away teams sets into lists so we can subset them
        homeTeams = homeTeams[0].tolist()
        awayTeams = list(awayTeams)
        endFlag1 = 1
        for i2 in range(0, len(homeTeams)):
            ptstr = teamTrack.loc[teamTrack['team'] == homeTeams[i2], 'playedTeams']
            if awayTeams[i2] in str(ptstr):
                dupTeam = 1
            else:
                dupTeam = 0
            if re.sub('[^A-Za-z]+', '', awayTeams[i2]) == re.sub('[^A-Za-z]+', '', homeTeams[i2]):
                sameTown = 1
            else:
                sameTown = 0
            if dupTeam == 1 and sameTown == 1:
                endFlag1 = 0
            if i2 < len(awayTeams):
                for j2 in range(i2 + 1, len(awayTeams)):
                    if awayTeams[j2] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[j2]) != re.sub(
                            '[^A-Za-z]+', '', homeTeams[i2]):
                        tempTeam1 = awayTeams[j2]
                    else:
                        tempTeam1 = ''
                    if tempTeam1 != '' and endFlag1 == 0:
                        endFlag1 = 1
                        awayTeams[j2] = awayTeams[i2]
                        awayTeams[i2] = tempTeam1
            ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
            if endFlag1 == 0:
                if i2 > 1:
                    for j3 in range(0, i2):
                        if awayTeams[j3] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[j3]) != re.sub(
                                '[^A-Za-z]+', '', homeTeams[i2]):
                            tempTeam1 = awayTeams[j3]
                        else:
                            tempTeam1 = ''
                        if tempTeam1 != '' and endFlag1 == 0:
                            endFlag1 = 1
                            awayTeams[j3] = awayTeams[i2]
                            awayTeams[i2] = tempTeam1
            ###### If we can't get matchups avoiding duplicates and same town matchups, at least avoid duplicates
            if endFlag1 == 0:
                if i2 < len(awayTeams):
                    for j4 in range(i2 + 1, len(awayTeams)):
                        if awayTeams[j4] not in str(ptstr):
                            tempTeam1 = awayTeams[j4]
                        else:
                            tempTeam1 = ''
                        if (tempTeam1 != '' and endFlag1 == 0):
                            endFlag1 = 1
                            awayTeams[j4] = awayTeams[i2]
                            awayTeams[i2] = tempTeam1
            ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
            if endFlag1 == 0:
                if i2 > 1:
                    for j5 in range(1, i2 - 1):
                        if awayTeams[j5] not in str(ptstr):
                            tempTeam1 = awayTeams[j5]
                        else:
                            tempTeam1 = ''
                        if (tempTeam1 != '' and endFlag1 == 0):
                            endFlag1 = 1
                            awayTeams[j5] = awayTeams[i2]
                            awayTeams[i2] = tempTeam1
            ###### See if we can find a matchup that is not a duplicate and is also not two teams from the same town playing, then make sure to remove the duplicate
            if (dupTeam == 1 and sameTown == 0):
                endFlag2 = 0
                if i2 < len(awayTeams):
                    for k2 in range(i2 + 1, len(awayTeams)):
                        if awayTeams[k2] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[k2]) != re.sub(
                                '[^A-Za-z]+', '', homeTeams[i2]):
                            tempTeam2 = awayTeams[k2]
                        else:
                            tempTeam2 = ''
                        if (tempTeam2 != '' and endFlag2 == 0):
                            endFlag2 = 1
                            awayTeams[k2] = awayTeams[i2]
                            awayTeams[i2] = tempTeam2
                ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
                if endFlag2 == 0:
                    if i2 > 1:
                        for k3 in range(1, i2 - 1):
                            if awayTeams[k3] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[k3]) != re.sub(
                                    '[^A-Za-z]+', '', homeTeams[i2]):
                                tempTeam2 = awayTeams[k3]
                            else:
                                tempTeam2 = ''
                            if (tempTeam2 != '' and endFlag2 == 0):
                                endFlag2 = 1
                                awayTeams[k3] = awayTeams[i2]
                                awayTeams[i2] = tempTeam2
                ###### Now that we can't get both, at least try to remove the duplicate matchup
                if endFlag2 == 0:
                    if i2 < len(awayTeams):
                        for k4 in range(i2 + 1, len(awayTeams)):
                            if awayTeams[k4] not in str(ptstr):
                                tempTeam2 = awayTeams[k4]
                            else:
                                tempTeam2 = ''
                            if tempTeam2 != '' and endFlag2 == 0:
                                endFlag2 = 1
                                awayTeams[k4] = awayTeams[i2]
                                awayTeams[i2] = tempTeam2
                ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
                if endFlag2 == 0:
                    if i2 > 1:
                        for k5 in range(1, i2 - 1):
                            if awayTeams[k5] not in str(ptstr):
                                tempTeam2 = awayTeams[k5]
                            else:
                                tempTeam2 = ''
                            if (tempTeam2 != '' and endFlag2 == 0):
                                endFlag2 = 1
                                awayTeams[k5] = awayTeams[i2]
                                awayTeams[i2] = tempTeam2
            ###### Duplicate teams are more of a priority, so only look forward to avoid teams from the same town playing
            if (dupTeam == 0 and sameTown == 1):
                endFlag3 = 0
                if i2 < len(awayTeams):
                    for l2 in range(i2 + 1, len(awayTeams)):
                        if awayTeams[l2] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[l2]) != re.sub(
                                '[^A-Za-z]+', '', homeTeams[i2]):
                            tempTeam3 = awayTeams[l2]
                        else:
                            tempTeam3 = ''
                        if (tempTeam3 != '' and endFlag3 == 0):
                            endFlag3 = 1
                            awayTeams[l2] = awayTeams[i2]
                            awayTeams[i2] = tempTeam3
                ##### If we've gotten to the end and there is still teams from the same town playing, check back at the beginning
                if endFlag3 == 0:
                    if i2 > 1:
                        for l3 in range(1, i2 - 1):
                            if awayTeams[l3] not in str(ptstr) and re.sub('[^A-Za-z]+', '', awayTeams[l3]) != re.sub(
                                    '[^A-Za-z]+', '', homeTeams[i2]):
                                tempTeam3 = awayTeams[l3]
                            else:
                                tempTeam3 = ''
                            if (tempTeam3 != '' and endFlag3 == 0):
                                endFlag3 = 1
                                awayTeams[l3] = awayTeams[i2]
                                awayTeams[i2] = tempTeam3
        teamIndex = 0
        for l in range(startIndex - 1, endIndex):
            leagueSched.loc[l, 'homeTeam'] = homeTeams[teamIndex]
            leagueSched.loc[l, 'awayTeam'] = awayTeams[teamIndex]
            teamIndex += 1
        # Should only be 1 bye team at most
        if (totalTeams % 2 == 1):
            teamTrack.loc[teamTrack['team'] == byeTeams.values[0], 'byeCount'] += 1
        for j in range(0, len(homeTeams)):
            teamTrack.loc[teamTrack['team'] == homeTeams[j], 'homeGames'] += 1
            teamTrack.loc[teamTrack['team'] == homeTeams[j], 'playedTeams'] = teamTrack.loc[
                                                                                  teamTrack['team'] == homeTeams[
                                                                                      j], 'playedTeams'] + ", " + \
                                                                              teamTrack[
                                                                                  teamTrack['team'] == awayTeams[j]][
                                                                                  'team'].values[0]
        for k in range(0, len(awayTeams)):
            teamTrack.loc[teamTrack['team'] == awayTeams[k], 'awayGames'] += 1
            teamTrack.loc[teamTrack['team'] == awayTeams[k], 'playedTeams'] = teamTrack.loc[
                                                                                  teamTrack['team'] == awayTeams[
                                                                                      k], 'playedTeams'] + ", " + \
                                                                              teamTrack[
                                                                                  teamTrack['team'] == homeTeams[k]][
                                                                                  'team'].values[0]

        if gameDay.weekday() in range(0, 2):
            if ((gameDay + dt.timedelta(days=2)) in us_holidays):
                gameDay = gameDay + dt.timedelta(days=7)
            else:
                gameDay = gameDay + dt.timedelta(days=2)
        elif gameDay.weekday() in range(2, 4):
            if ((gameDay + dt.timedelta(days=5)) in us_holidays):
                gameDay = gameDay + dt.timedelta(days=7)
            else:
                gameDay = gameDay + dt.timedelta(days=5)
        ##### For weekend games, we need an added check to see if the following Monday is a holiday, making it a holiday weekend
        elif gameDay.weekday() in range(5, 7):
            if ((gameDay + dt.timedelta(days=7)) in us_holidays or (gameDay + dt.timedelta(days=8)) in us_holidays or (
                    gameDay + dt.timedelta(days=7)) in us_holidays):
                gameDay = gameDay + dt.timedelta(days=14)
            else:
                gameDay = gameDay + dt.timedelta(days=7)

        ##### Check that home games and byes are even
        if (max(teamTrack['homeGames']) >= (min(teamTrack['homeGames']) + 3)):
            st.error("Error: Home Games are Not Being Evenly Distributed")
        if (max(teamTrack['byeCount']) >= (min(teamTrack['byeCount']) + 2)):
            st.error("Error: Byes are Not Being Evenly Distributed")
        rs += 1
    #### End for loop
    blankIndex = [''] * len(teamTrack)
    teamTrack = teamTrack.rename(
        columns={"team": "Team", "homeGames": "Home Games", "awayGames": "Away Games", "byeCount": "Bye Count",
                 "playedTeams": "Played Teams"})
    teamTrack.index = blankIndex
    leagueSched = leagueSched.rename(columns={"date": "Date", "homeTeam": "Home Team", "awayTeam": "Away Team"})
    st.header(leag + " team tracking summary for " + seas + " season")
    st.table(teamTrack.style)
    st.header(leag + " schedule for " + seas + " season")
    st.table(leagueSched)


# End makeSchedule function

# Sidebar Design
st.sidebar.header("Schedule Inputs")
### Pick the season
season = st.sidebar.radio('Select the Season', ['Spring', 'Summer', 'Fall'])
### Select the number of Games
if (season == "Spring"):
    numberGames = st.sidebar.number_input("Enter the Number of Games", value=12)
if (season == "Summer"):
    numberGames = st.sidebar.number_input("Enter the Number of Games", value=6)
if (season == "Fall"):
    numberGames = st.sidebar.number_input("Enter the Number of Games", value=6)
gameMethod = st.sidebar.radio('Determine the Length of the Season', [
    'Number of Game Days (Limits the Season Length & Allows for 1 Additional Game for a Bye)',
    'Minimum Number of Games Played per Team (will Extend the Season Length)'])
### Determine fit he start date should be calculated
sdCalc = st.sidebar.checkbox("Manually enter the season start date?")
if sdCalc:
    startDay = st.sidebar.date_input("Season Start Date (first game)")
else:
    startDay = ""
### Enter the year
year = st.sidebar.number_input("Enter the Year", 2010, 2100, 2022)
### Select the league
league = st.sidebar.radio('Which League is this for', ['Minors', 'Majors', 'Seniors'])
### Set the total number of towns for the for loop
numTeams = st.sidebar.number_input("How many towns are playing?", 1, 50)
### Enter the towns and the number of teams within each town
teams = []
teamCnt = []
teams.append(st.sidebar.text_input("Enter the first town to add to the schedule", ""))
teamCnt.append(st.sidebar.slider("Select the number of teams for town 1", 1, 4))
if numTeams > 1:
    for x in range(1, numTeams):
        teams.append(st.sidebar.text_input(f'Enter the number {x + 1:2d} town', ""))
        teamCnt.append(st.sidebar.slider(f'Select the number of teams for town {x + 1:2d}', 1, 4))

schedButton = st.sidebar.button("Calculate Schedule")
### Random seed for choosing teams, this should be different each time the button is pressed so a new schedule is generated
randomSeed = random.randint(1, 100)

# Main Panel Design
if schedButton:
    makeSchedule(season, year, league, startDay, numberGames, gameMethod, randomSeed)
