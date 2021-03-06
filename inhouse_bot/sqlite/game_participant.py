from sqlalchemy import Column, Integer, ForeignKey, Float, ForeignKeyConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from inhouse_bot.sqlite.player_rating import PlayerRating
from inhouse_bot.sqlite.sqlite_utils import sql_alchemy_base, team_enum, role_enum


class GameParticipant(sql_alchemy_base):
    """Represents a participant in an inhouse game"""

    __tablename__ = "game_participant"

    # Reference to the game table
    game_id = Column(Integer, ForeignKey("game.id"), primary_key=True)

    # Identifier among game participants
    team = Column(team_enum, primary_key=True)
    role = Column(role_enum, primary_key=True)

    # Unique player_id
    player_id = Column(Integer, ForeignKey("player.discord_id"))

    # Player relationship
    player = relationship("Player", viewonly=True)

    # Champion id, only filled if the player updates it by themselves after the game
    champion_id = Column(Integer)

    # Pre-game TrueSkill values
    trueskill_mu = Column(Float)
    trueskill_sigma = Column(Float)

    # Conservative rating for MMR display
    @hybrid_property
    def mmr(self):
        return self.trueskill_mu - 3 * self.trueskill_sigma + 25

    __table_args__ = (
        ForeignKeyConstraint((player_id, role), (PlayerRating.player_id, PlayerRating.role)),
        {},
    )

    def __init__(self, game, team, role, player):
        """
        Should be called only from the game.__init__() function.

        :param game: the parent game object
        :param team: blue/red
        :param role: a role in [top, jungle, mid, bot, support]
        :param player: participant’s player object
        """

        self.game_id = game.id
        self.team = team
        self.role = role
        self.player_id = player.discord_id
        self.trueskill_mu = player.ratings[role].trueskill_mu
        self.trueskill_sigma = player.ratings[role].trueskill_sigma
