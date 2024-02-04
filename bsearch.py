import re


def binary_search(data: list[str], find: str, regexp: str | None = None) -> int | None:
    '''This is a basic implementation of binary search that
    has some wordnet specific details.
    This will also sort the array in place and the returned
    index will be with respect to the sorted array.
    '''
    # 1. sort data list (ascending)
    data.sort()
    # 2. while `left` index <= `right` index
    left = 0
    right = len(data)
    f = find.strip().lower()
    # wordnet words don't have '_' instead of spaces
    if " " in f:
        f = "_".join(find.split(" "))
    while left <= right:
        # find midpoint index `m` in data and compare `data[m]` with `find`
        m = (left+right)//2
        data_m = data[m]
        # in case regular expression is provided for comparison
        if regexp:
            data_m = re.search(regexp, data_m)
            if data_m:
                data_m = data_m.group()
            else:
                raise Exception("provided expression doesn't match data list")
        # 3. if `find`==`data[m]` then the value being searched for has been found, return its index: `m`
        if f == data_m:
            return m
        # 4. if `find` lies on the right side of `data[m]`, search on the right side of data
        if f > data_m:
            left = m+1
        # 5. otherwise focus search on left side
        else:
            right = m-1
    return None
