#!/usr/local/Cellar/python/2.7.2/bin/python
"""
This script extracts features from the raw Urgent Action files and writes them
to a new file.
Summary of the output so far:

      document              id                                           subject
 Min.   :    2          :  239                                            :  203
 1st Qu.: 5470   139/11 :   12   stop action to ex 13/98 on iran          :    3
 Median : 8910   347/09 :   12   ua 152/12 on china                       :    3
 Mean   : 8374   119/12 :   11   ua 156/12 on peru (issued on 1 june 2012):    3
 3rd Qu.:11660   22/01  :   11   ua 313/98 on mexico                      :    3
 Max.   :14410   32/01  :   11   1st update to ua 258/05 on syria         :    2
                 (Other):10704   (Other)                                  :10783
                               category         country          gender
                                   :  204   usa     : 986           :10971
 quotes                            :   16   iran    : 697   m       :   12
 death penalty                     :    9   colombia: 502   both    :    5
 fear for safety                   :    8   mexico  : 458   all male:    2
 death penalty|ex 84/98|philippines:    7   syria   : 375   f       :    2
 death penalty|usa                 :    7   nepal   : 358   all m   :    1
 (Other)                           :10749   (Other) :7624   (Other) :    7
     appeal_date         issue_date           action          all_dates
           :10008             :7244              :6797             :  490
 2012-05-03:    9   1998-10-21:  11   stop action: 744   2002-05-10:    5
 2012-12-06:    9   1999-01-29:  10   update     :3459   1999-01-29:    4
 2012-06-22:    8   2003-02-21:  10                      2000-11-06:    4
 2012-07-13:    8   2005-05-25:  10                      2001-07-03:    4
 2012-06-29:    7   2012-06-01:  10                      2002-03-28:    4
 (Other)   :  951   (Other)   :3705                      (Other)   :10489
"""

import os
import re
import csv
import sys
import datetime
USE_DB = False
if "mongo" in sys.argv:
    USE_DB = True
    import pymongo


INPUT_FILE = "../raw_data/lotus_database.txt"
OUTPUT_FILE = "../cleaned_data/lotus_database.csv"
OUTPUT_DIR = "../cleaned_data/ua_files"

BAD_CHARACTER_REGEX = re.compile(r'[\r\xbb\xbf\xef\xef\xbf\xbd]')


