"""
hgtools implements several repo managers, each of which provides an interface
to Mercurial functionality.
"""

import posixpath
import itertools

from hgtools import versioning

class HGRepoManager(versioning.VersionManagement, object):
	"""
	An abstract class defining some interfaces for working with
	Mercurial repositories.
	"""
	def __init__(self, location='.'):
		self.location = location
		self.setup()

	def is_valid(self):
		"Return True if this is a valid manager for this location."
		return True

	def setup(self):
		pass

	@classmethod
	def get_valid_managers(cls, location):
		"""
		Get the valid HGRepoManagers for this location.
		"""
		by_priority_attr = lambda c: getattr(c, 'priority', 0)
		classes = sorted(cls.__subclasses__(), key = by_priority_attr,
			reverse = True)
		all_managers = (c(location) for c in classes)
		return (mgr for mgr in all_managers if mgr.is_valid())

	@staticmethod
	def get_first_valid_manager(location='.'):
		return next(HGRepoManager.get_valid_managers(location))

	@staticmethod
	def existing_only(managers):
		"""
		Return only those managers that refer to an existing repo
		"""
		return (mgr for mgr in managers if mgr.find_root())

	def __repr__(self):
		class_name = self.__class__.__name__
		loc = self.location
		return '%(class_name)s(%(loc)r)' % vars()

	def find_root(self):
		raise NotImplementedError()

	def find_files(self):
		raise NotImplementedError()

	def get_tags(self, rev=None):
		"""
		Get the tags for the specified revision (or the current revision
		if none is specified).
		"""
		raise NotImplementedError()

	def get_repo_tags(self):
		"""
		Get all tags for the repository.
		"""
		raise NotImplementedError()

	def get_parent_tags(self, rev=None):
		"""
		Return the tags for the parent revision (or None if no single
			parent can be identified).
		"""
		try:
			parent_rev = one(self.get_parent_revs(rev))
		except Exception:
			return None
		return self.get_tags(parent_rev)

	def get_parent_revs(self, rev=None):
		"""
		Get the parent revision for the specified revision (or the current
		revision if none is specified).
		"""
		raise NotImplementedError

	def is_modified(self):
		'Does the current working copy have modifications'
		raise NotImplementedError()

	def find_all_files(self):
		"""
		Find files including those in subrepositories.
		"""
		files = self.find_files()
		subrepo_files = (
			posixpath.join(subrepo.location, filename)
			for subrepo in self.subrepos()
			for filename in subrepo.find_files()
		)
		return itertools.chain(files, subrepo_files)

	def subrepos(self):
		try:
			with open(posixpath.join(self.location, '.hgsub')) as file:
				subs = list(file)
		except Exception:
			subs = []

		locs = [part.partition('=')[0].strip() for part in subs]
		return [self.__class__(posixpath.join(self.location, loc)) for loc in locs]

# from jaraco.util.itertools
def one(item):
	"""
	Return the first element from the iterable, but raise an exception
	if elements remain in the iterable after the first.

	>>> one([3])
	3
	>>> one(['val', 'other'])
	Traceback (most recent call last):
	...
	ValueError: item contained more than one value
	>>> one([])
	Traceback (most recent call last):
	...
	StopIteration
	"""
	iterable = iter(item)
	result = next(iterable)
	if tuple(itertools.islice(iterable, 1)):
		raise ValueError("item contained more than one value")
	return result
