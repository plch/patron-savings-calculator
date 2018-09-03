#~ this script will fetch data from the sierra postgresql database and
#~ fill a local database.

import configparser
import sqlite3
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

# debug
import pdb

class App:

	def __init__(self):
		#~ open the config file, and parse the options into local vars
		config = configparser.ConfigParser()
		config.read('config.ini')

		# the salt used for encoding the bib record id (make sure the salt is the same going forward, or we won't be able to id unique bibs)
		self.salt = config['misc']['salt']

		# the remote database connection
		self.db_connection_string = config['db']['connection_string']
		self.pgsql_conn = None

		# the local database connection
		self.local_db_connection_string = config['local_db']['connection_string']
		self.sqlite_conn = None

		# the number of rows to iterate over
		self.itersize = int(config['db']['itersize'])

		# open the database connections
		self.open_db_connections()

		# create the table if it doesn't exist
		self.create_local_table()

		# fill the local database
		self.fill_local_db()


	def open_db_connections(self):
		#~ connect to the sierra postgresql server
		try:
			self.pgsql_conn = psycopg2.connect(self.db_connection_string)

		except psycopg2.Error as e:
			print("unable to connect to sierra database: %s" % e)

		#~ connect to the local sqlite database
		try:
			self.sqlite_conn = sqlite3.connect(self.local_db_connection_string)
		except sqlite3.Error as e:
			print("unable to connect to local database: %s" % e)


	def close_connections(self):
		print("closing database connections...")
		if self.pgsql_conn:
			if hasattr(self.pgsql_conn, 'close'):
				print("closing pgsql_conn")
				self.pgsql_conn.close()
				self.pgsql_conn = None

		if self.sqlite_conn:
			if hasattr(self.sqlite_conn, 'close'):
				print("closing sqlite_conn")
				self.sqlite_conn.close()
				self.sqlite_conn = None


	def create_local_table(self):
		cursor = self.sqlite_conn.cursor()
		
		# create the table if it doesn't exist
		sql = """
		CREATE TABLE IF NOT EXISTS circ_trans (
			circ_trans_id INTEGER UNIQUE,
			patron_record_id INTEGER,
			patron_record_num INTEGER,
			ptype_code INTEGER,
			bib_record_hash TEXT,
			transaction_epoch INTEGER,
			due_epoch INTEGER,
			application_name INTEGER,
			stat_group_code_num INTEGER,
			loanrule_code_num INTEGER,
			bib_level_code TEXT,
			material_code TEXT,
			itype_code_num INTEGER,
			price REAL,
			PRIMARY KEY(circ_trans_id)
		)
		"""
		cursor.execute(sql)
		
		# sql = """
		# CREATE UNIQUE INDEX IF NOT EXISTS `bib_id_index` ON `bib_data` (`bib_id` DESC)
		# """
		# cursor.execute(sql)
				
		self.sqlite_conn.commit()		
		cursor.close()
		cursor = None


	def get_local_max(self):
		# this will return the maximum circ_trans_id from the local database, for use in the later update
		sql = """
		SELECT
		IFNULL(MAX(circ_trans_id), 0) as max_id

		FROM
		circ_trans

		LIMIT 1
		"""

		cursor = self.sqlite_conn.cursor()
		cursor.execute(sql)
		max_id = cursor.fetchone()[0]
		cursor.close()
		cursor = None

		return max_id


	def sierra_data_generator(self, start_id=0):
		sql = """
		SELECT
		c.id as circ_trans_id,
		c.patron_record_id,
		r.record_num as patron_record_num,
		pr.ptype_code,
		md5(
			concat(c.bib_record_id, r.record_num, %s)
		) AS bib_record_hash,
		extract(EPOCH FROM c.transaction_gmt)::INTEGER AS transaction_epoch,
		extract(EPOCH FROM c.due_date_gmt)::INTEGER as due_epoch,
		c.application_name,
		c.stat_group_code_num,
		c.loanrule_code_num,
		p.bib_level_code,
		p.material_code,
		c.itype_code_num,
		i.price

		FROM
		sierra_view.circ_trans as c

		JOIN
		sierra_view.record_metadata as r
		ON
		r.id = c.patron_record_id

		JOIN
		sierra_view.item_record as i
		ON
		i.record_id = c.item_record_id

		JOIN
		sierra_view.bib_record_property as p
		ON
		p.bib_record_id = c.bib_record_id

		JOIN
		sierra_view.patron_record as pr
		ON
		  pr.record_id = c.patron_record_id

		WHERE
		c.op_code = 'o' -- only checkout data
		AND c.id > %s
		"""

		with self.pgsql_conn as conn:
			with conn.cursor(name='circ_trans_cursor', cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
				
				#~ we want to have the remote database feed us records of self.itersize
				cursor.itersize = self.itersize
				#~ execute the query with the query parameters
				cursor.execute(sql, (self.salt, start_id,))
				# pdb.set_trace()
				#~ fetch and yield self.itersize number of rows per round
				rows = None
				while True:
					rows = cursor.fetchmany(self.itersize)
					if not rows:
						break

					for row in rows:
						# do something with row
						yield row
		cursor.close()
		cursor = None


	def fill_local_db(self):
		"""
		TODO: more documentation
		"""						
			
		local_max = self.get_local_max()
		print('starting with max id: \t{}'.format(local_max))
		cursor = self.sqlite_conn.cursor()

		# debug
		# pdb.set_trace()

		sql = """
		INSERT OR REPLACE INTO
		circ_trans (
			circ_trans_id, -- 1 INTEGER UNIQUE
			patron_record_id, -- 2 INTEGER
			patron_record_num, -- 3 INTEGER
			ptype_code, -- 4 INTEGER
			bib_record_hash, -- 5 TEXT
			transaction_epoch, --6 INTEGER
			due_epoch, -- 7 INTEGER
			application_name, -- 8 INTEGER
			stat_group_code_num, -- 9 INTEGER
			loanrule_code_num, -- 10 INTEGER
			bib_level_code, -- 11 TEXT
			material_code, -- 12 TEXT
			itype_code_num, -- 13 INTEGER
			price -- 14 REAL
		)

		VALUES (
			?, -- 1
			?, -- 2
			?, -- 3
			?, -- 4
			?, -- 5
			?, -- 6
			?, -- 7
			?, -- 8
			?, -- 9
			?, -- 10
			?, -- 11
			?, -- 12
			?, -- 13
			?  -- 14
		)
		"""

		counter = 0
		for row in self.sierra_data_generator(local_max):
			# debug
			# pdb.set_trace()

			# set the values coming from the generator
			values = (
				int(row.circ_trans_id),
				int(row.patron_record_id),
				int(row.patron_record_num),
				int(row.ptype_code),
				row.bib_record_hash,
				int(row.transaction_epoch),
				int(row.due_epoch),
				row.application_name,
				row.stat_group_code_num,
				row.loanrule_code_num,
				row.bib_level_code,
				row.material_code,
				row.itype_code_num,
				format(row.price, '.2f') # limit decimal to two places past the decimal
			)

			# debug
			# pdb.set_trace()
			
			cursor.execute(sql, values)
			counter += 1
			
			#~ we are going to insert if it doesn't exist, and if we 
			#~ reaise an integrity error (duplicate key), update in the except
			#~ try:
				#~ cursor.execute(sql, values)
				
			#~ except sqlite3.IntegrityError as error:
				#~ print("last row id: ", end='')
				#~ print(cursor.lastrowid)
				#~ print(error)
				
				#~ pass
				
			
			#~ probably should commit every self.itersize rows
			if(counter % self.itersize == 0):
				self.sqlite_conn.commit()
				print('counter: {}'.format(counter))
				print('id: {}'.format(row.circ_trans_id))
				print(values)

		# when done with the the for loop, make sure we commit one more time, to make sure we've added all values
		self.sqlite_conn.commit()

		#~ fixes the error "UnboundLocalError: local variable 'row' 
		#~ referenced before assignment" where there are no rows returned 
		#~ from query		
		if 'row[0]' in locals():
			print('finishing with id: \t{}'.format(row.circ_trans_id))
		print('final count inserted: \t\t{}'.format(counter))
		cursor.close()
		cursor = None


	#~ the destructor
	def __del__(self):
		self.sqlite_conn.commit()
		self.close_connections()
		print("done.")


#~ run the app!
start_time = datetime.now()
print('starting import at: \t\t{}'.format(start_time))
app = App()
end_time = datetime.now()
print('finished import at: \t\t{}'.format(end_time))
print('total import time: \t\t{}'.format(end_time - start_time))