from datetime import datetime, timezone
import pystac


def empty_extent():
    """Generate a new empty pystac.Extent"""
    return pystac.Extent(
        pystac.SpatialExtent([None, None, None, None]),
        pystac.TemporalExtent([[None, datetime.now(timezone.utc)]]),
    )


def update_collection_extents(catalog):
    """Recursively update all child collection extents in catalog"""
    for child in catalog.get_children():
        if isinstance(child, pystac.Collection):
            child.update_extent_from_items()
        update_collection_extents(child)
    if isinstance(catalog, pystac.Collection):
        catalog.update_extent_from_items()


def build_recursive(catalog, children, catalog_type="collection"):
    """Append child catalogs to catalog with the ids in children

    Catalog ids in children will be concatenated to the parent catalog
    id to ensure uniqueness, separated by `-`.

    An example:
    ```
    catalog = pystac.Catalog("test, "test")
    leaf_catalog = build_recursive(catalog, ["foo", "bar"], "collection")
    leaf_catalog.id
        <"test-foo-bar">
    isinstance(leaf_catalog, pystac.Collection)
        <True>
    ```

    Yields a catalog tree that looks like:
    ```
    Catalog("test")
    |- Collection("test-foo")
        |- Collection("test-foo-bar")
    ```

    Args:
        catalog (pystac.Catalog | pystac.Collection)
        children (list[str]): A list of child catalog names to walk in order,
            down the catalog tree
        catalog_type (str): Must be either "catalog" or "collection". Each child
            created will be of the requested catalog_type.

    Return:
        pystac.Catalog: The catalog created for the last entry in children. In
            other words, the leaf node of the catalog tree described by
            catalog + children.


    """
    if not children:
        return catalog
    else:
        child_id = "-".join([catalog.id, str(children.pop(0))])
        child_catalog = catalog.get_child(child_id)
        if child_catalog is None:
            if catalog_type == "catalog":
                child_catalog = pystac.Catalog(child_id, child_id)
            elif catalog_type == "collection":
                child_catalog = pystac.Collection(child_id, child_id, empty_extent())
            else:
                raise TypeError(
                    "catalog_type {} must be 'catalog' or 'collection'".format(
                        catalog_type
                    )
                )
            catalog.add_child(child_catalog)
        return build_recursive(child_catalog, children, catalog_type)
