import os
import logging
import psycopg
import requests
import scores as ScoresPkg
from http import HTTPStatus
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Scraper:
    """Scraper class"""

    def __init__(self):

        startDate = os.getenv("SCRAPE_START_DATE")
        if startDate is None:
            logging.error("SCRAPE_START_DATE environment variable not set")
            exit(1)

        endDate = os.getenv("SCRAPE_END_DATE")
        if endDate is None:
            endDate = startDate

        startDateObj = datetime.strptime(startDate, "%Y-%m-%d").date()
        endDateObj = datetime.strptime(endDate, "%Y-%m-%d").date()
        if endDateObj < startDateObj:
            raise ValueError(
                f"end date ({endDate}) cannot be earlier than start date ({startDate})"
            )

        self.startDate = startDateObj
        self.endDate = endDateObj
        self.scoreEndpoint = "https://www.basketball-reference.com/boxscores/index.fcgi?month={month}&day={day}&year={year}"

        psqlURL = os.getenv("PSQL_URL")
        if psqlURL is None:
            logging.error("PSQL_URL environment variable not set")
            exit(1)
        self.psqlObj = psycopg.connect(conninfo=psqlURL)


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

        scores = []
        for gameSummary in gameSummariesExpanded:
            scoreRows = gameSummary.find_all("tr", class_=["winner", "loser"])
            if len(scoreRows) != 2:
                logging.error(f"Unexpected number of scores for game: {url}")
                continue

            for index, score in enumerate(scoreRows):
                if index == 0:
                    awayTeam = score.a.text
                    finalScoreAway = int(score.find("td", class_="right").text)
                else:
                    homeTeam = score.a.text
                    finalScoreHome = int(score.find("td", class_="right").text)
            
            quarterScores = gameSummary.find_all("td", class_="center")
            if len(quarterScores) == 8:
                a1 = int(quarterScores[0].text)
                a2 = int(quarterScores[1].text)
                a3 = int(quarterScores[2].text)
                a4 = int(quarterScores[3].text)
                h1 = int(quarterScores[4].text)
                h2 = int(quarterScores[5].text)
                h3 = int(quarterScores[6].text)
                h4 = int(quarterScores[7].text)
                hot = 0
                aot = 0
            elif len(quarterScores) == 10:
                a1 = int(quarterScores[0].text)
                a2 = int(quarterScores[1].text)
                a3 = int(quarterScores[2].text)
                a4 = int(quarterScores[3].text)
                aot = int(quarterScores[4].text)
                h1 = int(quarterScores[5].text)
                h2 = int(quarterScores[6].text)
                h3 = int(quarterScores[7].text)
                h4 = int(quarterScores[8].text)
                hot = int(quarterScores[9].text)
            else:
                logging.error(f"TODO: handle double OT // or unexpected number of quarters {url}")
                continue

            scoreObj = ScoresPkg.Score(
                currentDate,
                homeTeam,
                awayTeam,
                finalScoreHome,
                finalScoreAway,
                h1,
                a1,
                h2,
                a2,
                h3,
                a3,
                h4,
                a4,
                hot,
                aot
            )
            scores.append(scoreObj)

        # scoresDF = ScoresPkg.ScoresToDataFrame(scores)
        logging.debug(
            "{totalScores} games played on {currentDate}".format(
                totalScores=len(scores),
                currentDate=currentDate.strftime("%m/%d/%Y")
            )
        )
        self.upsertScores(scores)

    def upsertScores(self, scores: list[ScoresPkg.Score]):
        with self.psqlObj as conn:
            with conn.cursor() as cursor:
                for score in scores:
                    cursor.execute(score.returnUpsertSql())
                    if cursor.rowcount == 0:
                        logging.debug(
                            f"No rows affected by upsert for {score.date} {score.homeTeam} vs {score.awayTeam}"
                        )
            conn.commit()
        logging.info(f"Successfully inserted/updated {len(scores)} scores")

    def run(self):
        currentDate = self.startDate
        while currentDate <= self.endDate:
            logging.debug(currentDate.strftime("%Y-%m-%d"))
            self.retreiveScoreData(currentDate)
            currentDate += timedelta(days=1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(message)s"
    )
        
    scraper = Scraper()
    scraper.run()