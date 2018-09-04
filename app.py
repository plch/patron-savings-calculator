from flask import Flask, request, send_from_directory
from flask_restful import Resource, Api
from flask_cors import CORS
import configparser
import sqlite3

app = Flask(__name__, static_url_path='')
# allow CORS for all domains and routes (makes cross-origin AJAX possible)
CORS(app)
api = Api(app)

# this should be only used for testing purposes only ...it's better to serve javascript from a webserver like apache
@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)

class PatronSavings(Resource):
    def __init__(self):
        #~ open the config file, and parse the options into local vars
        config = configparser.ConfigParser()
        config.read('config.ini')

        # the local database connection
        self.local_db_connection_string = config['local_db']['connection_string']
        self.sqlite_conn = None

        # open the database connections
        self.open_db_connections()


    def open_db_connections(self):
        #~ connect to the local sqlite database
        try:
            # this method opens the sqlite3 database in read-only mode
            self.sqlite_conn = sqlite3.connect('file:' + self.local_db_connection_string, uri=True)
        except sqlite3.Error as e:
            print("unable to connect to local database: %s" % e)


    def close_connections(self):
        print("closing database connections...")

        if self.sqlite_conn:
            if hasattr(self.sqlite_conn, 'close'):
                print("closing sqlite_conn")
                self.sqlite_conn.close()
                self.sqlite_conn = None


    def get(self, patron_record_num):
        cursor = self.sqlite_conn.cursor()
        sql = """
        WITH prices AS (
            SELECT
            circ_trans.patron_record_num,
            circ_trans.bib_record_hash,
            circ_trans.price

            FROM
            circ_trans

            WHERE
            circ_trans.patron_record_num = ?

            GROUP BY
            circ_trans.patron_record_num,
            circ_trans.bib_record_hash,
            circ_trans.price
        )

        SELECT
        prices.patron_record_num,
        SUM(prices.price) AS total,
        (
            SELECT
            MIN(circ_trans.transaction_epoch)

            FROM
            circ_trans

            WHERE
            circ_trans.patron_record_num = ?
        ) AS min_date,
        count(prices.bib_record_hash) as count_titles

        FROM 
        prices

        LIMIT 1
        ;
        """
        cursor.execute(sql, (int(patron_record_num), int(patron_record_num)))
        data = cursor.fetchone()
        if (data[0] != None):
            return {
                'patron_record_num': data[0],
                'total_savings': data[1],
                'min_date_epoch': data[2],
                'count_titles': data[3]
            }
        else:
            # return a null value, and a http 404 code for no patron info found
            return None, 404


    #~ the destructor
    def __del__(self):
        # if the sqlite connection is still open, and we can, commit any uncommited results
        # ...although, if reading database in read-only mode, then this shouldn't matter
        if self.sqlite_conn:
            if hasattr(self.sqlite_conn, 'commit'):
                self.sqlite_conn.commit()
        self.close_connections()
        print("done.")   
    

api.add_resource(PatronSavings, '/<int:patron_record_num>')

if __name__ == '__main__':
    # note: this is only for testing, but in order to test on encore (which loads account info over https, we need to serve our API over https)
    # TODO: get this endpoint running over 
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')