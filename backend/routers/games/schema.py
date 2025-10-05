from ninja import Schema

class GameOut(Schema):
    id: int
    name: str
    summary: str
    igdb_game_id: int
