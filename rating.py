from datetime import datetime
from database_model import DatabaseModel
from database_manager import execute_query


class Rating(DatabaseModel):
    '''Stores one rating event — either rider→driver or driver→rider'''

    table_name = "ratings"

    def __init__(self, trip_id, rater_type, rater_id,
                 ratee_type, ratee_id, stars, comment="", timestamp=None):
        self.trip_id    = trip_id
        self.rater_type = rater_type    # "rider" or "driver"
        self.rater_id   = rater_id
        self.ratee_type = ratee_type
        self.ratee_id   = ratee_id
        self.stars      = stars
        self.comment    = comment
        self.timestamp  = timestamp or datetime.now().isoformat()

    def save(self):
        '''Insert this rating into the ratings table'''

        data = self._to_dict()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        execute_query(sql, tuple(data.values()))

    def _to_dict(self):
        '''Map rating fields to the ratings table columns'''

        return {
            "trip_id":    self.trip_id,
            "rater_type": self.rater_type,
            "rater_id":   self.rater_id,
            "ratee_type": self.ratee_type,
            "ratee_id":   self.ratee_id,
            "stars":      self.stars,
            "comment":    self.comment,
            "timestamp":  self.timestamp
        }

    @classmethod
    def _from_dict(cls, row):
        '''Rebuild a Rating object from a DB row'''
        
        r = cls(
            trip_id    = row["trip_id"],
            rater_type = row["rater_type"],
            rater_id   = row["rater_id"],
            ratee_type = row["ratee_type"],
            ratee_id   = row["ratee_id"],
            stars      = row["stars"],
            comment    = row["comment"] or "",
            timestamp  = row["timestamp"]
        )
        return r

    def __str__(self):
        return (f"[Rating] {self.rater_type}:{self.rater_id} -> "
                f"{self.ratee_type}:{self.ratee_id} | {self.stars} stars | Trip:{self.trip_id}")
