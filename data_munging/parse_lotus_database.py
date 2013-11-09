#!/usr/local/Cellar/python/2.7.2/bin/python
"""
This script extracts features from the raw Urgent Action files and writes them
to a new file.

Summary of the output so far:

      document           id                                             subject     
 Min.   :    2          :  239                                            :  203  
 1st Qu.: 5470   139/11 :   12   stop action to ex 13/98 on iran          :    3  
 Median : 8910   347/09 :   12   ua 152/12 on china                       :    3  
 Mean   : 8374   119/12 :   11   ua 156/12 on peru (issued on 1 june 2012):    3  
 3rd Qu.:11660   22/01  :   11   ua 313/98 on mexico                      :    3  
 Max.   :14410   32/01  :   11   1st update to ua 258/05 on syria         :    2  
                 (Other):10704   (Other)                                  :10783  

                                 category         country          gender     
                                   :  308   usa     :1140           :10971  
 quotes                            :   16   iran    : 814   m       :   12  
 death penalty                     :    9   colombia: 508   both    :    5  
 fear for safety                   :    8   mexico  : 485   all male:    2  
 death penalty|ex 84/98|philippines:    7   syria   : 400   f       :    2  
 death penalty|usa                 :    7   nepal   : 382   all m   :    1  
 (Other)                           :10645   (Other) :7271   (Other) :    7  

     appeal_date        issue_date           action    
 asap      :7544             :9851              :6797  
           :2307   2012-06-01:  10   stop action: 744  
 2012-06-01:  10   2012-10-25:  10   update     :3459  
 2012-10-25:  10   2012-05-11:   9                     
 2012-05-11:   9   2012-05-18:   9                     
 2012-05-18:   9   2011-09-13:   8                     
 (Other)   :1111   (Other)   :1103                     
"""

import os
import re
import csv
import datetime

INPUT_FILE = "/data/datakind/AI/Lotus Database.txt"
OUTPUT_DIR = "/data/datakind/AI/lotus"

BAD_CHARACTER_REGEX = re.compile(r'[\r\xbb\xbf\xef\xef\xbf\xbd]')


class UADoc(object):

    __APPEAL_DATE_REGEX = re.compile(r"please send appeals before *([0-9]{1,2}) ?([a-z]+) ([0-9]{4})")
    __ISSUE_DATE_REGEX  = re.compile(r"issue date: ([0-9]{1,2}) ?([a-z]+) ([0-9]{4})")
    __COUNTRY_REGEX     = re.compile(r"subject: *.+ on (.+)$")
    __RE_SUBJECT        = re.compile("subject: *(.+)")
    __GENDER_REGEX      = re.compile("gender m/f: *(.+)")
    __CATEGORY_REGEX    = re.compile("categories: *(.+)")

    # a total hack to fix typos.
    __STRING_TRANSLATION = [
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
        self.category    = ""
        self.id          = ""
        self.action      = ""

    def addline(self, line):
        """
        As we add lines, this method will parse it.
        """
        line = self.cleanup_text(line)
        if self.subject == "":
            self.parse_subject(line)

        if self.appeal_date == "":
            if "please send appeals to arrive as quickly as possible" in line or "please send appeals immediately" in line:
                self.appeal_date = "asap"
            else:
                self.appeal_date = self.__extract_date(line, self.__ISSUE_DATE_REGEX)

        if self.issue_date == "":
            self.issue_date = self.__extract_date(line, self.__ISSUE_DATE_REGEX)

        if self.gender == "":
            self.gender = self.match_line(line, self.__GENDER_REGEX)

        if self.category == "":
            self.category = self.match_line(line, self.__CATEGORY_REGEX).replace(",", "|")

        self.text += line + "\n"



    def parse_subject(self, line):
        self.subject = self.match_line(line, self.__RE_SUBJECT)
        if self.subject != "":
            # get the ID
            m = re.search(r"([0-9]{1,3}/[0-9]{1,3})", self.subject)
            if m is not None:
                self.id = m.group(1)
            
            # get the action
            if "stop action" in line:
                self.action = "stop action"
            elif "update" in line:
                self.action = "update"

            # get the country
            self.country = self.match_line(line, self.__COUNTRY_REGEX)
            if "/" in self.country:
                print self.country
                self.country, self.region = self.country.split("/", 1)
            elif re.search(r"(.+) \(.+\)", self.country) is not None:
                self.region = re.search(r"(.+) \((.+)\)", self.country).group(2)
                self.country = re.search(r"(.+) \((.+)\)", self.country).group(1)

    def cleanup_text(self, line):
        """
        Performs some substitutions for country names or known typos
        """
        for k, v in self.__STRING_TRANSLATION:
            if k in line:
                text = line.replace(k, v)
        return line

    def match_line(self, line, reg, grp=1):
        match = reg.search(line)
        if match is not None:
            return match.group(grp)
        return ""

    def __extract_date(self, line, dt_regex, as_string=True):
        dt = dt_regex.search(line)
        if dt is not None:
            date_string = " ".join([dt.group(1), dt.group(2), dt.group(3)])
            return_date = datetime.datetime.strptime(date_string, "%d %B %Y")
            if as_string == True:
                return return_date.strftime("%Y-%m-%d")
            else:
                return return_date
        else:
            if as_string == True:
                return ""
            else:
                return datetime.datetime.fromtimestamp(0)

    def __len__(self):
        return len(self.text)


def debug_line(line):
    # return
    x = re.sub(r"[a-z0-9 ,;\.:=\\\/\(\)\$\-\+@]", "", line)
    if x != "":
        print x


if __name__ == "__main__":
    fout = csv.writer(open(os.path.join(OUTPUT_DIR, "output.csv"), "wb"))
    fout.writerow([
        "document", "id", "subject",
        "category", "country", "gender",
        "appeal_date", "issue_date", "action"
    ])

    fin = open(INPUT_FILE, "r")
    file_count = 0
    doc = UADoc()
    for line_number, line in enumerate(fin.readlines()):

        line = BAD_CHARACTER_REGEX.sub("", line.strip())

        if line.startswith("from:") or "$file:" in line:
            if doc.text != "":
                # print "writing document", file_count
                # print "document length:", len(doc)
                # print "subject:", doc.subject
                # print "country:", doc.country
                # print "gender:", doc.gender
                # print "appeal_date:", doc.appeal_date
                # print "issue_date:", doc.appeal_date
                # print "---------------------------"
                fout.writerow([
                    file_count, doc.id, doc.subject,
                    doc.category, doc.country, doc.gender,
                    doc.appeal_date, doc.issue_date, doc.action
                ])
                open(os.path.join(OUTPUT_DIR, str(file_count)), "wb").write(doc.text)
            doc = UADoc()
            file_count += 1
            continue

        doc.addline(line)

        if line_number % 10000 == 0:
            print "lines:", line_number/1000, "documents:", file_count
    del(fout)