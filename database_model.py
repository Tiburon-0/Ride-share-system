from database_manager import execute_query

class DatabaseModel:
    '''Mini-ORM base class; Subclasses must define table_name, _to_dict(), and _from_dict()'''

    table_name = None  # Override in each subclass

    # ──────────────────────────────────────────────
    # Write operations
    # ──────────────────────────────────────────────

    def save(self):
        '''Insert or replace this object in the database'''

        data = self._to_dict()                              # get column->value mapping
        columns = ", ".join(data.keys())                    # "id, name, rating_avg, ..."
        placeholders = ", ".join(["?" for _ in data])       # "?, ?, ?, ..."
        sql = f"INSERT OR REPLACE INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        execute_query(sql, tuple(data.values()))

    # ──────────────────────────────────────────────
    # Read operations
    # ──────────────────────────────────────────────

    @classmethod
    def get(cls, record_id):
        '''Return one object by primary key, or None if not found'''

        sql = f"SELECT * FROM {cls.table_name} WHERE id = ?"
        rows = execute_query(sql, (record_id,), fetch=True)
        if rows:
            return cls._from_dict(rows[0])
        return None

    @classmethod
    def all(cls):
        '''Return all rows as a list of objects'''
        rows = execute_query(f"SELECT * FROM {cls.table_name}", fetch=True)
        return [cls._from_dict(row) for row in rows]

    @classmethod
    def filter(cls, **conditions):
        '''Return all rows matching the given column=value conditions
        Example: Rider.filter(name="Alice")'''
        
        where_clause = " AND ".join([f"{k} = ?" for k in conditions])
        sql = f"SELECT * FROM {cls.table_name} WHERE {where_clause}"
        rows = execute_query(sql, tuple(conditions.values()), fetch=True)
        return [cls._from_dict(row) for row in rows]

    # ──────────────────────────────────────────────
    # Subclasses must implement these
    # ──────────────────────────────────────────────

    def _to_dict(self):
        '''Map instance attributes to a column -> value dict for INSERT. Override in subclass'''
        raise NotImplementedError(f"{self.__class__.__name__} must implement _to_dict()")

    @classmethod
    def _from_dict(cls, row):
        '''Rebuild an object from a database row dict. Override in subclass'''
        raise NotImplementedError(f"{cls.__name__} must implement _from_dict()")
