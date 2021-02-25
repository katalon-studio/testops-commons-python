from testops_commons.katalon.testops.commons.helper.helper import *
from testops_commons.katalon.testops.commons.core.constants import *


def test_generate_unique_value():
    actual = generate_unique_value()
    print(actual)
    assert actual is not None
    assert len(actual) > 16


def test_generate_upload_batch():
    actual = generate_upload_batch()
    print(actual)
    assert actual is not None


def test_is_blank():
    assert is_blank('') is True
    assert is_blank(' ') is True
    assert is_blank('  ') is True
    assert is_blank('  \n  ') is True
    assert is_blank('\n') is True
    assert is_blank('\t') is True
    assert is_blank(None) is True
    assert is_blank('a') is False
    assert is_blank(' a ') is False


def test_current_time_millis():
    actual = current_time_millis()
    print(actual)
    assert actual is not None
    assert actual > 1_000_000_000_000


def test_current_thread_name():
    actual = current_thread_name()
    print(actual)
    assert actual is not None
    assert len(actual) > 1


def test_host_name():
    actual = host_name()
    assert actual is not None
    assert len(actual) > 1


def test_read_json():
    actual = read_json(CONFIG_FILE)
    print(actual)
    assert actual is not None


def test_ConfigLoader():
    actual = ConfigurationHelper()
    print(vars(actual))
    print(actual.get('proxy'))
    assert actual.basePath is not None
    assert actual.apiKey is not None
    assert actual.proxy.protocol is not None
    assert actual.PATH is not None
    assert actual.abc is None

def test_ConfigLoader_get_config():
    absent_name = 'dummy_name'
    absent_env_name = 'DUMMY_ENV'
    name = TESTOPS_PROXY_SERVER_TYPE
    env_name = 'PATH'
    default = 123

    conf = ConfigurationHelper()
    assert is_blank(conf.get_config(absent_name, env_name=absent_env_name))
    assert conf.get_config(absent_name, env_name=absent_env_name, default=default) == default
    assert not is_blank(conf.get_config(absent_name, env_name=env_name))
    env_value = conf.get_config(absent_name, env_name=env_name)
    assert conf.get_config(absent_name, env_name=env_name, default=default) == env_value

    assert not is_blank(conf.get_config(name, env_name=absent_env_name))
    name_value = conf.get_config(name, env_name=absent_env_name)
    assert conf.get_config(name, env_name=absent_env_name, default=default) == name_value
    assert conf.get_config(name, env_name=env_name) == env_value
    assert conf.get_config(name, env_name=env_name, default=default) == env_value
    
