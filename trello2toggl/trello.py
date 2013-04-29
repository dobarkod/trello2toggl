import requests

from .jsonobject import JSONObject


class Trello(object):
    """Simple Trello API wrapper"""

    BASE_URL = 'https://api.trello.com/1/'

    def __init__(self, api_key, token):
        """
        Initialize wrapper with application API key and the user access
        token.
        """
        self.api_key = api_key
        self.token = token

    def _get(self, endpoint, **args):
        params = dict(key=self.api_key, token=self.token)
        params.update(args)

        resp = requests.get(self.BASE_URL + endpoint, params=params)
        if resp.status_code != 200:
            raise Exception('Status code is %d' % resp.status_code)
        return JSONObject.parse(resp.json())

    def get_my_organizations(self):
        return self._get('members/me/organizations')

    def get_organization_boards(self, org_id):
        return [b for b in self._get('organizations/%s/boards' % org_id,
            actions='createCard,updateCard', action_limit='1')
            if not b.closed]

    def get_board_cards(self, board_id, status=None):
        return self._get('board/%s/cards/%s' % (board_id,
            status if status in ['open', 'closed'] else ''))

    def get_board_lists(self, board_id):
        return self._get('board/%s/lists' % board_id, cards='open')
