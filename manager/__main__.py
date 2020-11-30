from . import *

if not testing:	
	try:
		con = None
		# open connection to db
		con = connect_to_db_server(pguser, pgpassword, pgdb)
		# create a new table "person"
		create_new_table(con)
		# populate table from csv file
		csv_to_table(con, "persons", path_data)
		# read table again
		#table_to_csv(con, "persons", path_output_data)
	except Exception as e:
		print(f"An error occured:\n {e}")
	finally:
		# close connection if exists
	    if con is not None:
	        con.close()	
else:
	launch_tests()
