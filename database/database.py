"""API for a sql database which contains averages for letter pairs"""
import sqlite3

# init database
conn = sqlite3.connect('../Cube/cube_data.db')
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS edges_cycle_averages (
    pair text,
    average float
)""")


def find_pair(table, pair):
    with conn:
        cursor.execute(f"SELECT * FROM {table} WHERE pair= :pair ", {'pair': pair})
    return cursor.fetchone()


def insert_pair(table, pair, average) -> bool:
    was_inserted = False
    if find_pair(table, pair) is None:
        was_inserted = True
        with conn:
            cursor.execute(f"INSERT INTO {table} VALUES (:pair, :average)",
                           {'pair': pair, 'average': average})
    if not was_inserted:
        set_average(table, pair, average)
    return was_inserted


def set_average(table, pair, average):
    with conn:
        cursor.execute(f"UPDATE {table} SET average = :average WHERE pair= :pair",
                       {'average': average, 'pair': pair})


def get_all(table='edges_cycle_averages'):
    with conn:
        cursor.execute(f"SELECT * FROM {table}")

    return dict(cursor.fetchall())


curr_table = 'edges_cycle_averages'
set_average(curr_table, 'QQ', 1.5)

# print(get_all(curr_table))
