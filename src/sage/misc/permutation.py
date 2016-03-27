r"""
Tools for permutations on `{0, 1, ..., n-1}`

Permutation in Sage works by default on `{1, 2, ..., n}` but it might be much
more convenient to work on `{0, 1, ..., n-1}`. This module provide simple
functions for the latter representation.
"""
from sage.rings.integer import Integer


def str_to_cycles(s):
    """
    Returns a list of cycles from a string

    EXAMPLES::

        sage: from sage.misc.permutation import str_to_cycles
        sage: str_to_cycles('(0,1)')
        ((0, 1),)
        sage: str_to_cycles('(0,1)(3,2)')
        ((0, 1), (3, 2))
    """
    return tuple(tuple(map(Integer, c_str.replace(' ', '').split(',')))
                 for c_str in s[1:-1].split(')('))


def perms_are_connected(g, n):
    """
    Checks that the action of the generated group is transitive

    INPUT:

    - a list of permutations of `[0, n-1]` (in a SymmetricGroup)

    - an integer `n`

    EXAMPLES::

        sage: from sage.misc.permutation import perms_are_connected
        sage: S = SymmetricGroup(range(3))
        sage: perms_are_connected([S([0,1,2]),S([0,2,1])],3)
        False
        sage: perms_are_connected([S([0,1,2]),S([1,2,0])],3)
        True
    """
    from sage.graphs.graph import Graph
    G = Graph()
    if g:
        G.add_vertices(g[0].domain())
    for p in g:
        G.add_edges(enumerate(p.tuple()))
    return G.num_verts() == n and G.is_connected()


def perms_canonical_labels_from(x, y, j0, verbose=False):
    r"""
    Return canonical labels for ``x``, ``y`` that starts at ``j0``

    .. WARNING:

        The group generated by ``x`` and the elements of ``y`` should be
        transitive.

    INPUT:

    - ``x`` -- list - a permutation of `[0, ..., n]` as a list

    - ``y`` -- list of permutations of `[0, ..., n]` as a list of lists

    - ``j0`` -- an index in [0, ..., n]

    OUTPUT:

    mapping: a permutation that specify the new labels

    EXAMPLES::

        sage: from sage.misc.permutation import perms_canonical_labels_from
        sage: S = SymmetricGroup(range(3))
        sage: perms_canonical_labels_from(S([0,1,2]),[S([1,2,0])],0)
        ()
        sage: perms_canonical_labels_from(S([1,0,2]),[S([2,0,1])],0)
        ()
        sage: perms_canonical_labels_from(S([1,0,2]),[S([2,0,1])],1)
        (0,1)
        sage: perms_canonical_labels_from(S([1,0,2]),[S([2,0,1])],2)
        (0,2)
    """
    n = len(x.domain())
    S = x.parent()

    k = 0
    mapping = [None] * n
    waiting = [[] for i in xrange(len(y))]

    while k < n:
        if verbose:
            print "complete from", j0
        # initialize at j0
        mapping[j0] = k
        waiting[0].append(j0)
        k += 1
        # complete x cycle from j0
        j = x(j0)
        while j != j0:
            mapping[j] = k
            waiting[0].append(j)
            k += 1
            j = x(j)
        if verbose:
            print "completed cycle mapping=", mapping

        # find another guy
        if verbose:
            print "try to find somebody in", waiting
        l = 0
        while l < len(waiting):
            i = 0
            while i < len(waiting[l]):
                j1 = waiting[l][i]
                if mapping[y[l](j1)] is None:
                    break
                i += 1

            if i == len(waiting[l]):  # not found: go further in waiting
                if l < len(waiting)-1:
                    waiting[l+1].extend(waiting[l])
                waiting[l] = []
                l += 1
                i = 0

            else:  # found: complete cycle from new guy
                j0 = y[l](j1)
                if l < len(waiting)-1:
                    waiting[l+1].extend(waiting[l][:i+1])
                del waiting[l][:i+1]
                break

    return S(mapping)


def perms_canonical_labels(p, e=None):
    """
    Relabel a list with a common conjugation such that two conjugated
    lists are relabeled the same way.

    INPUT:

    - ``p`` is a list of at least 2 permutations

    - ``e`` is None or a list of integer in the domain of the
      permutations. If provided, then the renumbering algorithm is
      only performed from the elements of ``e``.

    OUTPUT:

    - a pair made of a list of permutations (as a list of lists) and a
      list that corresponds to the conjugacy used.

    EXAMPLES::

        sage: from sage.misc.permutation import perms_canonical_labels
        sage: S = SymmetricGroup(range(4))
        sage: l0 = [S([2,0,3,1]),S([3,1,2,0]),S([0,2,1,3])]
        sage: l, m = perms_canonical_labels(l0); l
        [(0,1,2,3), (1,3), (0,2)]

        sage: [~m * u * m for u in l0] == l
        True

        sage: from sage.misc.permutation import perms_canonical_labels
        sage: perms_canonical_labels([])
        Traceback (most recent call last):
        ...
        ValueError: input must have length >= 2
    """
    if not len(p) > 1:
        raise ValueError('input must have length >= 2')
    n = len(p[0].domain())

    c_win = None
    m_win = range(n)

    x = p[0]
    y = p[1:]

    if e is None:
        e = range(n)

    # get canonical label from i in to_test and compare
    while e:
        i = e.pop()
        m_test = perms_canonical_labels_from(x, y, i)
        inv_m_test = ~m_test
        c_test = [inv_m_test * u * m_test for u in p]
        if c_win is None or c_test < c_win:
            c_win = c_test
            m_win = m_test

    return c_win, m_win
