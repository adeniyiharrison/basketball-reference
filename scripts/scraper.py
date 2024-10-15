import sys
import logging
import requests
import pandas as pd
from http import HTTPStatus
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Scraper:
    """Scraper class"""

    def __init__(self, startDate, endDate):
        startDateObj = datetime.strptime(startDate, "%Y-%m-%d").date()
        endDateObj = datetime.strptime(endDate, "%Y-%m-%d").date()
        if endDateObj < startDateObj:
            raise ValueError(
                f"end date ({endDate}) cannot be earlier than start date ({startDate})"
            )

        self.startDate = startDateObj
        self.endDate = endDateObj
        self.scoreEndpoint = "https://www.basketball-reference.com/boxscores/index.fcgi?month={month}&day={day}&year={year}"

    def retreiveScoreData(self, currentDate: datetime):

        url = self.scoreEndpoint.format(
            month=currentDate.month,
            day=currentDate.day,
            year=currentDate.year
        )

        response = requests.get(url)

        if response.status_code != HTTPStatus.OK:
            logging.error(f"Failed to retrieve data for {url}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, "html.parser")
        gameSummaries = soup.find("div", class_="game_summaries")
        gameSummariesExpanded = gameSummaries.find_all("div", class_="game_summary expanded nohover")

        scoresDf = instantiateScoreDataFrame()
        for gameSummary in gameSummariesExpanded:
            scores = gameSummary.find_all("tr", class_=["winner", "loser"])
            if len(scores) != 2:
                logging.error(f"Unexpected number of scores for game: {url}")
                continue

            scoreDf = instantiateScoreDataFrame()
            for index, score in enumerate(scores):
                teamAndScore = score.text.strip().split("\n")
                if len(teamAndScore) < 2:
                    logging.error(f"Invalid team and score: {teamAndScore}")
                    continue
                if index == 0:
                    scoreDf["away_team"] = teamAndScore[0]
                    scoreDf["final_score_away"] = teamAndScore[1]
                    if score["class"][0] == "winner":
                        scoreDf["winner"] = teamAndScore[0]
                else:
                    scoreDf["home_team"] = teamAndScore[0]
                    scoreDf["final_score_home"] = teamAndScore[1]
                    if score["class"][0] == "winner":
                        scoreDf["winner"] = teamAndScore[0]
            scoresDf = pd.concat([scoresDf, scoreDf.iloc[[0]]])
            # quarterScores = gameSummary.find_all("td", class_="center")
        print("done for the day")


            


    def run(self):
        currentDate = self.startDate
        while currentDate <= self.endDate:
            logging.debug(currentDate.strftime("%Y-%m-%d"))
            self.retreiveScoreData(currentDate)
            currentDate += timedelta(days=1)

def instantiateScoreDataFrame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            # "date": pd.Series(dtype="datetime"),
            "home_team": pd.Series(dtype="str"),
            "away_team": pd.Series(dtype="str"),
            "winner": pd.Series(dtype="str"),
            "final_score_home": pd.Series(dtype="int"),
            "final_score_away": pd.Series(dtype="int"),
            "h1": pd.Series(dtype="int"),
            "a1": pd.Series(dtype="int"),
            "h2": pd.Series(dtype="int"),
            "a2": pd.Series(dtype="int"),
            "h3": pd.Series(dtype="int"),
            "a3": pd.Series(dtype="int"),
            "h4": pd.Series(dtype="int"),
            "a4": pd.Series(dtype="int"),
            "hot": pd.Series(dtype="int"),
            "aot": pd.Series(dtype="int"),
        }
    )

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(message)s"
    )
    kwargs = dict(arg.split("=") for arg in sys.argv[1:])
    startDate = kwargs["start_date"]
    endDate = kwargs["end_date"]

    scraper = Scraper(startDate, endDate)
    scraper.run()