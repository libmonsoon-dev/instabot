from modules.settings import user_params, main_params
from modules.logger import debug_wrapper
from modules.api import InstagramAPI


@debug_wrapper
def main():
    api = InstagramAPI(**user_params, **main_params)
    api.login()
    api.main_loop()
    api.close()


if __name__ == '__main__':
    main()
