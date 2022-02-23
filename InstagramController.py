from Config import Config
from Database import Database
import requests


class InstagramController:
    BLOGGER_DATA_LINK = "https://www.instagram.com/%s/?__a=1"  # %s - blogger short name
    BLOGGER_STORIES_DATA_LINK = "https://i.instagram.com/api/v1/feed/user/%s/reel_media/"  # %s - blogger id
    BLOGGER_STORIES_USER_AGENT = "Mozilla/5.0 (iPhone; CPU iPhone OS 12_3_1 like Mac OS X) AppleWebKit/605.1.15 (" \
                                 "KHTML, like Gecko) Mobile/15E148 Instagram 105.0.0.11.118 (iPhone11,8; iOS 12_3_1; " \
                                 "en_US; en-US; scale=2.00; 828x1792; 165586599) "

    def __init__(self):
        self.database = Database(Config().get_all_section_parameters('DATABASE'))

    # TEMPORARILY FROZEN AND IDENTICAL BECAUSE USER STORIES CANNOT GET WITHOUT LOGIN
    # I HIGHLY RECOMMEND USING get_blogger_main_info METHOD.
    def get_blogger_info(self, blogger_short_name, blogger_id=None):
        self.get_blogger_main_info(blogger_short_name)

    def get_blogger_id(self, short_name=None, blogger_data=None):
        if short_name is None and blogger_data is None:
            return None

        return (blogger_data
                if blogger_data is not None
                else self.get_blogger_main_info(short_name)
                )['logging_page_id'].replace('profilePage_', '')

    def get_blogger_main_info(self, blogger_short_name):
        result = requests.get(self.BLOGGER_DATA_LINK % blogger_short_name)

        return result.json()

    # WORK ONLY WITH LOGGED IN ACCOUNT.
    # TEMPORARILY FROZEN
    def get_blogger_stories_info(self, blogger_id):
        raise Exception('TEMPORARILY FROZEN')
        result = requests.get(self.BLOGGER_STORIES_DATA_LINK % blogger_id,
                              headers={'User-Agent': self.BLOGGER_STORIES_USER_AGENT})

        print(result.text)

        return result.json()

