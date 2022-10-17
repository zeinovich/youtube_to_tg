import psycopg2

class Cursor(psycopg2.extensions.cursor):
    def __init__(self, conn):
        super().__init__(conn)

    def insert(self, columns: list, values: list, table: str):
        sql = f'''INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)});'''
        self.execute(sql)

    def select(self, columns: list, table: str, where: str = None):
        sql = f'''SELECT {', '.join(columns)} FROM {table}'''
        if where:
            sql += f' WHERE {where}'
        self.execute(sql)
        return self.fetchall()

    def update(self, table: str, set: str, where: str):
        sql = f'''UPDATE {table} SET {set} WHERE {where};'''
        self.execute(sql)
    
    def delete(self, table: str, where: str):
        sql = f'''DELETE FROM {table} WHERE {where};'''
        self.execute(sql)

    def drop(self, table: str):
        sql = f'''DROP TABLE {table};'''
        self.execute(sql)

    def create(self, table: str, columns: list, types: list):
        sql = f'''CREATE TABLE IF NOT EXISTS {table} ({', '.join([f'{col} {typ}' for col, typ in zip(columns, types)])});'''
        self.execute(sql)

    def check_exists(self, table: str, video_id: str):
        sql = f'''SELECT EXISTS(SELECT 1 FROM {table} WHERE video_id = '{video_id}');'''
        self.execute(sql)
        return self.fetchone()[0]