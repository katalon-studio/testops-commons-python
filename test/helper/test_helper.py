from os import path
from testops_commons.model.models import Error, TestResult, Status
from testops_commons.helper.helper import *
from testops_commons.core.constants import *


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


def test_write_json():
    test_result = TestResult(
        uuid='cf9f5503-e4fe-4c7b-89f7-bd1255b1f665',
        parent_uuid='e5d1265b-b559-4b43-9b80-d21f90c4c403',
        name='com.katalon.testops.CalculatorDivideByZeroTestNGTest.divideByZeroFailed',
        suite_name='Calculator Suite (parallel)',
        parameters={},
        status=Status.FAILED,
        errors=[Error(message='com.katalon.testops.CalculatorDivideByZeroTestNGTest.divideByZeroIncomplete', stack_trace='org.testng.SkipException: Skipping divideByZeroIncomplete\r\n\tat com.katalon.testops.CalculatorDivideByZeroTestNGTest.divideByZeroIncomplete(CalculatorDivideByZeroTestNGTest.java:28)\r\n\tat sun.reflect.NativeMethodAccessorImpl.invoke0(Native Method)\r\n\tat sun.reflect.NativeMethodAccessorImpl.invoke(NativeMethodAccessorImpl.java:62)\r\n\tat sun.reflect.DelegatingMethodAccessorImpl.invoke(DelegatingMethodAccessorImpl.java:43)\r\n\tat java.lang.reflect.Method.invoke(Method.java:498)\r\n\tat org.testng.internal.MethodInvocationHelper.invokeMethod(MethodInvocationHelper.java:132)\r\n\tat org.testng.internal.TestInvoker.invokeMethod(TestInvoker.java:599)\r\n\tat org.testng.internal.TestInvoker.invokeTestMethod(TestInvoker.java:174)\r\n\tat org.testng.internal.MethodRunner.runInSequence(MethodRunner.java:46)\r\n\tat org.testng.internal.TestInvoker$MethodInvocationAgent.invoke(TestInvoker.java:822)\r\n\tat org.testng.internal.TestInvoker.invokeTestMethods(TestInvoker.java:147)\r\n\tat org.testng.internal.TestMethodWorker.invokeTestMethods(TestMethodWorker.java:146)\r\n\tat org.testng.internal.TestMethodWorker.run(TestMethodWorker.java:128)\r\n\tat java.util.ArrayList.forEach(ArrayList.java:1257)\r\n\tat org.testng.TestRunner.privateRun(TestRunner.java:764)\r\n\tat org.testng.TestRunner.run(TestRunner.java:585)\r\n\tat org.testng.SuiteRunner.runTest(SuiteRunner.java:384)\r\n\tat org.testng.SuiteRunner.access$000(SuiteRunner.java:28)\r\n\tat org.testng.SuiteRunner$SuiteWorker.run(SuiteRunner.java:425)\r\n\tat org.testng.internal.thread.ThreadUtil.lambda$execute$0(ThreadUtil.java:66)\r\n\tat java.util.concurrent.FutureTask.run$$$capture(FutureTask.java:266)\r\n\tat java.util.concurrent.FutureTask.run(FutureTask.java)\r\n\tat java.util.concurrent.ThreadPoolExecutor.runWorker(ThreadPoolExecutor.java:1149)\r\n\tat java.util.concurrent.ThreadPoolExecutor$Worker.run(ThreadPoolExecutor.java:624)\r\n\tat java.lang.Thread.run(Thread.java:748)\r\n')],
        description='',
        start=1608285803652,
        stop=1608285803654,
        duration=4,
    )
    expected_file_path = path.join(path.dirname(__file__), 'expected_result.json')
    actual_file_path = path.join(path.dirname(__file__), 'result.json')

    write_json(test_result, actual_file_path)

    actual = read_json(actual_file_path)
    expected = read_json(expected_file_path)
    assert actual == expected
