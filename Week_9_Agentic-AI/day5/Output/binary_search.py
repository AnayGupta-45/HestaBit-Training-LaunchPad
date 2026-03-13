# binary_search.py
"""Binary search utility.

This module provides a robust, generic implementation of the binary search
algorithm for sorted sequences.  The implementation is **iterative** to avoid
recursion depth limits and operates in :math:`O(log n)` time with ``O(1)``
auxiliary space.

The public API is the :func:`binary_search` function which supports:

* **Standard usage** – ``binary_search(arr, target)`` where ``arr`` is a sorted
  list/tuple of comparable items.
* **Custom sub‑range** – optional ``low`` and ``high`` arguments to restrict the
  search to ``arr[low:high+1]``.
* **Key extraction** – a ``key`` callable (similar to ``sorted``) can be provided
  to transform items before comparison.  This enables searching on complex
  objects (e.g., ``key=lambda x: x.id``).
* **Comparator** – an optional ``cmp`` function that takes two items and returns
  ``-1``, ``0`` or ``1``.  ``cmp`` overrides ``key`` if both are supplied.

The function returns the *index* of the ``target`` within ``arr`` if found;
otherwise ``-1`` is returned.  ``ValueError`` is raised for invalid arguments
(e.g., ``low``/``high`` out of bounds) and ``TypeError`` for unsupported types.

Example
-------
>>> from binary_search import binary_search
>>> data = [1, 3, 5, 7, 9]
>>> binary_search(data, 7)
3
>>> binary_search(data, 2)
-1
>>> # Using a key function on a list of dicts
>>> records = [{"id": 10}, {"id": 20}, {"id": 30}]
>>> binary_search(records, 20, key=lambda x: x["id"])
1
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Sequence, TypeVar, Optional

_T = TypeVar("_T")

logger = logging.getLogger(__name__)


def _default_cmp(a: Any, b: Any) -> int:
    """Default comparator using the ``<`` and ``>`` operators.

    Returns ``-1`` if ``a < b``, ``1`` if ``a > b`` and ``0`` otherwise.
    """
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


def _is_sorted(seq: Sequence[_T], *, key: Optional[Callable[[Any], Any]] = None) -> bool:
    """Check whether *seq* is sorted in non‑decreasing order.

    The check is performed in ``O(n)`` time.  It is used for defensive
    programming; the algorithm still works on unsorted input but the result is
    undefined, so we raise ``ValueError`` when a violation is detected.
    """
    if len(seq) < 2:
        return True
    it = iter(seq)
    prev = next(it)
    prev_val = key(prev) if key else prev
    for cur in it:
        cur_val = key(cur) if key else cur
        if prev_val > cur_val:
            return False
        prev_val = cur_val
    return True


def binary_search(
    arr: Sequence[_T],
    target: Any,
    low: int = 0,
    high: Optional[int] = None,
    *,
    key: Optional[Callable[[Any], Any]] = None,
    cmp: Optional[Callable[[Any, Any], int]] = None,
) -> int:
    """Search *target* in a sorted ``arr`` using binary search.

    Parameters
    ----------
    arr:
        A sequence (list, tuple, etc.) sorted in **ascending** order.  Elements
        must be comparable either directly, via the ``key`` function, or via the
        ``cmp`` callable.
    target:
        The value to locate.  When ``key`` is provided, ``target`` should be the
        *key* value, not the original element.
    low:
        Lower bound index (inclusive) for the search interval.  Must be ``>= 0``.
    high:
        Upper bound index (inclusive).  If ``None`` the default is ``len(arr)-1``.
    key:
        Optional callable that extracts a comparable key from each element.  It
        is applied to both the elements in ``arr`` and the ``target`` before any
        comparison.
    cmp:
        Optional comparator taking two arguments ``a`` and ``b`` and returning
        ``-1`` if ``a < b``, ``0`` if equal, ``1`` if ``a > b``.  If provided, it
        overrides ``key`` for all comparisons.

    Returns
    -------
    int
        Index of ``target`` in ``arr`` if present; otherwise ``-1``.

    Raises
    ------
    TypeError
        If ``arr`` is not a list or tuple‑like sequence.
    ValueError
        If ``low``/``high`` are out of range, ``low`` > ``high``, or ``arr`` is
        not sorted according to the supplied ``key``/``cmp``.
    """
    # Basic type validation
    if not isinstance(arr, (list, tuple)):
        logger.error("binary_search expects a list or tuple, got %s", type(arr))
        raise TypeError("arr must be a list or tuple")

    n = len(arr)
    if high is None:
        high = n - 1

    # Validate bounds
    if not (0 <= low <= high < n):
        logger.error("Invalid low/high bounds: low=%d, high=%d, len=%d", low, high, n)
        raise ValueError("low/high indices are out of valid range")

    # Validate sortedness (defensive programming)
    if not _is_sorted(arr[low : high + 1], key=key):
        logger.error("Array segment arr[%d:%d] is not sorted", low, high)
        raise ValueError("Input array must be sorted in ascending order")

    # Choose comparison strategy
    compare = cmp if cmp is not None else _default_cmp

    # Normalise target using key if supplied
    target_key = key(target) if key else target

    while low <= high:
        mid = (low + high) // 2
        mid_elem = arr[mid]
        mid_key = key(mid_elem) if key else mid_elem

        comp_result = compare(mid_key, target_key)
        logger.debug(
            "low=%d, high=%d, mid=%d, mid_key=%s, target_key=%s, comp=%d",
            low,
            high,
            mid,
            mid_key,
            target_key,
            comp_result,
        )

        if comp_result == 0:
            logger.info("Found target %s at index %d", target, mid)
            return mid
        elif comp_result < 0:
            low = mid + 1
        else:
            high = mid - 1

    logger.info("Target %s not found", target)
    return -1


__all__ = ["binary_search"]
