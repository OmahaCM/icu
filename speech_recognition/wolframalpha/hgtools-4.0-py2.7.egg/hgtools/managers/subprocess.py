from __future__ import absolute_import

import os
import subprocess

from . import base
from . import cmd

class SubprocessManager(cmd.Command, base.HGRepoManager):
	"""
	An HGRepoManager implemented by calling into the 'hg' command-line
	as a subprocess.
	"""
	priority = 1

	@staticmethod
	def _safe_env():
		"""
		Return an environment safe for calling an `hg` subprocess.

		Removes MACOSX_DEPLOYMENT_TARGET from the env, as if there's a
		mismatch between the local Python environment and the environment
		in which `hg` is installed, it will cause an exception. See
		https://bitbucket.org/jaraco/hgtools/issue/7 for details.
		"""
		env = os.environ.copy()
		env.pop('MACOSX_DEPLOYMENT_TARGET', None)
		return env

	def _run_hg(self, *params):
		cmd = [self.exe] + list(params)
		proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
			stderr=subprocess.PIPE, cwd=self.location, env=self._safe_env())
		stdout, stderr = proc.communicate()
		if not proc.returncode == 0:
			raise RuntimeError(stderr.strip() or stdout.strip())
		return stdout.decode('utf-8')
