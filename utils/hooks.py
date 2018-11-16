from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from tensorflow.python.training import session_run_hook
from tensorflow.python.training.basic_session_run_hooks import NeverTriggerTimer, SecondOrStepTimer
from tensorflow.python.training.session_run_hook import SessionRunArgs
from tensorflow.python.util.tf_export import tf_export

import smtplib
from email.mime.text import MIMEText


@tf_export("train.EmailAtStepHook")
class EmailAtStepHook(session_run_hook.SessionRunHook):

    def __init__(self, user_info, server_info, every_n_iter=None, every_n_secs=None,
                 at_end=False):
        only_log_at_end = (
                at_end and (every_n_iter is None) and (every_n_secs is None))
        if (not only_log_at_end and
                (every_n_iter is None) == (every_n_secs is None)):
            raise ValueError(
                "either at_end and/or exactly one of every_n_iter and every_n_secs "
                "must be provided.")
        if every_n_iter is not None and every_n_iter <= 0:
            raise ValueError("invalid every_n_iter=%s." % every_n_iter)

        self._timer = (
            NeverTriggerTimer() if only_log_at_end else
            SecondOrStepTimer(every_secs=every_n_secs, every_steps=every_n_iter))
        self._log_at_end = at_end
        self._user_info = user_info
        self._server_info = server_info
        self._timer.reset()
        self._iter_count = 0

    def begin(self):
       pass

    def before_run(self, run_context):  # pylint: disable=unused-argument
        self._should_trigger = self._timer.should_trigger_for_step(self._iter_count)

    def after_run(self, run_context, run_values):
        _ = run_context
        if self._should_trigger:
            self._send_email()

        self._iter_count += 1

    def end(self, session):
        if self._log_at_end:
            self._send_email()

    def _send_email(self):
        smtpserver = 'smtp.gmail.com:587'

        header = 'From: %s' % self._server_info['email_address']
        header += 'To: %s' % self._user_info['email_address']
        header += 'Subject: %s' % "Training finished"
        message = header + "Training finished"

        server = smtplib.SMTP(smtpserver)
        server.starttls()
        server.login(self._server_info['login'], self._server_info['password'])
        problems = server.sendmail(self._server_info['email_address'], self._user_info['email_address'], message)
        server.quit()
