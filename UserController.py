from datetime import datetime

import asyncio

from Database import Database
from Config import Config
from FunctionResult import FunctionResult
from InstagramController import InstagramController


class UserController:
    def __init__(self):
        self.database = Database(Config().get_all_section_parameters('DATABASE'))
        self.instagram_controller = InstagramController()

    def create_new_user(self, telegram_id):
        return self.database.add_new_user(telegram_id)

    def subscribe_user(self, telegram_id, blogger_short_name):
        user_tariffs = self.get_active_user_tariffs_and_add_if_not_found(telegram_id)

        max_user_subscriptions_count = self.get_max_user_subscriptions_count(user_tariffs)

        if max_user_subscriptions_count is not None and \
                len(self.get_user_subscriptions(telegram_id)) >= max_user_subscriptions_count:
            return FunctionResult.error('У вас слишком много подписок')

        blogger_data = self.database.search_blogger_in_database(blogger_short_name)

        function_result = FunctionResult.success()

        if blogger_data is None:
            blogger_info = self.instagram_controller.get_blogger_main_info(blogger_short_name)

            if blogger_info == {}:
                return FunctionResult.error('Такого пользователя не существует или его аккаунт закрыт')

            blogger_id = self.instagram_controller.get_blogger_id(blogger_data=blogger_info)

            posts_count = blogger_info['graphql']['user']['edge_owner_to_timeline_media']['count']

            last_post_id = blogger_info['graphql']['user']['edge_owner_to_timeline_media']['edges'][0]['node']['id'] \
                if posts_count != 0 and blogger_info['graphql']['user']['edge_owner_to_timeline_media']['edges'] != [] \
                else 0

            try:
                last_story_id = self.instagram_controller.get_last_blogger_story_id_from_data(
                    self.instagram_controller.get_blogger_stories(blogger_id)
                )
            except asyncio.TimeoutError:
                function_result.error('Не удалось получить доступ к историям пользователя. ')
                last_story_id = 0

            try:
                raw_reels_data = self.instagram_controller.get_blogger_reels(blogger_id)
            except asyncio.TimeoutError:
                function_result.error(
                    function_result.errorMessage + 'Не удалось получить доступ к reels пользователя. ')
                raw_reels_data = {'tray': []}

            reels_data = {}

            for reel in raw_reels_data['tray']:
                reels_data[
                    self.instagram_controller.get_reel_album_id(reel)
                ] = reel['latest_reel_media']

            blogger_data = [
                self.instagram_controller.get_blogger_id(blogger_data=blogger_info),
                blogger_short_name,
                posts_count,
                last_post_id,
                last_story_id,
                reels_data
            ]
            self.database.add_new_blogger(blogger_data)

        user_subscription = self.database.subscribe_user(telegram_id, blogger_data[0])

        if not function_result.isSuccess:
            function_result.error(
                function_result.errorMessage + 'Однако нам удалось подписать Вас на пользователя. '
                                               'Вам придёт сообщение, когда мы сможем получить доступ к недоступной '
                                               'на данный момент информации')
            return function_result

        return FunctionResult.success(blogger_short_name) \
            if user_subscription.isSuccess \
            else user_subscription

    def get_active_user_tariffs_and_add_if_not_found(self, telegram_id):
        user_tariffs = self.get_active_user_tariffs(telegram_id)

        if not user_tariffs:
            self.add_tariff_to_user(1, telegram_id)

            user_tariffs = self.get_active_user_tariffs(telegram_id)

        return user_tariffs

    def get_max_user_subscriptions_count(self, tariffs):
        subscriptions_count = tariffs[0][4]

        for tariff in tariffs:
            if tariff[4] is None:
                return None

            if tariff[4] > subscriptions_count:
                subscriptions_count = tariff[4]

        return subscriptions_count

    def get_active_user_tariffs(self, telegram_id):
        return self.database.get_valid_user_tariffs(telegram_id)

    def get_user_tariffs(self, telegram_id):
        return self.database.get_user_tariffs(telegram_id)

    def get_user_subscriptions(self, telegram_id):
        return self.database.get_user_subscriptions(telegram_id)

    def add_tariff_to_user(self, tariff_id, telegram_id, started_at=datetime.now()):
        self.database.add_tariff_to_user(tariff_id, telegram_id, started_at)

    def unsubscribe_user(self, telegram_id, blogger_id):
        return self.database.unsubscribe_user(telegram_id, blogger_id)
