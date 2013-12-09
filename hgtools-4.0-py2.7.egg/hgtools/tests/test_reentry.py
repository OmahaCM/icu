from __future__ import print_function

import sys

import py.test

from hgtools.managers import reentry

def hello_world():
	print("hello world")

def hello_unicode_world():
	print(b"hello world".decode('ascii'))

def exit_zero():
	raise SystemExit(0)

def exit_one():
	raise SystemExit(1)

def exit_string():
	raise SystemExit('who does this?')

def echo():
	print("args are", sys.argv)

class TestReEntry(object):
	"""
	Test the in-process entry point launcher
	"""
	def test_hello_world(self):
		with reentry.in_process_context(['hello-world.py']) as proc:
			hello_world()
		assert proc.returncode == 0
		assert proc.stdio.stdout.getvalue() == 'hello world\n'

	def test_hello_world_unicode(self):
		with reentry.in_process_context(['hello-world.py']) as proc:
			hello_unicode_world()
		assert proc.returncode == 0
		assert proc.stdio.stdout.getvalue() == 'hello world\n'

	def test_main_with_system_exit(self):
		with reentry.in_process_context(['exit-zero']) as proc:
			exit_zero()
		assert proc.returncode == 0
		assert proc.stdio.stdout.getvalue() == ''

	def test_main_with_system_exit_one(self):
		with reentry.in_process_context(['exit-one']) as proc:
			exit_one()
		assert proc.returncode == 1
		assert proc.stdio.stdout.getvalue() == ''

	def test_main_with_system_exit_string(self):
		with reentry.in_process_context(['exit-string']) as proc:
			exit_string()
		assert proc.returncode == 1
		assert proc.stdio.stdout.getvalue() == ''

	def test_echo_args(self):
		with reentry.in_process_context(['echo', 'foo', 'bar']) as proc:
			echo()
		assert proc.returncode == 0
		out = "args are ['echo', 'foo', 'bar']\n"
		assert proc.stdio.stdout.getvalue() == out

class TestErrors(object):
	def test_name_error(self):
		with py.test.raises(NameError) as exc_info:
			with reentry.in_process_context([]) as proc:
				not_present
		assert proc.returncode == 1
		msg = "global name 'not_present' is not defined"
		assert str(exc_info.value) == msg

	def test_keyboard_interrupt(self):
		with py.test.raises(KeyboardInterrupt):
			with reentry.in_process_context([]) as proc:
				raise KeyboardInterrupt()
		assert proc.returncode == 1
