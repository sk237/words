import io
import unittest
from unittest import (
    mock,
    TestCase,
)

import elasticsearch
from elasticmock import (
    elasticmock,
    FakeElasticsearch,
)

from elasticsearch import NotFoundError

from word.service.search_service import SearchService


class SearchServiceTest(TestCase):

    @elasticmock
    def setUp(self):
        super().setUp()
        self.index = 'key'
        self.body = {
            'key': 'value'
        }
        self.es = elasticsearch.Elasticsearch(hosts=[{'host': 'localhost', 'port': 9200}])
        self.search_service = SearchService(self.es, self.index)
        self.response = {
            'hits': {
                'hits': [
                    {
                        '_source': {'word': 'value'}
                    },
                ]
            }
        }

    def test_should_create_fake_es_instance(self):
        self.assertIsInstance(self.es, FakeElasticsearch)

    @unittest.mock.patch('elasticmock.fake_indices.FakeIndicesClient.exists')
    def test_should_raise_not_found_exception_when_index_does_not_exist(self, mocked_exists):
        mocked_exists.return_value(False)
        with self.assertRaises(NotFoundError):
            self.search_service.run(key='key', value='value', size=1)

    @unittest.mock.patch('elasticmock.fake_indices.FakeIndicesClient.exists')
    @unittest.mock.patch('elasticmock.FakeElasticsearch.search')
    def test_elasticsearch_search_is_called(self, mocked_exists, mocked_search):
        mocked_exists.return_value(False)
        self.search_service.run(key='key', value='value', size=1)
        mocked_search.assert_called_once()

    @unittest.mock.patch('elasticmock.fake_indices.FakeIndicesClient.exists')
    @unittest.mock.patch('elasticmock.FakeElasticsearch.search')
    @unittest.mock.patch('word.service.search_service.SearchService._print_response')
    def test_search_service__print_response_is_called(self, mocked_exists, _, mocked_print_response):
        mocked_exists.return_value(True)
        self.search_service.run(key='key', value='value', size=1)
        mocked_print_response.assert_called_once()

    @unittest.mock.patch('sys.stdout', new_callable=io.StringIO)
    def test_echo_response(self, mock_stdout):
        self.search_service._print_response(res=self.response)
        self.assertEqual(mock_stdout.getvalue(), '-*-' * 30 + '\nword: value\n\n' + '-*-' * 30 + '\n')
