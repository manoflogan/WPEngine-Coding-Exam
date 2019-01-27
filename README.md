# WP Engine Coding Exercise [![Build Status](https://travis-ci.org/manoflogan/WPEngine-Coding-Exam.svg?branch=master)](https://travis-ci.org/manoflogan/WPEngine-Coding-Exam)

### Table of Contents

- [Assignment](Assignment.md)
- [Requirements](#requirements)
- [Setup](#setup)
- [Execution](#execution)

### Requirements

* Python 3.6.x
* `requests` package

### Setup

* Install Python 3.6.x. You can use your favourite tool to install the software (HomeBrew, pyenv) etc.

* Set up virtualenv with the following command ``virtualenv -p `which python3` env``. Activate the virtual environment using the command `source env/bin/activate`

* Install the python packages required by the project by executing `pip install -r requirements.txt`.

## Execution

* Run the command ` python wp_engine.py --input '<fully qualified_file_path_to_input_csv_file>' --output '<fully qualified path to output csv>'` to execute the program.

* Run the command `pytest` to run the unit tests. The code coverage reports will be found under `html_coverage_report` directory in the main project.
