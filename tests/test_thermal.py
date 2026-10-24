import threading
from types import SimpleNamespace
from urllib.error import URLError
from unittest.mock import Mock, patch

import pytest
from llm_lab.thermal import thermal_violation, guarded_run, GuardAbort, ServiceStopper, check_guard

COOL = {'cpu_temp_c':52,'gpus':[{'temp_c':50}]}


@pytest.mark.parametrize('sample,expected',[(COOL,None),({'cpu_temp_c':85,'gpus':[]},'CPU'),({'cpu_temp_c':52,'gpus':[{'temp_c':80}]},'GPU'),({'cpu_temp_c':None,'gpus':[]},'CPU'),({'cpu_temp_c':52,'gpus':[]},'NVIDIA'),({'cpu_temp_c':52,'gpus':[{'temp_c':None}]},'GPU')])
def test_threshold_and_missing_sensor(sample,expected):
    reason=thermal_violation(sample,85,80,True)
    assert (reason is None) if expected is None else expected in reason


def test_guard_allows_completed_response():
    monitor=Mock();monitor.check.return_value=COOL
    stopper=Mock(gpu_required=True)
    assert guarded_run(lambda:42,monitor,stopper)==42
    stopper.stop.assert_not_called()


@pytest.mark.parametrize('confirmed',[True,False])
def test_trip_stops_server_and_preserves_confirmation(confirmed):
    released=threading.Event()
    def work():
        released.wait(3)
        return 'reply'
    monitor=Mock();monitor.check.side_effect=[COOL,{'cpu_temp_c':90,'gpus':[{'temp_c':55}]}]
    stopper=Mock(gpu_required=True)
    def stop():
        released.set()
        return {'confirmed':confirmed}
    stopper.stop.side_effect=stop
    with pytest.raises(GuardAbort) as caught:
        guarded_run(work,monitor,stopper)
    assert caught.value.shutdown['confirmed']==confirmed
    assert caught.value.shutdown['client_finished'] is True
    stopper.stop.assert_called_once()


def test_monitor_failure_stops_server():
    monitor=Mock();monitor.check.side_effect=ValueError('sensor perdido')
    stopper=Mock(gpu_required=True);stopper.stop.return_value={'confirmed':False}
    with pytest.raises(GuardAbort,match='sensor perdido'):
        guarded_run(lambda:42,monitor,stopper)
    stopper.stop.assert_called_once()


def test_worker_error_stops_server():
    monitor=Mock();monitor.check.return_value=COOL
    stopper=Mock(gpu_required=True);stopper.stop.return_value={'confirmed':True}
    def fail(): raise ValueError('timeout')
    with pytest.raises(GuardAbort,match='timeout'):
        guarded_run(fail,monitor,stopper)
    stopper.stop.assert_called_once()


def test_keyboard_interrupt_triggers_stop():
    monitor=Mock();monitor.check.side_effect=KeyboardInterrupt
    stopper=Mock(gpu_required=True);stopper.stop.return_value={'confirmed':True}
    with pytest.raises(GuardAbort,match='usuário'):
        guarded_run(lambda:42,monitor,stopper)


@pytest.mark.parametrize('host',['http://example.com:11434','http://127.0.0.1:8000','https://127.0.0.1:11434','http://127.0.0.1:11434/path'])
def test_remote_and_wrong_port_rejected(host):
    with pytest.raises(ValueError): ServiceStopper(host)


def test_service_stop_requires_all_confirmation_signals(tmp_path):
    with patch('llm_lab.thermal.shutil.which',return_value='/usr/bin/systemctl'),patch('llm_lab.thermal.os.geteuid',return_value=0):
        stopper=ServiceStopper()
    stopper.cgroup=tmp_path
    (tmp_path/'cgroup.procs').write_text('')
    stopper.state=Mock(return_value={'ActiveState':'inactive','MainPID':'0'})
    stopper.api=Mock(side_effect=URLError(ConnectionRefusedError()))
    with patch('llm_lab.thermal.subprocess.run',return_value=SimpleNamespace(returncode=0,stderr='')):
        assert stopper.stop()['confirmed'] is True
    (tmp_path/'cgroup.procs').write_text('123\n')
    with patch('llm_lab.thermal.subprocess.run',return_value=SimpleNamespace(returncode=0,stderr='')),patch('llm_lab.thermal.time.monotonic',side_effect=[0,11]):
        result=stopper.stop()
    assert result['confirmed'] is False and result['remaining_pids']==['123']


def test_api_responding_is_not_confirmation(tmp_path):
    with patch('llm_lab.thermal.shutil.which',return_value='/usr/bin/systemctl'),patch('llm_lab.thermal.os.geteuid',return_value=0):
        stopper=ServiceStopper()
    stopper.cgroup=tmp_path
    stopper.state=Mock(return_value={'ActiveState':'inactive','MainPID':'0'})
    stopper.api=Mock(return_value={'version':'test'})
    with patch('llm_lab.thermal.subprocess.run',return_value=SimpleNamespace(returncode=0,stderr='')),patch('llm_lab.thermal.time.monotonic',side_effect=[0,11]):
        assert stopper.stop()['confirmed'] is False


def test_rehearsal_rejects_loaded_models():
    stopper=Mock(gpu_required=False)
    stopper.preflight.return_value={}
    stopper.api.return_value={'models':[{'name':'busy'}]}
    with patch('llm_lab.thermal.ServiceStopper',return_value=stopper),patch('llm_lab.thermal.Sampler.sample',return_value=COOL):
        with pytest.raises(ValueError,match='nenhum modelo'):
            check_guard('http://127.0.0.1:11434',test_stop=True)
    stopper.stop.assert_not_called()