class UADoc(object):

    ANY_DATE_REGEX    = re.compile(r"([0-9]{1,2}) *([a-z]+) +([0-9]{4})")
    APPEAL_DATE_REGEX = re.compile(r"please send appeals before *?([0-9]{1,2}) *?([a-z]+?) +?([0-9]{4})")
    GENDER_REGEX      = re.compile(r"gender m/f: *(.+?)\|")
    CATEGORY_REGEX    = re.compile(r"\|categories: *(.+?)\|")
    BODY_REGEX        = re.compile(r"\|body:(.+?)\|[^\| ]+:")

    # a total hack to fix typos.
    STRING_TRANSLATION = [
        ('united states of america', 'usa'),
        ('united states', 'usa'),
        ('occupied palestinian territories', 'israel/opt'),
        ('israel/occupied palestinian territory', 'israel/opt'),
        ('israel and the occupied palestinian territories', 'israel/opt'),
        ('occupied palestinian territories', 'israel/opt'),
        ('israel/occupied palestinian territories', 'israel/opt'),
        ('palestine', 'israel/opt'),
        ('palestinian authority', 'israel/opt'),
        ('israel', 'israel/opt'),
        ('republic of yemen', 'yemen'),
        ('m\xc9xico', 'mexico'),
        ('russia federation', 'russia'),
        ('russian federation', 'russia'),
        ('kingdom of saudi arabia', 'saudi arabia'),
        ('sepember', 'september'),
        ('septmember', 'september')
    ]

    def __init__(self):
        self.text        = ""
        self.subject     = ""
        self.appeal_date = ""
        self.issue_date  = ""
        self.country     = ""
        self.gender      = ""
        self.category    = [""]
        self.id          = ""
        self.action      = ""

    def addline(self, line):
        """
        As we add lines, this method will parse it.
        """
        line = self.cleanup_text(line)
        self.text += line + "|"

    def finalize(self):
        """
        Some things to run once the whole document has been (mostly) parsed.
        """
        line = self.text
        self.parse_subject()

        self.parse_country()

        self.parse_issue_date()

        self.appeal_date = self.extract_date(self.APPEAL_DATE_REGEX, match_offset=0)

        self.gender = self.match_line(self.GENDER_REGEX)

        self.category = self.match_line(self.CATEGORY_REGEX).split(",")

        body = self.match_line(self.BODY_REGEX)
        self.body = re.sub("\|+", "\n", body)

        # just grab every known date in the whole document
        dates = self.ANY_DATE_REGEX.findall(self.text)
        dates = map(self.format_date, dates)
        self.dates = list(dates)

    ISSUE_DATE_REGEX  = re.compile(r"issue date\: *?([0-9]{1,2}) *?([a-z]+?)[, ]*?([0-9]{2,4})")
    ISSUE_DATE_REGEX2 = re.compile(r"issued ?o?n? \(?([0-9]{1,2}) *?([a-z]+?) *?([0-9]{2,4})\)?")
    ISSUE_DATE_REGEX3 = re.compile(r"issued ([0-9]{1,2}) *?([a-z]+?) *?([0-9]{2,4})")
    ISSUE_DATE_REGEX4 = re.compile(r"\(([0-9]{1,2}) *?([a-z]+?) *?([0-9]{2,4})\)")
    ISSUE_DATE_REGEX5 = re.compile(r"issue date\: ([a-z]+?) *?([0-9]{1,2})[, ]*?([0-9]{2,4})")
    def parse_issue_date(self):
        """
        Issue dates come in a few different formats. We'll try them all.
        """
        self.issue_date_version = -1

        self.issue_date = self.extract_date(self.ISSUE_DATE_REGEX2, line=self.subject)
        if self.issue_date != "":
            self.issue_date_version = 0
            return

        self.issue_date = self.extract_date(self.ISSUE_DATE_REGEX2)

        if self.issue_date != "":
            self.issue_date_version = 1
            return

        self.issue_date = self.extract_date(self.ISSUE_DATE_REGEX3)

        if self.issue_date != "":
            self.issue_date_version = 2
            return

        self.issue_date = self.extract_date(self.ISSUE_DATE_REGEX)

        if self.issue_date != "":
            self.issue_date_version = 3
            return

        self.issue_date = self.extract_date(self.ISSUE_DATE_REGEX4, line=self.subject)

        if self.issue_date != "":
            self.issue_date_version = 4
            return

        match = self.ISSUE_DATE_REGEX5.search(self.text)
        if match is not None:
            self.issue_date = self.format_date((match.group(2), match.group(1), match.group(3)))

        if self.issue_date != "":
            self.issue_date_version = 5

    def extract_date(self, dt_regex, match_offset=0, line=None):
        """
        Extracts a date from the text and returns it in YYYY-MM-DD format.

        Input is a regular expression to use for the matching.
        """
        if line is None:
            line = self.text
        dt = dt_regex.search(line)
        if dt is not None:
            day = dt.group(1 + match_offset)
            month = dt.group(2 + match_offset)
            year = dt.group(3 + match_offset)
            return self.format_date((day, month, year))
        return ""

    SUBJECT_REGEX = re.compile(r"subject: *?(.+?)\|")
    def parse_subject(self):
        self.subject = self.match_line(self.SUBJECT_REGEX)
        if self.subject != "":
            # get the ID
            m = re.search(r"([0-9]{1,3}/[0-9]{1,3})", self.subject)
            if m is not None:
                self.id = m.group(1).strip()

            # get the action
            if "stop action" in self.subject:
                self.action = "stop action"
            elif "update" in self.subject:
                self.action = "update"

    COUNTRY_REGEX = re.compile(r"\|country: *?(.+?)\|")
    REGION_REGEX  = re.compile(r"(.+) \((.+)\)")
    COUNTRY_REGEX2 = re.compile(r"\|subject: *[^\|]+? on ([^\|]+)\|")
    def parse_country(self):
        # get the country
        self.country = self.match_line(self.COUNTRY_REGEX)
        if self.country == "":
            self.country = self.match_line(self.COUNTRY_REGEX2)

        # see if there's a region and split that out.
        if "/" in self.country:
            self.country, self.region = self.country.split("/", 1)
        elif self.REGION_REGEX.search(self.country) is not None:
            match = self.REGION_REGEX.search(self.country)
            self.country = match.group(1)
            self.region = match.group(2)



    def cleanup_text(self, line):
        """
        Performs some substitutions for country names or known typos
        """
        line = line.replace("|", "")
        for k, v in self.STRING_TRANSLATION:
            if k in line:
                text = line.replace(k, v)
        return line

    def match_line(self, reg, grp=1, line=None):
        if line is None:
            line = self.text
        match = reg.search(line)
        if match is not None:
            return match.group(grp).strip()
        return ""

    @staticmethod
    def format_date(dmy_tuple):
        try:
            day, month, year = dmy_tuple
            if len(year) == 2:
                year = "20" + year
            if len(day) == 1:
                day = "0" + day
            date_string = " ".join([day, month, year])
            return_date = datetime.datetime.strptime(date_string, "%d %B %Y")
            return return_date.strftime("%Y-%m-%d")
        except:
            return ""

    def __len__(self):
        return len(self.text)

    @staticmethod
    def is_document_break(line, previous_line):
        if "$file:" in line:
            return True
        if line.startswith("from:"):
            if "$file" in previous_line:
                return True
            return True

def main():

    # set up mongo db (running on localhost for now)
    if USE_DB:
        db = pymongo.Connection().datakind
        db.drop_collection("data")

    # set up the output directory for individual files
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    fout = csv.writer(open(OUTPUT_FILE, "wb"))
    fout.writerow([
        "document", "id", "subject",
        "category", "country", "gender",
        "appeal_date", "issue_date", "action","all_dates","body"
    ])

    fin = open(INPUT_FILE, "r")
    file_count = 0
    doc = UADoc()
    line = ""
    previous_line = ""

    for line_number, line in enumerate(fin.readlines()):

        # hold onto the previous line value. we'll need this in determining
        # document breaks
        if line != "":
            previous_line = line

        # grab the next line
        line = BAD_CHARACTER_REGEX.sub("", line.strip())

        # document breaks on "from:" or "$file:"
        if doc.is_document_break(line, previous_line):
            if doc.text != "":

                # all of the collection is done. Parse the document.
                doc.finalize()

                # write output to csv.
                fout.writerow([
                    file_count, doc.id, doc.subject,
                    "|".join(doc.category), doc.country, doc.gender,
                    doc.appeal_date, doc.issue_date, doc.action, "|".join(doc.dates), doc.body.replace("\n", "|")
                ])

                # write raw text to a file
                open(os.path.join(OUTPUT_DIR, str(file_count)), "wb").write(doc.text.replace("|", "\n"))

                # insert the data into mongo
                if USE_DB == True:
                    db.data.insert(doc.__dict__)

            # on to a new document
            doc = UADoc()
            file_count += 1

            continue
        # if it's not a new document, add the line to the existing one.
        doc.addline(line)

        if line_number % 10000 == 0:
            print "lines:", line_number, "documents:", file_count
    del(fout)

if __name__ == "__main__":
    main()