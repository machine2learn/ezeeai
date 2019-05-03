from ezeeai.core.runner import Runner

import time
import psutil
from multiprocessing import Process, Queue
from ..utils.sys_ops import find_free_port, change_checkpoints
from ..config import config_reader
import threading
import logging
import subprocess

logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )


class ThreadHandler:
    def __init__(self):
        self._processes = {}
        self._ports = {}
        self._return_queue = Queue()

    def _get_runner(self, all_params_config):

        return Runner(all_params_config)

    def add_port(self, username, config_file, port):
        self._ports[username + '_' + config_file] = port

    def get_port(self, username, config_file):
        return self._ports[username + '_' + config_file]

    def tensor_board_thread(self, config_file, port):
        config_path = config_reader.read_config(config_file).all()['checkpoint_dir']
        logging.debug('Starting tensor board')
        time.sleep(3)
        pro = "tensorboard --host=0.0.0.0 --logdir=" + config_path + " --port=" + port
        subprocess.call(pro, shell=True)
        logging.debug('Exiting tensor board')

    def run_tensor_board(self, username, config_file):
        if not username + '_' + config_file in self._ports.keys():
            try:
                port = find_free_port()

                self.add_port(username, config_file, port)
                name = 'tensorboard-' + str(port)
                tboard_thread = threading.Thread(name=name,
                                                 target=lambda: self.tensor_board_thread(config_file, port))
                tboard_thread.setDaemon(True)
                tboard_thread.start()
            except ValueError:
                logging.error('No free port found.')

    def run_thread(self, all_params_config):
        runner = self._get_runner(all_params_config)
        runner.run()

    def predict_thread(self, all_params_config, new_features, all=False):
        runner = self._get_runner(all_params_config)
        self._return_queue.put(runner.predict(new_features, all))

    def predict_test_thread(self, all_params_config, test_file):
        runner = self._get_runner(all_params_config)
        self._return_queue.put(runner.predict_test(test_file))

    def explain_thread(self, all_params_config, explain_params):
        runner = self._get_runner(all_params_config)
        self._return_queue.put(runner.explain(explain_params))

    def pause_threads(self, username):
        p = self._processes[username]['process'] if username in self._processes.keys() else None
        if not isinstance(p, str) and p:
            pid = p.pid
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            del self._processes[username]
        return True

    def check_running(self, username):
        if username in self._processes.keys():
            return self._processes[username]['process'].is_alive(), self._processes[username]['config_file']
        return False, None

    def run_estimator(self, all_params_config, username, config_file):
        r_thread = Process(
            target=lambda: self.run_thread(all_params_config), name='run')
        r_thread.daemon = True
        r_thread.start()
        self._processes[username] = {'process': r_thread, 'config_file': config_file}

    def predict_estimator(self, all_params_config, features, all=False):
        r_thread = Process(target=lambda: self.predict_thread(all_params_config, features, all), name='predict')
        r_thread.daemon = True
        r_thread.start()
        final_pred = self._return_queue.get()
        r_thread.join()
        return final_pred

    def predict_test_estimator(self, all_params_config, features):
        r_thread = Process(target=lambda: self.predict_test_thread(all_params_config, features), name='test')
        r_thread.daemon = True
        r_thread.start()
        final_pred = self._return_queue.get()
        r_thread.join()
        return final_pred

    def explain_estimator(self, all_params_config, explain_params):
        r_thread = Process(target=lambda: self.explain_thread(all_params_config, explain_params),
                           name='explain')
        r_thread.daemon = True
        r_thread.start()
        exp = self._return_queue.get()
        r_thread.join()
        return exp

    def handle_request(self, option, all_params_config, username, resume_from, config_file):
        if option == 'run':
            if resume_from != '':
                change_checkpoints(all_params_config, resume_from)
            self.run_estimator(all_params_config, username, config_file)
        elif option == 'pause':
            self.pause_threads(username)
        else:
            raise ValueError("Invalid option")
