# Copyright (c) Microsoft Corporation
# Licensed under the MIT License.

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
import pytest
from tests.common_utils import (create_housing_data, create_iris_data,
                                create_sklearn_random_forest_classifier,
                                create_sklearn_random_forest_regressor)

from responsibleai import RAIInsights

LABELS = 'labels'


class TestRAIInsightsLargeData(object):

    def do_large_data_validations(self, rai_insights):
        assert rai_insights._large_test is not None
        assert len(rai_insights.test) + 1 == len(rai_insights._large_test)

        assert rai_insights._large_predict_output is not None
        assert len(rai_insights.test) + 1 == len(
            rai_insights._large_predict_output)
        if rai_insights.task_type == 'classification:':
            assert rai_insights._large_predict_proba_output is not None
            assert len(rai_insights.test) + 1 == len(
                rai_insights._large_predict_proba_output)

        dataset = rai_insights._get_dataset()
        assert dataset.is_large_data_scenario
        assert not dataset.use_entire_test_data

        filtered_small_data = rai_insights.get_filtered_test_data(
            [], [], use_entire_test_data=False)
        assert len(filtered_small_data) == len(rai_insights.test)

        filtered_large_data = rai_insights.get_filtered_test_data(
            [], [], use_entire_test_data=True)
        assert len(filtered_large_data) == len(rai_insights.test) + 1

    def validate_rai_insights_for_large_data(
            self, model, train_data, test_data,
            target_column,
            categorical_features, task_type):

        with pytest.warns(
                UserWarning,
                match="The size of test set {0} is greater than "
                      "supported limit of {1}. Computing insights"
                      " for first {1} samples "
                      "of test set".format(len(test_data),
                                           len(test_data) - 1)):
            rai_insights = RAIInsights(
                model, train_data, test_data,
                LABELS,
                categorical_features=categorical_features,
                task_type=task_type,
                maximum_rows_for_test=len(test_data) - 1)

        self.do_large_data_validations(rai_insights)

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'rai_test_path'
            # save the rai_insights
            rai_insights.save(path)

            # load the rai_insights
            rai_insights = RAIInsights.load(path)

            self.do_large_data_validations(rai_insights)

    def test_rai_insights_large_data_classification(self):
        train_data, test_data, y_train, y_test, feature_names, classes = \
            create_iris_data()
        model = create_sklearn_random_forest_classifier(train_data, y_train)

        train_data[LABELS] = y_train
        test_data[LABELS] = y_test

        self.validate_rai_insights_for_large_data(
            model, train_data, test_data, LABELS, [], 'classification')

    def test_rai_insights_large_data_regression(self):
        train_data, test_data, y_train, y_test, feature_names = \
            create_housing_data()
        train_data = pd.DataFrame(train_data, columns=feature_names)
        test_data = pd.DataFrame(test_data, columns=feature_names)
        model = create_sklearn_random_forest_regressor(train_data, y_train)
        train_data[LABELS] = y_train
        test_data[LABELS] = y_test

        self.validate_rai_insights_for_large_data(
            model, train_data, test_data, LABELS, [], 'regression')


class TestRAIInsightsNonLargeData(object):

    def do_non_large_data_validations(self, rai_insights):
        assert rai_insights._large_test is None
        assert rai_insights._large_predict_output is None
        assert rai_insights._large_predict_proba_output is None
        dataset = rai_insights._get_dataset()
        assert not dataset.is_large_data_scenario
        assert not dataset.use_entire_test_data

        filtered_small_data = rai_insights.get_filtered_test_data(
            [], [], use_entire_test_data=False)
        assert len(filtered_small_data) == len(rai_insights.test)

        filtered_large_data = rai_insights.get_filtered_test_data(
            [], [], use_entire_test_data=True)
        assert len(filtered_large_data) == len(rai_insights.test)

    def validate_rai_insights_for_non_large_data(
            self, model, train_data, test_data,
            target_column,
            categorical_features, task_type):

        rai_insights = RAIInsights(
            model, train_data, test_data,
            LABELS,
            categorical_features=categorical_features,
            task_type=task_type)

        self.do_non_large_data_validations(rai_insights)

        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / 'rai_test_path'
            # save the rai_insights
            rai_insights.save(path)

            # load the rai_insights
            rai_insights = RAIInsights.load(path)

            self.do_non_large_data_validations(rai_insights)

    def test_rai_insights_non_large_data_classification(self):
        train_data, test_data, y_train, y_test, feature_names, classes = \
            create_iris_data()
        model = create_sklearn_random_forest_classifier(train_data, y_train)

        train_data[LABELS] = y_train
        test_data[LABELS] = y_test

        self.validate_rai_insights_for_non_large_data(
            model, train_data, test_data, LABELS, [], 'classification')

    def test_rai_insights_non_large_data_regression(self):
        train_data, test_data, y_train, y_test, feature_names = \
            create_housing_data()
        train_data = pd.DataFrame(train_data, columns=feature_names)
        test_data = pd.DataFrame(test_data, columns=feature_names)
        model = create_sklearn_random_forest_regressor(train_data, y_train)
        train_data[LABELS] = y_train
        test_data[LABELS] = y_test

        self.validate_rai_insights_for_non_large_data(
            model, train_data, test_data, LABELS, [], 'regression')