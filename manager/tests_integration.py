import os
import unittest
from . import (
	connect_to_db_server, 
	csv_to_table, 
	table_to_csv, 
	csv_to_tuples,
	ping)
from . import package_dir

class TestVarEnvPresents(unittest.TestCase):
	def test_postgres_env_vars_set(self):
		""" assert whether env variables are defined """
		self.assertIn("POSTGRES_PASSWORD", os.environ)
		self.assertIn("POSTGRES_USER", os.environ)
		self.assertIn("POSTGRES_DB", os.environ)

	def test_CSV_filename_is_set(self):
		""" assert the CSV filename var env is set """
		self.assertIn("CSV_FILENAME", os.environ)

	def tearDown(self):
		super().tearDown()

class TestCoreServices(unittest.TestCase):
	def test_is_postgres_service_reachable(self):
		self.assertTrue(ping("db"))
	def test_are_dependencies_installed_for_app(self):
		try:
			import psycopg2
			boolean = True
		except:
			boolean = False
		self.assertTrue(boolean)

class TestConnectPostgres(unittest.TestCase):

	def setUp(self):
		self.pgpass = os.getenv("POSTGRES_PASSWORD")
		self.pguser = os.getenv("POSTGRES_USER")
		self.pgdb = os.getenv("POSTGRES_DB")
		self.connection = None

	def test_connection_to_db_server(self):
		""" using db as host server name """
		self.connection = connect_to_db_server(
				self.pguser, self.pgpass, self.pgdb)
		self.assertIsNotNone(self.connection)
			
	def tearDown(self):
		super().tearDown()
		""" This is called even if the test method raised an exception and if the setUp() succeeds """
		if self.connection is not None:
			self.connection.close()

class TestUploadCSV(TestConnectPostgres):

	def setUp(self):
		super().setUp()
		self.connection = connect_to_db_server(
			self.pguser, self.pgpass, self.pgdb)
		self.cursor = self.connection.cursor()
		self.table_name = "persons"
	
	def test_table_exists(self):
		""" Check for existence of the table, using EXISTS doesn't require that all rows be retrieved, but merely that at least one such row exists """
		self.cursor.execute(f"select * from {self.table_name} limit 0;")
		colnames = [desc[0] for desc in self.cursor.description]
		#print( colnames )
		# number of columns equals or is greater than 3
		self.assertGreaterEqual(len(colnames), 3)

	def test_csv_upload_and_download_have_worked(self):
		# replace by hand crafted file
		path_input_file = os.path.join(package_dir, os.getenv("CSV_FILENAME"))
		path_output_file = os.path.join(package_dir, "fetched_test.csv")

		table_to_csv(self.connection, self.table_name, path_output_file)

		self.assertEqual(
			csv_to_tuples(path_input_file),
			csv_to_tuples(path_output_file))

	def tearDown(self):
		super().tearDown()


def launch_tests():
	suite = unittest.TestSuite()
	suite.addTest(TestVarEnvPresents(
		'test_postgres_env_vars_set'))
	suite.addTest(TestVarEnvPresents(
		'test_CSV_filename_is_set'))
	suite.addTest(TestCoreServices(
		'test_is_postgres_service_reachable'
		))
	suite.addTest(TestCoreServices(
		'test_are_dependencies_installed_for_app'
		))
	suite.addTest(TestConnectPostgres(
		'test_connection_to_db_server'))
	suite.addTest(TestUploadCSV(
		'test_table_exists'))
	suite.addTest(TestUploadCSV(
		'test_csv_upload_and_download_have_worked'))
	test_result = unittest.TextTestRunner().run(suite)
	print(len(test_result.failures))
	print(len(test_result.errors))