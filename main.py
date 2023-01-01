# App for creating the schedule for the Metrowest Mass girls Minors & Majors softball league
##########Backlog Items##############
# 1. Format the tables that output the schedule
# 2. Functionality to limit the number of home games on a single day per town

import datetime as dt
import holidays
import math
from random import sample
import pandas as pd
import streamlit as st
import re
import random

# Title the app
st.title('Softball Scheduling - Metrowest League')
us_holidays = holidays.UnitedStates()
### Indicator on whether to run the app in debug mode (makes the schedule calculation repeatable)
debugInd = 0

# Function for creating the schedule
def makeSchedule(seas, yr, leag, sd, ng, gm, twnm, rs):
    #### First, create the array of team names
    teamList = []
    sameTownTeams = []
    sameTownTeamsHome = []
    sameTownTeamsAway = []
    for i in range(0, len(teams)):
        counter = 1
        for j in range(0, teamCnt[i]):
            teamList.append(teams[i] + " Team #" + str(counter))
            if teamCnt[i] % 2 == 0 or (teamCnt[i] - j) > 1:
                sameTownTeams.append(teams[i] + " Team #" + str(counter))
                ###Choose the even numbered teams to be home teams to make sure we don't have too many where we have to sample
                if counter % 2 == 0:
                    sameTownTeamsHome.append(teams[i] + " Team #" + str(counter))
                    sameTownTeamsAway.append(teams[i] + " Team #" + str(counter - 1))
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
        firstGameDay = startDay + dt.timedelta(days=1)
    else:
        firstGameDay = startDay
    #### Need to find the last game day as we will make the schedule in Reverse in case inter-town match-ups are required on the last day
    h = firstGameDay
    for g in range(1, schedGames):
        if h.weekday() in range(0, 2):
            if((h + dt.timedelta(days=2)) in us_holidays):
                h = h + dt.timedelta(days=7)
            else:
                h = h + dt.timedelta(days=2)
        elif h.weekday() in range(2, 4):
            if ((h + dt.timedelta(days=5)) in us_holidays):
                h = h + dt.timedelta(days=7)
            else:
                h = h + dt.timedelta(days=5)
        ##### For weekend games, we need an added check to see if the following Monday is a holiday, making it a holiday weekend
        elif h.weekday() in range(5, 7):
            if ((h + dt.timedelta(days=7)) in us_holidays or (h + dt.timedelta(days=8)) in us_holidays or (h + dt.timedelta(days=9)) in us_holidays):
                h = h + dt.timedelta(days=14)
            else:
                h = h + dt.timedelta(days=7)
    lastGameDay = h
    #### End makeSchedule function

    #### sub-function to choose the teams with the least amount of byes
    def byeTeamFunc(teamstoChooseFrom=[]):
        if len(teamstoChooseFrom) == 0:
            teamswMinByeGames = teamTrack[teamTrack['byeCount'] == min(teamTrack['byeCount'])].team
            if debugInd == 1: st.write("teamswMinByeGames (in if) = ", teamswMinByeGames)
        else:
            teamswMinByeGames = teamstoChooseFrom
            if debugInd == 1: st.write("teamswMinByeGames (in else) = ", teamswMinByeGames)
        if (totalTeams % 2 == 1):
            byeTm = pd.DataFrame(teamswMinByeGames, columns = ['team']).sample(n=1, random_state=rs).squeeze(
                        axis=1)
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

    #### sub-function that searches through the given indices to select a new away team for the home team to play, avoiding duplicate matchups and/or matchups with the same town (for any re-assigned games as well)
    def dupSameTownCheckFunc(startIndex, endIndex, parentIndex, dupInd, stInd):
        if debugInd == 1: st.write("in dupSameTownCheckFunc code")
        ef = 0
        for k in range(startIndex, endIndex):
            ptstr = teamTrack.loc[teamTrack['team'] == homeTeams[parentIndex], 'playedTeams']
            ptstr2 = teamTrack.loc[teamTrack['team'] == homeTeams[k], 'playedTeams']
            with pd.option_context('display.max_colwidth', -1):
                ps = ptstr.to_string()
                ps2 = ptstr2.to_string()
            if dupInd == 1 and stInd == 1:
                if awayTeams[k] not in ps and re.sub('[^A-Za-z]+', '', awayTeams[k]) != re.sub('[^A-Za-z]+', '', homeTeams[parentIndex]) and awayTeams[parentIndex] not in ps2 and re.sub('[^A-Za-z]+', '', awayTeams[parentIndex]) != re.sub('[^A-Za-z]+', '', homeTeams[k]):
                        tempTeam1 = awayTeams[k]
                else:
                        tempTeam1 = ''
            if dupInd == 1 and stInd == 0:
                if awayTeams[k] not in ps and awayTeams[parentIndex] not in ps2:
                        tempTeam1 = awayTeams[k]
                else:
                        tempTeam1 = ''
            if dupInd == 0 and stInd == 1:
                if re.sub('[^A-Za-z]+', '', awayTeams[k]) != re.sub('[^A-Za-z]+', '', homeTeams[parentIndex]) and re.sub('[^A-Za-z]+', '', awayTeams[parentIndex]) != re.sub('[^A-Za-z]+', '', homeTeams[k]):
                        tempTeam1 = awayTeams[k]
                else:
                        tempTeam1 = ''
            if (tempTeam1 != '' and ef == 0):
                ef = 1
                awayTeams[k] = awayTeams[parentIndex]
                awayTeams[parentIndex] = tempTeam1
        return ef
    #### End dupSameTownCheckFunc function

    if debugInd == 1: st.write("firstGameday =", firstGameDay)
    if debugInd == 1: st.write("lastgameday =", lastGameDay)
    #### Go through the assignments in reverse order in case the last game needs to have inter-town match-ups
    gameDay = lastGameDay

    for i in range(schedGames, 0, -1):
        startIndex = (gamesPerGameDay * (i - 1)) + 1
        endIndex = gamesPerGameDay * i
        if debugInd == 1: st.write("gameday =", gameDay)
        for j in range(startIndex, endIndex + 1):
            leagueSched.loc[j - 1, 'date'] = gameDay
        ##### First, select the bye team, users can not adjust this preference
        if (twnm == 'Have Inter-Town Match-Ups to End the Season (if possible)' and i == schedGames):
            #### Just pick from the towns who don't have more than 1 team
            byeChoiceTeams = set([x for x in teamList if x not in sameTownTeams])
            if debugInd == 1: st.write("byeChoiceTeams =", byeChoiceTeams)
            if debugInd == 1: st.write("length of byeChoiceTeams =", len(byeChoiceTeams))
            btd = list(byeChoiceTeams)
            if len(byeChoiceTeams) == 0: byeTeams = byeTeamFunc()
            else: byeTeams = byeTeamFunc(btd)
            if debugInd == 1: st.write("byeTeams =", byeTeams)
        else:
            byeTeams = byeTeamFunc()
        ##### Second, let's make sure home games are evened out as much as possible when choosing home teams this week
        if (twnm == 'Have Inter-Town Match-Ups to End the Season (if possible)' and i == schedGames):
            #### Just pick from the towns who do have more than 1 team
            if (totalTeams % 2 == 1):
                stt = [x for x in teamList if x not in byeTeams.values]
                firstChoiceTeams = [x2 for x2 in stt if x2 in sameTownTeamsHome]
                if debugInd == 1: st.write("firstChoiceTeams = ", firstChoiceTeams)
            else:
                firstChoiceTeams = [x2 for x2 in teamList if x2 in sameTownTeamsHome]
                if debugInd == 1: st.write("firstChoiceTeams = ", firstChoiceTeams)
            if (len(firstChoiceTeams) < gamesPerGameDay):
                homeGameDiffst = gamesPerGameDay - len(firstChoiceTeams)
                if (totalTeams % 2 == 1):
                    st1 = set([y for y in teamList if y not in byeTeams.values])
                    st2 = set([y2 for y2 in st1 if y2 not in firstChoiceTeams])
                    st3 = set([y3 for y3 in st2 if y3 not in sameTownTeamsAway])
                else:
                    st2 = set([y2 for y2 in teamList if y2 not in firstChoiceTeams])
                    st3 = set([y3 for y3 in st2 if y3 not in sameTownTeamsAway])
                stTemp = set(pd.DataFrame(st3).sample(n=homeGameDiffst, random_state=rs, replace=False).squeeze(
                        axis=1))
                firstChoiceTeams = list(set(firstChoiceTeams).union(stTemp))
                if debugInd == 1: st.write("firstChoiceTeams within extra if sameTeam statement = ", firstChoiceTeams)
        else:
            if (totalTeams % 2 == 1):
                teamswMinHomeGames = homeGameFunc(teamTrack[teamTrack['team'] != byeTeams.values[0]].team, 'min')
                firstChoiceTeams = set([x for x in teamList if x not in byeTeams.values]).intersection(
                    teamswMinHomeGames.values)
                if debugInd == 1: st.write("firstChoiceTeams = ", firstChoiceTeams)
            else:
                teamswMinHomeGames = homeGameFunc(teamTrack['team'], 'min')
                firstChoiceTeams = [x for x in teamList if x in teamswMinHomeGames.values]
                if debugInd == 1: st.write("firstChoiceTeams = ", firstChoiceTeams)
        if (len(firstChoiceTeams) < gamesPerGameDay):
            if debugInd == 1: st.write("inside firstChoiceTeams if, need more home teams")
            ##### find how many more home teams need to be chosen for this date
            homeGameDiff = gamesPerGameDay - len(firstChoiceTeams)
            ##### Third, choose from among the remaining teams, those who have not played the most home games
            teamswMaxHomeGames = homeGameFunc(teamTrack['team'], 'max')
            if (totalTeams % 2 == 1):
                sct = set([y for y in teamList if y not in byeTeams.values])
                sct2 = set([y2 for y2 in sct if y2 not in firstChoiceTeams])
            else:
                sct2 = set([y2 for y2 in teamList if y2 not in firstChoiceTeams])
            secondChoiceTeams = set([y3 for y3 in sct2 if y3 not in teamswMaxHomeGames])
            if debugInd == 1: st.write("secondChoiceTeams = ", secondChoiceTeams)
            if (len(secondChoiceTeams) < homeGameDiff):
                if debugInd == 1: st.write("inside secondChoiceTeams if, still don't have enough home teams")
                ##### find how many more home teams need to be chosen for this date
                homeGameDiff2 = gamesPerGameDay - len(firstChoiceTeams) - len(secondChoiceTeams)
                ##### Last, choose randomly from among the remaining teams
                if (totalTeams % 2 == 1):
                    tct = set([y for y in teamList if y not in byeTeams.values])
                    tct2 = set([y2 for y2 in tct if y2 not in firstChoiceTeams])
                else:
                    tct2 = set([y2 for y2 in teamList if y2 not in firstChoiceTeams])
                thirdChoiceTeams = set([y3 for y3 in tct2 if y3 not in secondChoiceTeams])
                tiTemp = set(
                    pd.DataFrame(thirdChoiceTeams).sample(n=homeGameDiff2, random_state=rs, replace=False).squeeze(
                        axis=1))
                tiTemp2 = tiTemp.union(secondChoiceTeams)
                teamsIncluded = pd.DataFrame(tiTemp2.union(firstChoiceTeams))
            else:
                if debugInd == 1: st.write("inside secondChoiceTeams else, found enough home teams")
                tiTemp = set(
                    pd.DataFrame(secondChoiceTeams).sample(n=homeGameDiff, random_state=rs, replace=False).squeeze(
                        axis=1))
                teamsIncluded = pd.DataFrame(tiTemp.union(firstChoiceTeams))
        else:
            teamsIncluded = pd.DataFrame(firstChoiceTeams).sample(n=gamesPerGameDay, random_state=rs, replace=False)
        homeTeams = teamsIncluded
        ##### Now, choose opponents, try and avoid duplicate matches and inter-town matches if possible
        if (totalTeams % 2 == 1):
            awt = set([z for z in teamList if z not in byeTeams.values])
            awayTeams = set([z2 for z2 in awt if z2 not in set(homeTeams.squeeze(axis=1))])
            if debugInd == 1: st.write("awayTeams = ", awayTeams)
        else:
            awayTeams = set([z for z in list(teamList) if z not in set(homeTeams.squeeze(axis=1))])
            if debugInd == 1: st.write("awayTeams = ", awayTeams)
        ##### Convert the home teams and away teams sets into lists so we can subset them
        homeTeams = homeTeams[0].tolist()
        awayTeams = list(awayTeams)
        endFlag1 = 1
        for i2 in range(0, len(homeTeams)):
            if debugInd == 1: st.write("i2 = ", i2)
            if debugInd == 1: st.write("awayTeams[i2] = ", awayTeams[i2])
            if debugInd == 1: st.write("homeTeams[i2] = ", homeTeams[i2])
            ptstr = teamTrack.loc[teamTrack['team'] == homeTeams[i2], 'playedTeams']
            with pd.option_context('display.max_colwidth', -1):
                ps = ptstr.to_string()
            if debugInd == 1: st.write("str(ps) = ", ps)
            if awayTeams[i2] in ps:
                dupTeam = 1
                if debugInd == 1: st.write("in dupTeam assignment")
            else:
                dupTeam = 0
            if re.sub('[^A-Za-z]+', '', awayTeams[i2]) == re.sub('[^A-Za-z]+', '', homeTeams[i2]):
                sameTown = 1
                if debugInd == 1: st.write("in sameTown assignment")
            else:
                sameTown = 0
            if dupTeam == 1 or sameTown == 1:
                endFlag1 = 0
            if i2 < len(awayTeams) and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(i2 + 1, len(awayTeams), i2, 1, 1)
                if debugInd == 1: st.write("After first dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
            ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
            if i2 > 0 and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(0, i2, i2, 1, 1)
                if debugInd == 1: st.write("After second dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
            ###### If we can't get matchups avoiding duplicates and same town matchups, at least avoid duplicates
            if i2 < len(awayTeams) and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(i2 + 1, len(awayTeams), i2, 1, 0)
                if debugInd == 1: st.write("After third dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
            ###### If we've gotten to the end and there is a still a duplicate match, check back at the beginning
            if i2 > 0 and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(0, i2, i2, 1, 0)
                if debugInd == 1: st.write("After fourth dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
            ###### If we still can't avoid duplicates, at least try and avoid match-ups between teams in the same town as a last resort
            if i2 < len(awayTeams) and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(i2 + 1, len(awayTeams), i2, 0, 1)
                if debugInd == 1: st.write("After fifth dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
            ###### If we've gotten to the end and there is a still a same town match-up, check back at the beginning
            if i2 > 0 and endFlag1 == 0:
                endFlag1 = dupSameTownCheckFunc(0, i2, i2, 0, 1)
                if debugInd == 1: st.write("After sixth dupSameTownCheckFunc call and endFlag1 = ", endFlag1)
        teamIndex = 0
        for l in range(startIndex - 1, endIndex):
            leagueSched.loc[l, 'homeTeam'] = homeTeams[teamIndex]
            leagueSched.loc[l, 'awayTeam'] = ""
            if (twnm == 'Have Inter-Town Match-Ups to End the Season (if possible)' and i == schedGames):
                for m in range(0, len(sameTownTeamsHome)):
                    if homeTeams[teamIndex] == sameTownTeamsHome[m]:
                        leagueSched.loc[l, 'awayTeam'] = sameTownTeamsAway[m]
                if leagueSched.loc[l, 'awayTeam'] == "":
                    if (totalTeams % 2 == 1):
                        lat = set([v for v in teamList if v not in byeTeams.values])
                        lat2 = set([v for v in lat if v not in sameTownTeamsAway])
                        lastAwayTemp = list(set([v2 for v2 in lat2 if v2 not in homeTeams]))[0]
                        if debugInd == 1: st.write("lastAwayTemp = ", lastAwayTemp)
                    else:
                        lat = set([v for v in teamList if v not in homeTeams])
                        lastAwayTemp = list(set([v2 for v2 in lat if v2 not in sameTownTeamsAway]))[0]
                        if debugInd == 1: st.write("lastAwayTemp = ", lastAwayTemp)
                    leagueSched.loc[l, 'awayTeam'] = lastAwayTemp
            else:
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
            if ((gameDay - dt.timedelta(days=5)) in us_holidays):
                gameDay = gameDay - dt.timedelta(days=7)
            else:
                gameDay = gameDay - dt.timedelta(days=5)
        elif gameDay.weekday() in range(2, 4):
            if ((gameDay - dt.timedelta(days=2)) in us_holidays):
                gameDay = gameDay - dt.timedelta(days=7)
            else:
                gameDay = gameDay - dt.timedelta(days=2)
        ##### For weekend games, we need an added check to see if the previous Monday is a holiday, making it a holiday weekend
        elif gameDay.weekday() in range(5, 7):
            if ((gameDay - dt.timedelta(days=7)) in us_holidays or (gameDay - dt.timedelta(days=6)) in us_holidays or (
                    gameDay - dt.timedelta(days=5)) in us_holidays):
                gameDay = gameDay - dt.timedelta(days=14)
            else:
                gameDay = gameDay - dt.timedelta(days=7)

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
    st.header(leag + " Team Tracking Summary for " + seas + " Season")
    st.table(teamTrack.style)
    st.header(leag + " Schedule for " + seas + " Season")
    st.table(leagueSched.sort_index())


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
townMatch = st.sidebar.radio('Additional Game Options', [
    'Have Inter-Town Match-Ups to End the Season (if possible)',
    'Create all Match-ups Randomly'])
### Determine if the start date should be calculated
sdCalc = st.sidebar.checkbox("Manually enter the season start date?")
if sdCalc:
    startDay = st.sidebar.date_input("Season Start Date (first game)")
else:
    startDay = ""
### Enter the year
year = st.sidebar.number_input("Enter the Year", 2010, 2100, 2023)
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
if debugInd == 1:
    randomSeed = 10
else:
    randomSeed = random.randint(1, 100)

# Main Panel Design
if schedButton:
    makeSchedule(season, year, league, startDay, numberGames, gameMethod, townMatch, randomSeed)
