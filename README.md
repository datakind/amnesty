amnesty
=======

DataKind NYC DataDive Amnesty International project

## Requirements
You'll need git to clone this repository.  If you don't have git install, check out [this guide](http://git-scm.com/book/en/Getting-Started-Installing-Git).  You'll also need mongodb and pymongo to build the csvs and database locally.

## Code
This repo is the home for all project-related code.  Folders for munging, analysis, and visualization code have also been created.  Putting code in its respective folder will help everyone stay organized and productive.  A requrements.txt file has also been included.  If your scripts require packages please add to this file.  (If you're not using python, obviously add any other requirements files as well!)  

## Goals, Tasks, & Documentation
Information about the project can be found on the [project hackpad](https://nycdatadive2013.hackpad.com/AMNESTY-INTERNATIONAL-Text-Analysis-of-Humanitarian-Emergencies-YH0NV2A8HUj).  There you'll find details about the project Data Ambassadors, volunteers, tasks, and goals.  

## Data
All of the data for dive-related tasks can be found on the [project dropbox](https://www.dropbox.com/home/Amnesty%20Public).  If you'd like to add data files talk to a Data Ambassador and they will share the folder with you.

To build the data locally (on a *nix system):
``` bash
pip install -r requirements.txt
cd data_munging
python parse_lotus_database.py
```
