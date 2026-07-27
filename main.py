from jarvis.envfile import load_env_file

load_env_file()

from jarvis.app import main  # noqa: E402 - must run after load_env_file()


if __name__ == "__main__":
    main()
