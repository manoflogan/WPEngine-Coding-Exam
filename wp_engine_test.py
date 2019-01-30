import datetime
import os
from unittest import mock

import pytest

import wp_engine


@pytest.fixture(scope='module')
def input_csv_file():
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(current_path, 'input.csv'))


@pytest.fixture(scope='module')
def output_csv_file():
    current_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.normpath(os.path.join(current_path, 'output.csv'))


def test_read_csv_file(input_csv_file):
    expected = [
        (12345, 'Lex', '2011-01-12'),
        (8172, 'Victor', '2014-11-19'),
        (1924, 'Max', '2012-02-29'),
        (222222, 'Ra\'s', '2012-03-01'),
        (48213, 'Wilson', '2015-07-07'),
        (918299, 'Norman', '2014-04-29'),
        (88888, 'Otto', '2013-08-08')]
    actual = [row for row in wp_engine.read_csv_file(input_csv_file)]
    assert actual == expected


async def test_fetch_account_status__success():
    response_object = mock.Mock()
    response_object.status_code = 200
    expected = {
        'account_id': 12345,
        'status': 'fraud',
        'created_on': '2015-03-20'}
    response_object.json = mock.MagicMock(return_value=expected)
    with mock.patch('requests.get',
                    return_value=response_object) as mock_request:
        response = await (wp_engine.fetch_account_status(12345))
        assert (
            mock_request.call_args[0][0] == (
                'http://interview.wpengine.io/v1/accounts/12345'))
        assert mock_request.call_count == 1
        assert response == expected


async def test_fetch_account_status__failure():
    response_object = mock.Mock()
    response_object.status_code = 500
    with mock.patch('requests.get',
                    return_value=response_object) as mock_request:
        response = await (wp_engine.fetch_account_status(12345))
        assert (
            mock_request.call_args[0][0] == (
                'http://interview.wpengine.io/v1/accounts/12345'))
        assert mock_request.call_count == 1
        assert response == {}


def read_csv_file(input_file_path):
    rows = [(12345, 'lexcorp', 'Lex', datetime.date(2011, 1, 12))]
    for row in rows:
        yield row


async def test_collate_similar_data(input_csv_file, output_csv_file):
    try:
        rows = []
        csv_writer_object = mock.Mock()
        csv_writer_object.writerow = lambda row: rows.append(row)
        with mock.patch('csv.writer',
                        return_value=csv_writer_object) as mock_writer, \
                mock.patch(
                    'wp_engine.read_csv_file',
                    side_effect=read_csv_file) as mock_read_csv_file, \
                mock.patch(
                    'wp_engine.fetch_account_status', return_value={
                        'account_id': 12345,
                        'status': 'fraud',
                        'created_on': '2015-03-20'
                    }) as mock_fetch_account_status:
            await (wp_engine.collate_similar_data(
                input_csv_file, output_csv_file))
            assert mock_writer.call_count == 1
            assert mock_writer.call_args[0][0] is not None
            assert mock_read_csv_file.call_count == 1
            assert mock_read_csv_file.call_args[0][0] == input_csv_file
            assert mock_fetch_account_status.call_count == 1
            assert mock_fetch_account_status.call_args[0][0] == 12345
            assert rows == [
                ('Account ID', 'First Name', 'Created On', 'Status',
                 'Status Set On'),
                (12345, 'lexcorp', 'Lex', datetime.date(2011, 1, 12), 'fraud',
                 '2015-03-20')]
    finally:
        os.remove(output_csv_file)


async def test_collate_similar_data__missing_input_file(output_csv_file):
    rows = []
    csv_writer_object = mock.Mock()
    csv_writer_object.writerow = lambda row: rows.append(row)
    with mock.patch('csv.writer',
                    return_value=csv_writer_object) as mock_writer, \
            mock.patch(
                'wp_engine.read_csv_file',
                side_effect=read_csv_file) as mock_read_csv_file, \
            mock.patch(
                'wp_engine.fetch_account_status', return_value={
                    'account_id': 12345,
                    'status': 'fraud',
                    'created_on': '2015-03-20'
                }) as mock_fetch_account_status:
        await (wp_engine.collate_similar_data(None, output_csv_file))
        assert mock_writer.call_count == 0
        assert mock_read_csv_file.call_count == 0
        assert mock_fetch_account_status.call_count == 0
        assert rows == []


async def test_collate_similar_data__missing_output_file(input_csv_file):
    rows = []
    csv_writer_object = mock.Mock()
    csv_writer_object.writerow = lambda row: rows.append(row)
    with mock.patch('csv.writer',
                    return_value=csv_writer_object) as mock_writer, \
            mock.patch(
                'wp_engine.read_csv_file',
                side_effect=read_csv_file) as mock_read_csv_file, \
            mock.patch(
                'wp_engine.fetch_account_status', return_value={
                    'account_id': 12345,
                    'status': 'fraud',
                    'created_on': '2015-03-20'
                }) as mock_fetch_account_status:
        await (wp_engine.collate_similar_data(input_csv_file, None))
        assert mock_writer.call_count == 0
        assert mock_read_csv_file.call_count == 0
        assert mock_fetch_account_status.call_count == 0
        assert rows == []


async def test_collate_similar_data__missing_http_request_data(
        input_csv_file, output_csv_file):
    try:
        rows = []
        csv_writer_object = mock.Mock()
        csv_writer_object.writerow = lambda row: rows.append(row)
        with mock.patch('csv.writer',
                        return_value=csv_writer_object) as mock_writer, \
                mock.patch(
                    'wp_engine.read_csv_file',
                    side_effect=read_csv_file) as mock_read_csv_file, \
                mock.patch(
                    'wp_engine.fetch_account_status',
                    return_value={}) as mock_fetch_account_status:
            await (wp_engine.collate_similar_data(input_csv_file,
                                                  output_csv_file))
            assert mock_writer.call_count == 1
            assert mock_read_csv_file.call_count == 1
            assert mock_fetch_account_status.call_count == 1
            assert rows == [
                ('Account ID', 'First Name', 'Created On', 'Status',
                 'Status Set On'),
                (12345, 'lexcorp', 'Lex', datetime.date(2011, 1, 12), '',
                 '')]
    finally:
        os.remove(output_csv_file)
