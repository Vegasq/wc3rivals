import json
from wc3rivals.utils import db
from wc3rivals.utils import utils


class NotablePlayers:
    def __init__(self):
        # Read list of predefined players
        self.players = db.NotablePlayersDB().get_players()
        # Access to all games in DB (do not specify gateway)
        self.history_db = db.DBHistory('')
    
    def _get_all_games_played(self, player):
        return [g for g in self.history_db.get_solo_history_all_time(player)]
    
    def _get_total_wins(self, player, games):
        wins = 0
        for game in games:
            user_data = [
                pd for pd in game['players_data']
                if pd['username'].lower() == player.lower()][0]

            if user_data['result'].lower() == 'win':
                wins += 1
        return wins
    
    def _get_kdr(self, wins, loses):
            if loses != 0:
                return round(wins/loses, 1)
            else:
                return '100% WINRATE'

    def _get_race(self, player, games):
        for game in games:
            user_data = [
                pd for pd in game['players_data']
                if pd['username'].lower() == player.lower()][0]
            return utils.detect_race(user_data['race'])

    def _prepare_response(self):
        for player in self.players:
            # Set GW for current player
            self.history_db.set_gateway(utils.GATEWAY_MAP[player['gateway']])
            played_games = self._get_all_games_played(player['account'])

            player['total_games'] = len(played_games)

            wins = self._get_total_wins(player['account'], played_games)
            loses = player['total_games'] - wins
            player['kdr'] = self._get_kdr(wins, loses)

            player['race'] = self._get_race(player['account'], played_games)
        return self.players

    def generate_response(self):
        return json.dumps(self._prepare_response())
