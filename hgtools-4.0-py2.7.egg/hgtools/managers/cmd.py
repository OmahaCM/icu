import os
import re
import operator
import itertools
import collections

class Command(object):
	exe = 'hg'

	def is_valid(self):
		try:
			self._run_hg('version')
		except Exception:
			return False
		return super(Command, self).is_valid()

	def find_root(self):
		try:
			return self._run_hg('root').strip()
		except Exception:
			pass

	def find_files(self):
		"""
		Find versioned files in self.location
		"""
		all_files = self._run_hg('locate', '-I', '.').splitlines()
		# now we have a list of all files in self.location relative to
		#  self.find_root()
		# Remove the parent dirs from them.
		from_root = os.path.relpath(self.location, self.find_root())
		loc_rel_paths = [os.path.relpath(path, from_root)
			for path in all_files]
		return loc_rel_paths

	def get_parent_revs(self, rev=None):
		cmd = ['parents', '--style', 'default',
			'--config', 'defaults.parents=']
		if rev:
			cmd.extend(['--rev', str(rev)])
		out = self._run_hg(*cmd)
		cs_pat = '^changeset:\s+(?P<local>\d+):(?P<hash>[0-9a-zA-Z]+)'
		return (match.groupdict()['local'] for match in
			re.finditer(cs_pat, out))

	def get_tags(self, rev=None):
		"""
		Get the tags for the given revision specifier (or the
		current revision if not specified).
		"""
		rev_num = self._get_rev_num(rev)
		# rev_num might end with '+', indicating local modifications.
		return (
			set(self._read_tags_for_rev(rev_num))
			if not rev_num.endswith('+')
			else set([])
		)

	def _read_tags_for_rev(self, rev_num):
		"""
		Return the tags for revision sorted by when the tags were
		created (latest first)
		"""
		cmd = ['log', '--style', 'default',  '--config', 'defaults.log=',
			'-r', rev_num]
		res = self._run_hg(*cmd)
		tag_lines = [
			line for line in res.splitlines()
			if line.startswith('tag:')
		]
		header_pattern = re.compile('(?P<header>\w+?):\s+(?P<value>.*)')
		return (header_pattern.match(line).groupdict()['value']
			for line in tag_lines)

	def _get_rev_num(self, rev=None):
		"""
		Determine the revision number for a given revision specifier.
		"""
		# first, determine the numeric ID
		cmd = ['identify', '--num']
		# workaround for #4
		cmd.extend(['--config', 'defaults.identify='])
		if rev:
			cmd.extend(['--rev', rev])
		res = self._run_hg(*cmd)
		return res.strip()

	def _get_tags_by_num(self):
		"""
		Return a dictionary mapping revision number to tags for that number.
		"""
		by_revision = operator.attrgetter('revision')
		tags = sorted(self.get_tags(), key=by_revision)
		revision_tags = itertools.groupby(tags, key=by_revision)
		get_id = lambda rev: rev.split(':', 1)[0]
		return dict(
			(get_id(rev), [tr.tag for tr in tr_list])
			for rev, tr_list in revision_tags
		)

	def get_repo_tags(self):
		tagged_revision = collections.namedtuple('tagged_revision',
			'tag revision')
		lines = self._run_hg('tags').splitlines()
		return (
			tagged_revision(*line.rsplit(None, 1))
			for line in lines if line
		)

	def is_modified(self):
		out = self._run_hg('status', '-mard')
		return bool(out)
