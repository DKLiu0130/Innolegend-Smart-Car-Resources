import configparser
def load_config(config_file='config.ini'):
    """
    从指定的 .ini 文件加载配置。
    如果文件不存在或为空，则程序会退出。
    """
    config = configparser.ConfigParser()
    if not config.read(config_file, encoding='utf-8'):
        print(f"错误: 找不到配置文件 '{config_file}' 或文件为空。")
        print("请确保一个有效的 config.ini 文件与此脚本位于同一目录中。")
        sys.exit()
    return config
