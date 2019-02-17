import logging

from environs import Env
from marshmallow.validate import OneOf

MODES = ['unfollow']


def get_logging_level_by_name(name: str) -> int:
    return logging.getLevelName(name)


env = Env()
env.read_env()

with env.prefixed('INSTABOT_'):

    main_params = dict(
        mode=env.str(
            name='MODE',
            default='unfollow',
            validate=OneOf(
                choices=['unfollow'],
                error="INSTABOT_MODE must be one of: {choices}"
            )
        ),

        limit=env.int(
            name='REQUESTS_LIMIT',
            default=1000
        ),

        requests_interval=env.float(
            name='REQUESTS_INTERVAL',
            default=30
        ),

        ajax_header=env.str(
            name='AJAX_HEADER',
            default='33a6d878c17d'
        ),

        random_intervals=env.bool(
            name='RANDOM_INTERVALS',
            default=False
        ),

        on_error_interval=env.float(
            name='ON_ERROR_INTERVAL',
            default=120
        )
    )

    with env.prefixed('USER_'):
        user_params = dict(
            username=env.str(
                name='NAME'
            ),
            password=env.str(
                name='PASS'
            ),
            query_hash=env.str(
                name='QUERY_HASH'
            )
        )

    with env.prefixed('LOGGING_'):

        logger_settings = dict(
            format=env.str(
                name='FORMAT',
                default='[%(asctime)s]\t%(levelname)s\t%(filename)s:%(lineno)d\t%(message)s'
            ),

            level=get_logging_level_by_name(env.str(
                name="LEVEL",
                default="INFO",
                validate=OneOf(
                    choices=logging._levelToName.values(),
                    error="LOGGING_LEVEL must be one of: {choices}"
                )
            ))
        )
