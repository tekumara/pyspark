# adapted from https://github.com/holdenk/spark-testing-base

def assertDataFrameEqual(expected, result, tol=0):
    """Assert that two DataFrames contain the same data.
    When comparing inexact fields uses tol.
    """
    assert expected.schema == result.schema
    try:
        expectedRDD = expected.rdd.cache()
        resultRDD = result.rdd.cache()
        assert expectedRDD.count() == resultRDD.count()

        def zipWithIndex(rdd):
            """Zip with index (idx, data)"""
            return rdd.zipWithIndex().map(lambda x: (x[1], x[0]))

        def equal(x, y):
            if (len(x) != len(y)):
                return False
            elif (x == y):
                return True
            else:
                for idx in range(len(x)):
                    a = x[idx]
                    b = y[idx]
                    if isinstance(a, float):
                        if (abs(a - b) > tol):
                            return False
                    else:
                        if a != b:
                            return False
            return True
        expectedIndexed = zipWithIndex(expectedRDD)
        resultIndexed = zipWithIndex(resultRDD)
        joinedRDD = expectedIndexed.join(resultIndexed)
        unequalRDD = joinedRDD.filter(
            lambda x: not equal(x[1][0], x[1][1]))
        differentRows = unequalRDD.take(10)
        assert [] == differentRows
    finally:
        expectedRDD.unpersist()
        resultRDD.unpersist()
