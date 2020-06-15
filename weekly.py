#!/user/bin/python3
# -*- coding: utf-8 -*-
# Copyright 2020 jbaten@i2rs.nl
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

version = "1.10"


import logging

logging.basicConfig(level=logging.DEBUG,
                    filename="weekly_" + version + ".log",
                    format="%(asctime)s:%(levelname)s:%(message)s")
import sys
import tkinter as tk
from tkinter import ttk
import psycopg2
import configparser
from pprint import pprint, pformat
import inspect
import time
import hashlib

logging.debug("Start initialisation")
now = time.strftime("%c")
logging.debug("Current date & time " + time.strftime("%c"))

class Weekly(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.read_config_file()
        self.create_widgets()
        self.whereami(inspect.stack()[0][3])
        self.root = root

    def read_config_file(self):
        self.whereami(inspect.stack()[0][3])
        # read config file
        configFile = "weekly.conf"
        config = configparser.ConfigParser()
        try:
            config.read(configFile)
            # read system vars
            self.DEBUG = config.get('system', 'debug')  # when true do not store invoice number into db!

            # Read database vars
            self.DB_HOST = config.get('db', 'host')
            self.DB_USER = config.get('db', 'user')
            self.DB_PASSWORD = config.get('db', 'password')
            self.DB_DATABASE = config.get('db', 'database')

        except:
            logging.critical("Error reading config file '" + configFile + "'.")
            print("Could not read config file. Program aborted.")
            sys.exit(1)

    ########################################################
    ### General Initialisation
    ########################################################

    def execute_db_query(self, query, parameters=()):
        """
        Method to execute database queries
        :param query:
        :param parameters:
        :return: list of dictionaries with fieldnames and values
        """
        self.whereami(inspect.stack()[0][3])

        try:
            conn = psycopg2.connect(dbname=self.DB_DATABASE, user=self.DB_USER, password=self.DB_PASSWORD,
                                    host=self.DB_HOST)
        except:
            errorstr = "ERROR: I am unable to connect to the database."
            logging.critical(errorstr)
            print(errorstr)
            sys.exit(1)

        cur = conn.cursor()
        try:
            logging.debug("db debug: \n=>query: " + pformat(query) + "\n=>parameters: " + pformat(parameters))
            cur.execute(query, parameters)

        except Exception as e:
            # e = sys.exc_info()[0]
            errorstr = "FATAL ERROR (" + str(e) + ")\n=>query: " + pformat(query) + "\n=>parameters: " + pformat(
                parameters)
            logging.critical(errorstr)
            self.message['text'] = str(e)
            print(errorstr)
            sys.exit(2)
        # Handle non returning queries
        if cur.description == None:
            result = []
        else:
            names = [d.name for d in cur.description]
            result = [dict(zip(names, row)) for row in cur.fetchall()]
        # query_result = cur.fetchall()
        # print("db debug: \n=>query result: " + pformat(query_result))
        logging.debug("db debug: \n=>query result: " + pformat(result))
        conn.commit()
        # return query_result
        return result

    def get_week_dicts(self, history_step):
        """
        Fill global weekdict with values from database
        :arg history_step: 0 is this week, -1 is previous week, etc.
        
        :return:
        """
        self.whereami(inspect.stack()[0][3])
        # This query is ugly AF. Maybe somebody can clean this up someday?
        query = """ select 
                    o.name , o.weeklyhours, 
                    ( select to_char(round(sum(tm2.time_unit/60),2), 'FM99990.00') from ticket_time_accountings as tm2,
                            tickets as t2,
                            organizations as o2
                    where   tm2.ticket_id=t2.id and t2.organization_id=o2.id and
                    o2.id=o.id and
                           extract(year from tm2.created_at) = extract(year from current_date) and
                           extract(week from tm2.created_at ) = extract(week from current_date) - %s ) as Time        
                    from 
                            ticket_time_accountings as tm,
                            tickets as t,
                            organizations as o
                    where   tm.ticket_id=t.id and t.organization_id=o.id 
                                   or o.weeklyhours is not null
                    group by o.id
                    order by o.id 
        """
        weekdict = self.execute_db_query(query, (history_step,))
        return weekdict

    def create_widgets(self):
        self.master.title("Weekly")
        self.pack(fill=tk.BOTH, expand=True)
        self.styling = ttk.Style()
        self.styling.theme_use('clam')
        self.styling.configure("red.Horizontal.TProgressbar", foreground='red', background='red')
        self.styling.configure("green.Horizontal.TProgressbar", foreground='green', background='green')
        self.styling.configure("orange.Horizontal.TProgressbar", foreground='orange', background='orange')

        label = "This should not be visible"

        dictlastweek = self.get_week_dicts(1)
        self.lastweek = ttk.LabelFrame(self, text='Last week', style='BLUE.TLabelframe')
        self.draw_my_frame(dictlastweek, self.lastweek, 1)
        self.lastweek.pack(side=tk.TOP)

        dictthisweek = self.get_week_dicts(0)
        self.thisweek = ttk.LabelFrame(self, text='This week', style='BLUE.TLabelframe')
        self.draw_my_frame(dictthisweek, self.thisweek, 0)
        self.thisweek.pack(side=tk.TOP)

        self.quit = tk.Button(self, text="QUIT", fg="blue", command=self.master.destroy)
        self.quit.pack(side="bottom")
        return

    def draw_my_frame(self, weekdict, myframe, week):
        """
        Should be a routine that draws widgets in a supplied frame
        """
        if len(weekdict) > 0:
            for line in weekdict:
                self.lineframe = tk.Frame(myframe)
                self.lineframe.pack(fill=tk.X)

                done = line["time"]
                # sanity check
                if done == None:
                    done = 0
                else:
                    done = float(done)

                target = line["weeklyhours"]
                # sanity check
                if target == None:
                    target = 0
                else:
                    target = float(target)

                name = line["name"]
                # Change name if demo = 1
                demo = 0
                if demo == 1:
                    hash = hashlib.sha1()
                    hash.update(str(name).encode('utf-8'))
                    name = hash.hexdigest()[:6] + " Inc."

                finalname = name + " (" + str(done)

                # only show when work is done or we need to work
                if done > 0 or target > 0:

                    finalname = finalname + "/" + str(target)
                    # Now we need to do some calculation
                    if target > 0:
                        mylength = int((done / target) * 100)
                    else:
                        mylength = 100
                    finalname = finalname + ")"

                    # Decide on font color
                    if week == 0 and target > 0 and done == 0:
                        fg = "red"
                    else:
                        fg = "black"

                    self.bedrijflabel = tk.StringVar()
                    self.label = tk.Label(self.lineframe, fg=fg, textvariable=self.bedrijflabel)
                    self.bedrijflabel.set(finalname)
                    self.label.pack(side="left")

                    # Decide on bar color
                    if week == 0:
                        if target > 0:
                            if done < target:
                                #pprint("make red 2")
                                color = "red.Horizontal.TProgressbar"
                            else:
                                #pprint("make green 2")
                                color = "green.Horizontal.TProgressbar"
                        else:
                            #pprint("make orange 2")
                            color = "orange.Horizontal.TProgressbar"
                    else:
                        color = ""
                    # self.label.grid(column=0,row=0)
                    self.progress = ttk.Progressbar(self.lineframe,
                                                    style=color,
                                                    orient="horizontal",
                                                    length=100,
                                                    mode='determinate',
                                                    value=mylength)
                    # self.progress.grid(column=1, row=0)
                    self.progress.pack(side="right")


        else:
            label = "No results for this week yet"
            self.msg = tk.Button(self)
            self.msg["text"] = label
            self.msg["command"] = "dummy"
            self.msg.pack(side="top")

        return

    def whereami(self, methodname):
        """
        Small diagnostic method to show what function I am running.
        :param methodname: name of method from call in start of method.
        :return:
        """
        logging.debug("####################################")
        logging.debug("### Entering " + methodname)
        logging.debug("####################################")
        return


# creating tkinter window 
root = tk.Tk()

# infinite loop
app = Weekly(master=root)
app.mainloop()
