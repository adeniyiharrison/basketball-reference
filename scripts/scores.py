import pandas as pd
from datetime import datetime

class Score:
    def __init__(
        self,
        date: datetime.date,
        homeTeam: str,
        awayTeam: str,
        finalScoreHome: int,
        finalScoreAway: int,
        h1: int,
        a1: int,
        h2: int,
        a2: int,
        h3: int,
        a3: int,
        h4: int,
        a4: int,
        hOT: int,
        aOT: int
    ):
        
        winner = awayTeam
        if finalScoreHome > finalScoreAway:
            winner = homeTeam

        self.date = date,
        self.homeTeam = homeTeam
        self.awayTeam = awayTeam
        self.winner = winner
        self.finalScoreHome = finalScoreHome
        self.finalScoreAway = finalScoreAway
        self.h1 = h1
        self.a1 = a1
        self.h2 = h2
        self.a2 = a2
        self.h3 = h3
        self.a3 = a3
        self.h4 = h4
        self.a4 = a4
        self.hOT = hOT
        self.aOT = aOT

    def toDataFrame(self) -> pd.DataFrame:
        data = {
            "date": self.date,
            "home_team": self.homeTeam,
            "away_team": self.awayTeam,
            "winner": self.winner,
            "final_score_home": self.finalScoreHome,
            "final_score_away": self.finalScoreAway,
            "h1": self.h1,
            "a1": self.a1,
            "h2": self.h2,
            "a2": self.a2,
            "h3": self.h3,
            "a3": self.a3,
            "h4": self.h4,
            "a4": self.a4,
            "hot": self.hOT,
            "aot": self.aOT
        }

        return pd.DataFrame(data=data)
    
def ScoresToDataFrame(scores: list[Score]):
    data = [
        {
            "date": score.date,
            "home_team": score.homeTeam,
            "away_team": score.awayTeam,
            "winner": score.winner,
            "final_score_home": score.finalScoreHome,
            "final_score_away": score.finalScoreAway,
            "h1": score.h1,
            "a1": score.a1,
            "h2": score.h2,
            "a2": score.a2,
            "h3": score.h3,
            "a3": score.a3,
            "h4": score.h4,
            "a4": score.a4,
            "hot": score.hOT,
            "aot": score.aOT
        } 
        for score in scores
    ]
    return pd.DataFrame(data=data)