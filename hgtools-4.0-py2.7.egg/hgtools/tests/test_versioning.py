import collections
from distutils.version import StrictVersion

from hgtools import versioning

class VersionedObject(versioning.VersionManagement):
	def __init__(self, **kwargs):
		self.__dict__.update(kwargs)

	def is_modified(self):
		return False

class TestVersioning(object):
	def test_tag_versions(self):
		"""
		Versioning should only choose relevant tags (versions)
		"""
		mgr = VersionedObject(get_tags = lambda: tags)
		tags = set(['foo', 'bar', '3.0'])
		assert mgr.get_tagged_version() == StrictVersion('3.0')
		tags = set([])
		assert mgr.get_tagged_version() == None
		tags = set(['foo', 'bar'])
		assert mgr.get_tagged_version() == None

	def test_tag_priority(self):
		"""
		Since Mercurial provides tags in arbitrary order, the versioning
		support should infer the precedence (choose latest).
		"""
		mgr = VersionedObject(get_tags = lambda: tags)
		tags = set(['1.0', '1.1'])
		assert mgr.get_tagged_version() == '1.1'
		tags = set(['0.10', '0.9'])
		assert mgr.get_tagged_version() == '0.10'

	def test_defer_to_parent_tag(self):
		"""
		Use the parent tag if on the tip
		"""
		mgr = VersionedObject(
			get_tags = lambda rev=None: set(['tip']),
			get_parent_tags = lambda rev=None: set(['1.0']),
		)
		assert mgr.get_tagged_version() == '1.0'

	def test_get_next_version(self):
		mgr = VersionedObject(
			get_repo_tags = lambda: set([])
		)
		assert mgr.get_next_version() == '0.0.1'

	def test_local_revision_not_tagged(self):
		"""
		When no tags are available, use the greatest tag and add the increment
		"""
		mgr = VersionedObject(
			get_tags = lambda rev=None: set([]),
			get_repo_tags = lambda: set(
				collections.namedtuple('tag', 'tag')(var)
				for var in ['foo', 'bar', '1.0'])
		)
		assert mgr.get_tagged_version() is None
		assert mgr.get_next_version() == StrictVersion('1.0.1')
		assert mgr.get_current_version() == '1.0.1dev'
