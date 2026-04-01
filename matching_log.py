import json
from datetime import datetime
from database_model import DatabaseModel
from database_manager import execute_query


class MatchingLog(DatabaseModel):
    '''Records every driver-selection decision — algorithm used, candidates considered, driver chosen'''

    table_name = "matching_logs"

    def __init__(self, rider_id, algorithm, graph_model,
                 candidate_drivers, distances,
                 chosen_driver_id, chosen_distance, timestamp=None):
        self.rider_id = rider_id
        self.algorithm = algorithm          # "weighted" or "unweighted"
        self.graph_model = graph_model        # e.g. "barabasi_albert"
        self.candidate_drivers = candidate_drivers  # list of driver IDs considered
        self.distances = distances          # list of corresponding distances
        self.chosen_driver_id = chosen_driver_id
        self.chosen_distance = chosen_distance
        self.timestamp = timestamp or datetime.now().isoformat()
        self.db_id = None               # set after save()

    def save(self):
        '''Insert and capture the auto-generated db_id for use as a Trip foreign key'''

        data = self._to_dict()
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.db_id = execute_query(sql, tuple(data.values()))
        return self.db_id

    def _to_dict(self):
        '''Serialize to column dict — candidate_drivers and distances encoded as JSON strings'''

        return {
            "rider_id":          self.rider_id,
            "algorithm":         self.algorithm,
            "graph_model":       self.graph_model,

            # list → JSON string
            "candidate_drivers": json.dumps(self.candidate_drivers),

            # list → JSON string
            "distances":         json.dumps(self.distances),
            "chosen_driver_id":  self.chosen_driver_id,
            "chosen_distance":   self.chosen_distance,
            "timestamp":         self.timestamp
        }

    @classmethod
    def _from_dict(cls, row):
        '''Rebuild a MatchingLog from a DB row, decoding JSON list fields'''
        
        log = cls(
            rider_id=row["rider_id"],
            algorithm=row["algorithm"],
            graph_model=row["graph_model"],
            candidate_drivers=json.loads(row["candidate_drivers"] or "[]"),
            distances=json.loads(row["distances"] or "[]"),
            chosen_driver_id=row["chosen_driver_id"],
            chosen_distance=row["chosen_distance"],
            timestamp=row["timestamp"]
        )
        log.db_id = row["id"]
        return log

    def __str__(self):
        return (f"[MatchingLog #{self.db_id}] Rider:{self.rider_id} | "
                f"Algorithm:{self.algorithm} | "
                f"Chosen:{self.chosen_driver_id} @ {self.chosen_distance:.2f}")
