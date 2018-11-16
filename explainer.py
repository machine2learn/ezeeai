from lime import lime_tabular


class Explainer:

    def __init__(self, train, training_labels, feature_names, class_names, categorical_features, categorical_names,  mode, verbose=True):

        self._mode = mode

        self._explainer = lime_tabular.LimeTabularExplainer(train,
                                                            feature_names=feature_names,
                                                            class_names=class_names,
                                                            categorical_features=categorical_features,
                                                            categorical_names=categorical_names,
                                                            training_labels=training_labels,
                                                            verbose=verbose,
                                                            mode=self._mode)

    def get_mode(self):
        return self._mode

    def explain_instance(self, sample, predict_fn, num_features=5, top_labels=3):
        if self._mode == 'classification':
            return self._explainer.explain_instance(sample, predict_fn, num_features=num_features, top_labels=top_labels)
        else:
            return self._explainer.explain_instance(sample, predict_fn, num_features=num_features)