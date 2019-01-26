"""
Entry point to wp engine coding test.

The implementation combines results from api and the csv file to write a single
combined output to a file whose path is provided by the user.

To call this function:
   python wp_engine.py --input '<fully qualified_file_path_to_input_csv_file>' --output '<fully qualified path to output csv>'  # noqa: E501
"""


import argparse
import csv
import datetime
import itertools
import sys
import requests


_ACCOUNTS_URL = 'http://interview.wpengine.io/v1/accounts/{account_id}'


def fetch_account_status(account_id):
    """Makes the http request ot fetch account status for account id.

    Args:
        account_id: integer; account id for which the accounts information is
            to be fetched

    Returns:
        dictionary representing representing the parsed output
    """
    res_object = requests.get(_ACCOUNTS_URL.format(account_id=account_id))
    return res_object.json() if res_object.status_code == 200 else {}


def read_csv_file(input_csv_file_path):
    """Reads a csv file to return a tuple of csv rows.

    Args:
        input_csv_file_path: fully qualified path of the
            input csv file to be read

    Yields:
        tuple representing the account id, first name, and created date in that
            order
    """
    with open(input_csv_file_path, 'r', encoding='utf-8') as file_path:
        csv_reader = csv.reader(file_path)
        for row in itertools.islice(csv_reader, 1, None):
            yield (
                int(row[0]), row[2],
                datetime.datetime.strftime(
                    datetime.datetime.strptime(row[-1], '%m/%d/%y'),
                    '%Y-%m-%d'))


def collate_similar_data(input_csv_file_path, output_file_path):
    """Collates input data from multiple resources to write to putput file.

    Args:
        input_csv_file_path: fully qualified file path of the input
            file to read
        output_csv_file_path: fully qualified path of the output file
            path to be written to
    """
    with open(output_file_path, 'w') as file_object:
        csv_writer = csv.writer(file_object, delimiter=',')
        csv_writer.writerow(
            ('Account ID', 'First Name', 'Created On', 'Status',
             'Status Set On'))
        for csv_row in read_csv_file(input_csv_file_path):
            if not csv_row:
                continue
            account_status = fetch_account_status(csv_row[0])
            csv_writer.writerow(csv_row + (
                account_status.get('status') or '',
                datetime.datetime.strftime(
                    datetime.datetime.strptime(
                        account_status.get('created_on'), '%Y-%m-%d'),
                    '%Y-%m-%d') if account_status.get('created_on') else ''))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        help='Fully qualified path of input file name',
                        required='True')
    parser.add_argument('--output',
                        help='Fully qualified path of output file name',
                        required='True')
    arguments = parser.parse_args(sys.argv[1:])
    collate_similar_data(arguments.input, arguments.output)
