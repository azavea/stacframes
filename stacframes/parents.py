""" Helper methods for generating the "parents" column used by stacframes.df_to() """
from itertools import accumulate


DEFAULT_PARENTS_COLUMN = "parents"


def from_properties(keys, dataframe, prefix="", parents_col=DEFAULT_PARENTS_COLUMN):
    """Add parents_col to dataframe using values for keys in properties column

    The resulting list in parents_col is generated by retrieving the value
    of each props key in order from the properties column.

    Args:
        keys (list): A list of string key names found in the properties dict
            column of dataframe
        dataframe (pandas.DataFrame): DataFrame to generate parents_col on
        prefix (str): A string prefix to apply to each value
        parents_col (str): The column name created

    Returns:
        pandas.DataFrame: dataframe with parents_col added

    """
    if "properties" not in dataframe.columns:
        raise ValueError("dataframe must have a 'properties' column")
    if parents_col in dataframe.columns:
        raise ValueError("{} already exists on dataframe".format(parents_col))

    def apply(series):
        properties = series.get("properties", {})
        parents = ["{}{}".format(prefix, properties[arg]) for arg in keys]
        series[parents_col] = parents
        return series

    return dataframe.apply(apply, axis=1)


def from_properties_accum(
    keys, dataframe, prefix="", separator="", parents_col=DEFAULT_PARENTS_COLUMN
):
    """from_properties, but with each value in parents accumulating those before it

    Example:
        df = pd.DataFrame({
            "properties": [{"Year": 2020, "Month": 1}]
        })
        df = from_properties_accum(["Year", "Month"], df, prefix="dt", separator="-")
        df["parents"][0]
        > ["dt-2020", "dt-2020-1"]

    Args:
        keys (list): A list of string key names found in the properties dict
            column of dataframe
        dataframe (pandas.DataFrame): DataFrame to generate parents_col on
        prefix (str): A string prefix to apply to each value
        separator (str): A string to separate each value with
        parents_col (str): The column name created

    Returns:
        pandas.DataFrame: dataframe with parents_col added

    """
    if "properties" not in dataframe.columns:
        raise ValueError("dataframe must have a 'properties' column")
    if parents_col in dataframe.columns:
        raise ValueError("{} already exists on dataframe".format(parents_col))

    def apply(series):
        properties = series.get("properties", {})
        values = [str(properties[x]) for x in keys]
        parents = list(accumulate(values, lambda acc, x: acc + separator + x))
        if prefix:
            parents = [prefix + separator + x for x in parents]
        series[parents_col] = parents
        return series

    return dataframe.apply(apply, axis=1)
