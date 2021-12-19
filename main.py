# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

##########Backlog Items##############
# 1. Fall Season should really start the first Saturday after Labor Day

import datetime as dt
import math
from random import sample
import holidays
import pandas as pd
import streamlit as st

# Title the app
st.title('Softball Scheduling - Metrowest League')
us_holidays = holidays.UnitedStates()

# Function for creating the schedule
def makeSchedule(seas, yr, leag, sd, ng):
  #### First, create the array of team names
  teamList = []
  for i in range(0, len(teams)):
      counter = 1
      for j in range(0, teamCnt[i]):
          teamList.append(teams[i] + " Team #" + str(counter))
          counter = counter + 1
  for value in teamList:
      st.write(value)
  totalTeams = len(teamList)
  #### Next, calculate the start day if it wasn't entered
  if sd == "":
      if seas == "Spring":
          ##### Season starts on the last Monday in April
          firstDay = dt.date(yr, 4, 1)
          wd = firstDay.weekday()
          firstMonday = firstDay + dt.timedelta(days=((7-wd) % 7))
          startDay = firstMonday + dt.timedelta(days=21)
      if seas == "Summer":
          ##### Season starts on the third Thursday in June
          firstDay = dt.date(yr, 6, 1)
          wd = firstDay.weekday()
          firstMonday = firstDay + dt.timedelta(days=((7-wd) % 7))
          firstThursday = firstMonday + dt.timedelta(days=3)
          startDay = firstThursday + dt.timedelta(days=14)
      if seas == "Fall":
          ##### Season starts on the first Saturday in September
          firstDay = dt.date(yr, 9, 1)
          wd = firstDay.weekday()
          firstMonday = firstDay + dt.timedelta(days=((7-wd) % 7))
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
  #### If there's an odd number of teams, an extra week is needed to play the desired number of games for each team
  schedRows = (ng + (totalTeams % 2))*gamesPerGameDay
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
      teamTrack.loc[j, 'playedTeams'] = ''
  #### The Majors generally start the day after the Minors leagues start
  if (leag == 'Majors'):
      gameDay = startDay + dt.timedelta(days=1)
  else:
      gameDay = startDay

  #### sub-function to choose the teams with the least amount of byes
  def byeTeamFunc(teamstoChooseFrom=""):
      if teamstoChooseFrom == "":
          st.write("(In If) Min Byes = ")
          st.write(teamTrack[teamTrack['byeCount'] == min(teamTrack['byeCount'])].team)
          teamswMinByeGames = teamTrack[teamTrack['byeCount'] == min(teamTrack['byeCount'])].team
      else:
          teamswMinByeGames = teamstoChooseFrom
      if (totalTeams % 2 == 1):
          byeTm = teamswMinByeGames.sample(n=1, random_state=1)
      else:
          byeTm = ""
      st.write("byeTeams = " + byeTm)
      return byeTm
  #### End byeTeamFunc function
  #### sub-function to choose the teams who have played the least or highest amount of home games
  def homeGameFunc(teamstoChooseFrom, minOrMax):
      if len(teamstoChooseFrom[teamTrack['homeGames'] == max(teamTrack['homeGames']), 'team']) == totalTeams:
          teamsChosen = teamstoChooseFrom.sample(n=1, random_state=1)
      else:
          if minOrMax == 'min':
              teamsChosen = teamstoChooseFrom[teamTrack['homeGames'] == min(teamTrack['homeGames'])].team
          else:
              teamsChosen = teamstoChooseFrom[teamTrack['homeGames'] == max(teamTrack['homeGames'])].team
      return teamsChosen
  #### End homeGameFunc function

  for i in range(1, (ng + (totalTeams % 2))):
      startIndex = (gamesPerGameDay * (i-1)) + 1
      endIndex = gamesPerGameDay * i
      st.write(startIndex)
      st.write(endIndex)
      for j in range(startIndex, endIndex+1):
          leagueSched.loc[j-1, 'date'] = gameDay
      ##### First, select the bye team, users can not adjust this preference
      byeTeams = byeTeamFunc()
      ##### Second, let's make sure home games are evened out as much as possible when choosing home teams this week

      # Should only be 1 bye team at most
      teamTrack.loc[teamTrack['team'] == byeTeams.values[0], 'byeCount'] += 1

      st.write(leagueSched)
      st.write(teamTrack)

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
          if ((gameDay + dt.timedelta(days=7)) in us_holidays or (gameDay + dt.timedelta(days=8)) in us_holidays or (gameDay + dt.timedelta(days=7)) in us_holidays):
              gameDay = gameDay + dt.timedelta(days=14)
          else:
              gameDay = gameDay + dt.timedelta(days=7)

      ##### Check that home games and byes are even
      if (max(teamTrack['homeGames']) >= (min(teamTrack['homeGames']) + 3)):
          st.error("Error: Home Games are Not Being Evenly Distributed")
      if (max(teamTrack['byeCount']) >= (min(teamTrack['byeCount']) + 2)):
          st.error("Error: Byes are Not Being Evenly Distributed")
  #### End for loop

  st.write(leag + " schedule for " + seas + ", ", yr, ":smile:")
  col1, col2 = st.columns(2)
  col1.write("Here's Column 1")
  col2.write("Here's Column 2")
# End makeSchedule function

# Sidebar Design
st.sidebar.header("Schedule Inputs")
### Pick the season
season = st.sidebar.radio('Select the Season', ['Spring', 'Summer', 'Fall'])
### Select the number of Games
if (season == "Spring"):
    numberGames = st.sidebar.number_input("Enter the Number of Games Each Team Will Play", value=12)
if (season == "Summer"):
    numberGames = st.sidebar.number_input("Enter the Number of Games Each Team Will Play", value=6)
if (season == "Fall"):
    numberGames = st.sidebar.number_input("Enter the Number of Games Each Team Will Play", value=6)
### Determine fit he start date should be calculated
sdCalc = st.sidebar.checkbox("Manually enter the season start date?")
if sdCalc:
    startDay = st.sidebar.date_input("Season Start Date (first game)")
else:
    startDay = ""
### Enter the year
year = st.sidebar.number_input("Enter the Year", 2010, 2100, 2021)
### Select the league
league = st.sidebar.radio('Which League is this for', ['Minors', 'Majors'])
### Set the total number of towns for the for loop
numTeams = st.sidebar.number_input("How many towns are playing?", 1, 50)
### Enter the towns and the number of teams within each town
teams = []
teamCnt = []
teams.append(st.sidebar.text_input("Enter the first town to add to the schedule", ""))
teamCnt.append(st.sidebar.slider("Select the number of teams for town 1", 1, 4))
if numTeams > 1:
    for x in range(1, numTeams):
        teams.append(st.sidebar.text_input(f'Enter the number {x+1:2d} town', ""))
        teamCnt.append(st.sidebar.slider(f'Select the number of teams for town {x+1:2d}', 1, 4))

schedButton = st.sidebar.button("Calculate Schedule")

# Main Panel Design

if schedButton:
    makeSchedule(season, year, league, startDay, numberGames)




