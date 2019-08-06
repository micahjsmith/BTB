# -*- coding: utf-8 -*-

"""Package where the numerical hyperparameters are defined."""

import sys

import numpy as np

from btb.tuning.hyperparams.base import BaseHyperParam


class NumericalHyperParam(BaseHyperParam):
    """Numerical Hyperparameter Class.

    The numerical hyperparameter class defines an abstraction to hyperparameters which ranges are
    defined by a numerical value and can take any number between that range.

    Attributes:
        K (int):
            Number of dimensions that this hyperparameter uses to be represented in the search
            space.

    Args:
        min (int or float):
            Minimum numerical value that this hyperparameter can be set to.
        max (int or float):
            Maximum numerical value that this hyperparameter can be set to.
        include_min (default=True):
            Either ot include or not the ``min`` value inside the range.
        include_max (default=True):
            Either ot include or not the ``max`` value inside the range.
        step (int or float):
            Increase amount to take for each sample.
    """
    pass


class FloatHyperParam(NumericalHyperParam):
    """NumericalHyperParam of type ``float``.

    Hyperparameter space:
        ``[min, max]``

    Search space:
        ``[0, 1]``
    """

    K = 1

    def __init__(self, min=None, max=None, include_min=True, include_max=True):

        self.include_min = include_min
        self.include_max = include_max

        if min is None or min == -np.inf:
            min = sys.float_info.min

        if max is None or max == np.inf:
            max = sys.float_info.max

        self.min = min
        self.max = max
        self.range = max - min

    def _inverse_transform(self, values):
        """Inverse transform one or more ``normalized`` values.

        Inverse transorm one or more normalized values from the search space [0, 1)^k. This is
        being computed by multiplying the hyperparameter's range with the values to be denormalized
        and adding the ``min`` value to them.

        Args:
            values (ArrayLike):
                Single value or 2D ArrayLike of normalized values.

        Returns:
            denormalized (Union[object, List[object]]):
                Denormalized value or list of denormalized values.

        Examples:
            >>> instance = FloatHyperParam(0.1, 0.9)
            >>> instance.inverse_transform([0., 1.])
            array([0.1, 0.9])
            >>> instance.inverse_transform(0.875)
            0.8
        """
        return values * self.range + self.min

    def _transform(self, values):
        """Transform one or more ``float`` values.

        Convert one or more `float` values from the original hyperparameter space to the
        normalized search space [0, 1)^k. This is being computed by substracting the `min` value
        that the hyperparameter can take from the values to be trasnformed and dividing them by
        the range of the hyperparameter.

        Args:
            values (Union[object, List[object]]):
                Single value or list of values to be normalized.

        Returns:
            normalized (ArrayLike):
                2D array of shape(len(values)) or a single float number.

        Examples:
            >>> instance = FloatHyperParam(0.1, 0.9)
            >>> instance.transform([0.1, 0.9])
            array([0., 1.])
            >>> instance.transform(0.8)
            0.875
        """
        return (values - self.min) / self.range

    def sample(self, n_samples):
        """Generate sample values in the hyperparameter search space of [0, 1)^k.

        Args:
            n_samples (int):
                Number of values to sample.

        Returns:
            samples (ArrayLike):
                2D arry with shape of (n_samples, self.K) with normalized values inside the search
                space [0, 1)^k.

        Examples:
            >>> instance = FloatHyperParam(0.1, 0.9)
            >>> instance.sample(2)
            array([0.52058728], [0.00582452]])
        """
        return np.random.random((n_samples, self.K))


class IntHyperParam(NumericalHyperParam):
    """NumericalHyperParam of type ``int``.

    Hyperparameter space:
        ``{min, min + step, min + 2 * step...max}``
    Search space:
        ``{i1...in} where n is ((max - min) / step) + 1``
    """

    K = 1

    def __init__(self, min=None, max=None, include_min=True, include_max=True, step=1):

        self.include_min = include_min
        self.include_max = include_max

        if min is None:
            min = -(sys.maxsize / 2)

        if max is None:
            max = sys.maxsize / 2

        self.min = int(min) if include_min else int(min) + 1
        self.max = int(max) if include_max else int(max) - 1
        self.step = step
        self.range = ((self.max - self.min) / step) + 1
        self.interval = 1 / self.range

    def _inverse_transform(self, values):
        """Inverse transform one or more ``normalized`` values.

        Inverse transorm one or more normalized values from the search space [0, 1)^k. This is
        being computed by divinding the hyperparameter's interval with the values to be inverted
        and adding the `min` value to them and resting the 0.5 that has been added during the
        transformation.

        Args:
            values (ArrayLike):
                Single value or 2D ArrayLike of normalized values.

        Returns:
            denormalized (Union[object, List[object]]):
                Denormalized value or list of denormalized values.

        Examples:
            >>> instance = IntHyperParam(1, 4)
            >>> instance.inverse_transform([0.125, 0.875])
            array([1, 4])
            >>> instance.inverse_trasnfrom(0.625)
            3
        """
        unscaled_values = values / self.interval - 0.5 + self.min
        rounded = unscaled_values.round()

        # Restrict to make sure that we stay within the valid range
        restricted = np.minimum(np.maximum(rounded, self.min), self.max)

        return restricted.astype(int)

    def _transform(self, values):
        """Transform one or more ``int`` values.

        Convert one or more ``int`` values from the original hyperparameter space to the
        normalized search space [0, 1)^k. This is being computed by substracting the `min` value
        that the hyperparameter can take from the values to be trasnformed and adding them 0.5,
        then multiply by the interval.

        Args:
            values (Union[object, List[object]]): single value or list of values to be normalized.

        Returns:
            normalized (ArrayLike): 2D array of shape(len(values)).

        Examples:
            >>> instance = IntHyperParam(1, 4)
            >>> instance.transform([1, 4])
            array([0.125, 0.875])
            >>> instance.trasnfrom(3)
            0.625
        """
        return (values - self.min + 0.5) * self.interval

    def sample(self, n_samples):
        sampled = np.random.random((n_samples, self.K))
        inverted = self.inverse_transform(sampled)

        return self.transform(inverted)
