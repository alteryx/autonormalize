import os  # noqa isort:skip
import sys  # noqa isort:skip
sys.path.append(os.path.abspath(os.path.join('..', '..',)))  # noqa

import featuretools as ft  # noqa isort:skip

import autonormalize as an  # noqa isort:skip


def test_ft_mock_customer():
    df = ft.demo.load_mock_customer(n_customers=80, n_products=50, n_sessions=200,
                                    n_transactions=10000, return_single_table=True)

    entityset = an.auto_entityset(df, name="Customer Transactions", time_index='transaction_time')

    assert set(entityset['transaction_id'].df.columns) == set(['transaction_id', 'session_id', 'transaction_time',
                                                              'product_id', 'amount'])

    assert set(entityset['product_id'].df.columns) == set(['product_id', 'brand'])

    assert set(entityset['session_id'].df.columns) == set(['session_id', 'customer_id', 'device', 'session_start'])

    assert set(entityset['customer_id'].df.columns) == set(['customer_id', 'zip_code', 'join_date', 'date_of_birth'])

    assert set([str(rel) for rel in entityset.relationships]) == set(['<Relationship: transaction_id.session_id -> session_id.session_id>',
                                                                      '<Relationship: transaction_id.product_id -> product_id.product_id>',
                                                                      '<Relationship: session_id.customer_id -> customer_id.customer_id>'])
