from flask import Flask, request, send_file, jsonify, send_from_directory  # remove send_from_directory when we no longer need the static route.
from flask_cors import CORS
import configparser
import sqlite3

app = Flask(__name__, static_url_path='')
# allow CORS for all domains and routes (makes cross-origin AJAX possible)
CORS(app)

class PatronSavings():
    def __init__(self):
        #~ open the config file, and parse the options into local vars
        config = configparser.ConfigParser()
        config.read('config.ini')

        # the local database connection
        self.local_db_connection_string = config['local_db']['connection_string']
        self.sqlite_conn = None

        self.sql_compute_savings = """
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


    def open_db_connections(self):
        #~ connect to the local sqlite database
        try:
            # this method opens the sqlite3 database in read-only mode
            self.sqlite_conn = sqlite3.connect('file:' + self.local_db_connection_string, uri=True, check_same_thread=True)
        except sqlite3.Error as e:
            print("unable to connect to local database: %s" % e)


    def close_connections(self):
        print("closing database connections...")

        if self.sqlite_conn:
            if hasattr(self.sqlite_conn, 'close'):
                print("closing sqlite_conn")
                self.sqlite_conn.close()
                self.sqlite_conn = None


    def get_json(self, patron_record_num):
        self.open_db_connections()
        cursor = self.sqlite_conn.cursor()
        cursor.execute(self.sql_compute_savings, (int(patron_record_num), int(patron_record_num)))
        data = cursor.fetchone()
        if (data[0] != None):
            return {
                'patron_record_num': data[0],
                'total_savings': data[1],
                'min_date_epoch': data[2],
                'count_titles': data[3]
            }
        else:
            # return a null value, (make sure to set http 404 code for no patron info found)
            return None

        
    def get_img(self, patron_record_num):
        # these libraries are only used for producing the image ... lazy load them
        from PIL import Image, ImageDraw, ImageFont
        import time
        import os

        # check if there's an output directory, and create it if it doesn't exist
        self.output_path = 'output'
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        self.open_db_connections()
        cursor = self.sqlite_conn.cursor()
        cursor.execute(self.sql_compute_savings, (int(patron_record_num), int(patron_record_num)))
        data = cursor.fetchone()
        if (data[0] != None):
            file_name = self.output_path + '/{}_patron_savings.png'.format(patron_record_num)
            img = Image.new(
                'RGB',
                (300, 110), # width, height
                color = (255, 255, 255) # R, G, B
            )
            d = ImageDraw.Draw(img)
            d.text(
                xy = (10,10), #
                text = 'By using The Public Library\nof Cincinnati and Hamilton County,\nyou have saved approximatly\n${0:.2f} Since {1}\nCha-ching!!!'.format(
                    data[1],
                    time.strftime('%m/%d/%Y',  time.gmtime(data[2])) # data[2]
                ), # text
                font = ImageFont.truetype('UbuntuMono-Bold.ttf', 15), # font 
                fill = (0, 0, 0) # fill 
            )
            img.save(file_name, format='png')
            return file_name
        else:
            # return a null value, (make sure to set http 404 code for no patron info found)
            return None


    #~ the destructor
    def __del__(self):
        # if the sqlite connection is still open, and we can, commit any uncommited results
        # ...although, if reading database in read-only mode, then this shouldn't matter
        if self.sqlite_conn:
            if hasattr(self.sqlite_conn, 'commit'):
                self.sqlite_conn.commit()
        self.close_connections()
        print("done.")


# set up the routes for the API
# this should be only used for testing purposes only ...it's better to serve javascript from a webserver like apache
patron_savings = PatronSavings()

@app.route('/js/<path:path>')
def send_js(path):
    return send_from_directory('js', path)


# this route produces a json response (note that jsonify also sets the `mimetype='application/json'`)
@app.route('/get/patron_savings/<int:patron_record_num>')
def get_json_patron_savings(patron_record_num):
    patron_record_data = patron_savings.get_json(patron_record_num)
    if (patron_record_data):
        return jsonify(patron_record_data)
    else:
        return jsonify(error=404), 404


@app.route('/get/patron_savings/img/<int:patron_record_num>')
def get_json_patron_savings_img(patron_record_num):
    file_name = patron_savings.get_img(patron_record_num)
    if (file_name):
        return send_file(file_name, mimetype='image/png')
        # TODO: delete the file?
    else:
        # return jsonify(None)
        return jsonify(error=404), 404

if __name__ == '__main__':
    # note: this is only for testing, but in order to test on encore (which loads account info over https, we need to serve our API over https)
    # TODO: get this endpoint running over
    app.run(debug=True, host='0.0.0.0', ssl_context='adhoc')