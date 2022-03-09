import featuretools as ft
import pandas as pd
from unittest.mock import patch

import pytest
import autonormalize as an


def test_ft_mock_customer():
    df = ft.demo.load_mock_customer(n_customers=80, n_products=50, n_sessions=200,
                                    n_transactions=10000, return_single_table=True)

    entityset = an.auto_entityset(df, name="Customer Transactions", time_index='transaction_time')

    assert set(entityset['transaction_id'].columns) == set(['transaction_id', 'session_id', 'transaction_time',
                                                            'product_id', 'amount'])

    assert set(entityset['product_id'].columns) == set(['product_id', 'brand'])

    assert set(entityset['session_id'].columns) == set(['session_id', 'customer_id', 'device', 'session_start'])

    assert set(entityset['customer_id'].columns) == set(['customer_id', 'zip_code', 'join_date', 'birthday'])

    assert set([str(rel) for rel in entityset.relationships]) == set(['<Relationship: transaction_id.session_id -> session_id.session_id>',
                                                                      '<Relationship: transaction_id.product_id -> product_id.product_id>',
                                                                      '<Relationship: session_id.customer_id -> customer_id.customer_id>'])


@patch("autonormalize.autonormalize.auto_entityset")
def test_normalize_entityset(auto_entityset):
    df1 = pd.DataFrame({"test": [0, 1, 2]})
    df2 = pd.DataFrame({"test": [0, 1, 2]})
    accuracy = 0.98

    es = ft.EntitySet()

    error = "This EntitySet is empty"
    with pytest.raises(ValueError, match=error):
        an.normalize_entityset(es, accuracy)

    es.add_dataframe(df1, "df")

    df_out = es.dataframes[0]

    an.normalize_entityset(es, accuracy)

    auto_entityset.assert_called_with(df_out, accuracy, index=df_out.ww.index, name=es.id, time_index=df_out.ww.time_index)

    es.add_dataframe(df2, "df2")

    error = "There is more than one dataframe in this EntitySet"
    with pytest.raises(ValueError, match=error):
        an.normalize_entityset(es, accuracy)
