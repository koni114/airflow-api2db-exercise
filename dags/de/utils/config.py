import os
import sys
from argparse import ArgumentParser

from de.utils.io import read_file, read_yaml
from de.utils.common import AppInfo, host_name, MultiDictContainer
from de.utils.logger import create_logger, INFO, MORE, DETAIL, WARNING, ERROR, set_logging_level

app_info = AppInfo(app_dir=os.getcwd())

base_dir = app_info.app_dir()
app_name = app_info.app_name()
host_name_str = host_name()

default_prop_dir = os.path.join(base_dir, "default_properties")  # 공통
default_conn_prop_file = os.path.join(default_prop_dir, "conn_properties.yaml")
default_app_prop_file = os.path.join(default_prop_dir, "app_properties.yaml")

# 개별 테스트 시, root directory 에 해당 스크립트가 있으면 기존 config 에 덮어 씀
prop_dir = base_dir
conn_prop_file = os.path.join(prop_dir, "conn_properties.yaml")
app_prop_file = os.path.join(prop_dir, "app_properties.yaml")

# log file config setting
# app_name.log file 에 logging
log_dir = os.path.join(base_dir, "logs")
log_file = os.path.join(log_dir, f"{app_name}.log")
logger = create_logger(log_file)

# 현재 환경 정보 setting -> 실행 환경: dev(개발환경), test(테스트환경), prod(운영환경)
EXECUTE_ENV = os.getenv("EXECUTE_ENV", "prod")  # 실행 환경: dev(개발환경), test(테스트환경), prod(운영환경)


def load_yaml(config_file):
    """
        Return the yaml file in the config_file location as a MultiDictContainer object.
    :param config_file:
                app_properties.yaml,
                conn_properties.yaml 중 하나
    :return:
    """
    properties = MultiDictContainer({})
    if os.path.exists(config_file):
        dic = read_file(config_file, data_type="yaml")
        if dic is not None:
            properties = MultiDictContainer(dic)
        return properties


def _extend_args_conf(args_parser: ArgumentParser, args_conf):
    """
        Add dict type args value to argument
    """
    for arg_conf in args_conf:
        arg = arg_conf['arg']
        del arg_conf['arg']
        args_parser.add_argument(*arg, **arg_conf)


class DefaultConfig(object):
    logger.log(INFO, "load default config ")

    # db connection 기본 설정 가져오기
    __ALL_CONN_INFO_TMP = read_yaml(path=default_conn_prop_file)

    # 사용자 설정 가져오기
    __ALL_CONN_INFO_TMP.merge(read_yaml(conn_prop_file))

    ALL_CONN_INFO = __ALL_CONN_INFO_TMP['instork_conn_infos']
    logger.logc(DETAIL, f"ALL_CONN_INFO --> {repr(ALL_CONN_INFO)}")

    # app 설정 파일 로딩
    APP_PROPERTIES = load_yaml(default_app_prop_file)
    APP_PROPERTIES.merge(app_prop_file)

    # pytest 실행시, input_args_parser 미실행
    if sys.argv[0].endswith("pytest"):
        ARGS = MultiDictContainer({})

    set_logging_level(logging_level=APP_PROPERTIES.logging_level)

    logger.logc(MORE, f"conn properties --> {ALL_CONN_INFO}")
    logger.logc(MORE, f"app properties -->  {APP_PROPERTIES}")

# 향후 개발, 테스트, 운영 환경별 다르게 셋팅이 추가 필요한 경우, class 에 선언!

class DevelopmentConfig(DefaultConfig):
    pass


class TestingConfig(DefaultConfig):
    pass


class ProductionConfig(DefaultConfig):
    pass


config_by_name = dict(
    dev=DevelopmentConfig,
    test=TestingConfig,
    prod=ProductionConfig
)

config = config_by_name[EXECUTE_ENV]  # 실행환경 기준의 config 값
