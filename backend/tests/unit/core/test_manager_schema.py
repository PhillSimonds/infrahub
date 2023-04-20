import pytest
from deepdiff import DeepDiff
from neo4j import AsyncSession

from infrahub.core import registry
from infrahub.core.branch import Branch
from infrahub.core.manager import SchemaManager, SchemaRegistryBranch
from infrahub.core.schema import (
    FilterSchemaKind,
    GenericSchema,
    GroupSchema,
    NodeSchema,
    SchemaRoot,
    core_models,
    internal_schema,
)


# -----------------------------------------------------------------
# SchemaRegistryBranch
# -----------------------------------------------------------------
@pytest.fixture
def schema_all_in_one():
    FULL_SCHEMA = {
        "nodes": [
            {
                "name": "criticality",
                "kind": "Criticality",
                "inherit_from": ["GenericInterface"],
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "unique": True},
                    {"name": "level", "kind": "Number"},
                    {"name": "color", "kind": "Text", "default_value": "#444444"},
                    {"name": "description", "kind": "Text", "optional": True},
                ],
                "relationships": [
                    {"name": "tags", "peer": "Tag", "label": "Tags", "optional": True, "cardinality": "many"},
                ],
            },
            {
                "name": "tag",
                "kind": "Tag",
                "label": "Tag",
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
            },
            {
                "name": "status",
                "kind": "Status",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                ],
            },
        ],
        "generics": [
            {
                "name": "generic_interface",
                "kind": "GenericInterface",
                "attributes": [
                    {"name": "my_generic_name", "kind": "Text"},
                ],
                "relationships": [
                    {
                        "name": "primary_tag",
                        "peer": "Tag",
                        "label": "Primary Tag",
                        "identifier": "primary_tag__criticality",
                        "optional": True,
                        "cardinality": "one",
                    },
                    {
                        "name": "status",
                        "peer": "Status",
                        "optional": True,
                        "cardinality": "one",
                    },
                ],
            },
        ],
        "groups": [
            {
                "name": "generic_group",
                "kind": "GenericGroup",
            },
        ],
    }

    return FULL_SCHEMA


async def test_schema_branch_set():
    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "description", "kind": "Text"},
        ],
    }
    schema = NodeSchema(**SCHEMA)

    schema_branch = SchemaRegistryBranch(cache={}, name="test")

    schema_branch.set(name="schema1", schema=schema)
    assert hash(schema) in schema_branch._cache
    assert len(schema_branch._cache) == 1

    schema_branch.set(name="schema2", schema=schema)
    assert len(schema_branch._cache) == 1


async def test_schema_branch_get(default_branch: Branch):
    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "description", "kind": "Text"},
        ],
    }
    schema = NodeSchema(**SCHEMA)

    schema_branch = SchemaRegistryBranch(cache={}, name="test")

    schema_branch.set(name="schema1", schema=schema)
    assert len(schema_branch._cache) == 1

    schema11 = schema_branch.get(name="schema1")
    assert schema11 == schema


async def test_schema_branch_load_schema_initial(schema_all_in_one):
    schema = SchemaRegistryBranch(cache={}, name="test")
    schema.load_schema(schema=SchemaRoot(**schema_all_in_one))

    assert isinstance(schema.get(name="Criticality"), NodeSchema)
    assert isinstance(schema.get(name="GenericGroup"), GroupSchema)
    assert isinstance(schema.get(name="GenericInterface"), GenericSchema)


async def test_schema_branch_generate_identifiers(schema_all_in_one):
    schema = SchemaRegistryBranch(cache={}, name="test")
    schema.load_schema(schema=SchemaRoot(**schema_all_in_one))

    schema.generate_identifiers()

    generic = schema.get(name="GenericInterface")
    assert generic.relationships[1].identifier == "genericinterface__status"


async def test_schema_branch_load_schema_extension(
    session: AsyncSession, default_branch, schema_file_infra_w_extensions_01
):
    schema = SchemaRoot(**core_models)

    schema_branch = SchemaRegistryBranch(cache={}, name="test")
    schema_branch.load_schema(schema=schema)
    schema_branch.process()

    org = schema_branch.get(name="Organization")
    initial_nbr_relationships = len(org.relationships)

    schema_branch.load_schema(schema=SchemaRoot(**schema_file_infra_w_extensions_01))

    org = schema_branch.get(name="Organization")
    assert len(org.relationships) == initial_nbr_relationships + 1
    assert schema_branch.get(name="Device")


async def test_schema_branch_process_filters(
    session, reset_registry, default_branch: Branch, register_internal_models_schema
):
    FULL_SCHEMA = {
        "nodes": [
            {
                "name": "criticality",
                "kind": "Criticality",
                "default_filter": "name__value",
                "label": "Criticality",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "level", "kind": "Number", "label": "Level"},
                    {"name": "color", "kind": "Text", "label": "Color", "default_value": "#444444"},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
                "relationships": [
                    {"name": "tags", "peer": "Tag", "label": "Tags", "optional": True, "cardinality": "many"},
                    {
                        "name": "primary_tag",
                        "peer": "Tag",
                        "label": "Primary Tag",
                        "identifier": "primary_tag__criticality",
                        "optional": True,
                        "cardinality": "one",
                    },
                ],
            },
            {
                "name": "tag",
                "kind": "Tag",
                "label": "Tag",
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
            },
        ]
    }

    schema_branch = SchemaRegistryBranch(cache={}, name="test")
    schema_branch.load_schema(schema=SchemaRoot(**FULL_SCHEMA))
    schema_branch.process_filters()

    assert len(schema_branch.nodes) == 2
    criticality_dict = schema_branch.get("Criticality").dict()

    expected_filters = [
        {"name": "ids", "kind": FilterSchemaKind.LIST, "enum": None, "object_kind": None, "description": None},
        {
            "name": "level__value",
            "kind": FilterSchemaKind.NUMBER,
            "enum": None,
            "object_kind": None,
            "description": None,
        },
        {
            "name": "color__value",
            "kind": FilterSchemaKind.TEXT,
            "enum": None,
            "object_kind": None,
            "description": None,
        },
        {
            "name": "name__value",
            "kind": FilterSchemaKind.TEXT,
            "enum": None,
            "object_kind": None,
            "description": None,
        },
        {
            "name": "description__value",
            "kind": FilterSchemaKind.TEXT,
            "enum": None,
            "object_kind": None,
            "description": None,
        },
    ]

    assert not DeepDiff(criticality_dict["filters"], expected_filters, ignore_order=True)


async def test_schema_branch_copy(
    session: AsyncSession, reset_registry, default_branch: Branch, register_internal_models_schema
):
    FULL_SCHEMA = {
        "nodes": [
            {
                "name": "criticality",
                "kind": "Criticality",
                "default_filter": "name__value",
                "label": "Criticality",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "level", "kind": "Number", "label": "Level"},
                    {"name": "color", "kind": "Text", "label": "Color", "default_value": "#444444"},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
                "relationships": [
                    {"name": "tags", "peer": "Tag", "label": "Tags", "optional": True, "cardinality": "many"},
                    {
                        "name": "primary_tag",
                        "peer": "Tag",
                        "label": "Primary Tag",
                        "identifier": "primary_tag__criticality",
                        "optional": True,
                        "cardinality": "one",
                    },
                ],
            },
            {
                "name": "tag",
                "kind": "Tag",
                "label": "Tag",
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
            },
        ]
    }

    schema_branch = SchemaRegistryBranch(cache={}, name="test")
    schema_branch.load_schema(schema=SchemaRoot(**FULL_SCHEMA))
    new_schema = schema_branch.duplicate()

    assert id(new_schema.nodes) != id(schema_branch.nodes)
    assert hash(new_schema) == hash(schema_branch)

    new_schema.process()
    assert hash(new_schema) != hash(schema_branch)


async def test_schema_branch_diff(
    session: AsyncSession, reset_registry, default_branch: Branch, register_internal_models_schema
):
    FULL_SCHEMA = {
        "nodes": [
            {
                "name": "criticality",
                "kind": "Criticality",
                "default_filter": "name__value",
                "label": "Criticality",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "level", "kind": "Number", "label": "Level"},
                    {"name": "color", "kind": "Text", "label": "Color", "default_value": "#444444"},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
                "relationships": [
                    {"name": "tags", "peer": "Tag", "label": "Tags", "optional": True, "cardinality": "many"},
                    {
                        "name": "primary_tag",
                        "peer": "Tag",
                        "label": "Primary Tag",
                        "identifier": "primary_tag__criticality",
                        "optional": True,
                        "cardinality": "one",
                    },
                ],
            },
            {
                "name": "tag",
                "kind": "Tag",
                "label": "Tag",
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
            },
        ]
    }

    schema_branch = SchemaRegistryBranch(cache={}, name="test")
    schema_branch.load_schema(schema=SchemaRoot(**FULL_SCHEMA))
    new_schema = schema_branch.duplicate()

    node = new_schema.get(name="Criticality")
    node.attributes[0].unique = False
    new_schema.set(name="Criticality", schema=node)

    diff = schema_branch.diff(obj=new_schema)
    assert diff.dict() == {"added": [], "changed": ["Criticality"], "removed": []}


# -----------------------------------------------------------------
# SchemaManager
# -----------------------------------------------------------------
async def test_schema_manager_set():
    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "description", "kind": "Text"},
        ],
    }
    schema = NodeSchema(**SCHEMA)
    manager = SchemaManager()

    manager.set(name="schema1", schema=schema)
    assert hash(schema) in manager._cache
    assert len(manager._cache) == 1

    manager.set(name="schema2", schema=schema)
    assert len(manager._cache) == 1


async def test_schema_manager_get(default_branch: Branch):
    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "description", "kind": "Text"},
        ],
    }
    schema = NodeSchema(**SCHEMA)

    manager = SchemaManager()

    manager.set(name="schema1", schema=schema)
    assert len(manager._cache) == 1

    schema11 = manager.get(name="schema1")
    assert schema11 == schema


# -----------------------------------------------------------------


async def test_load_node_to_db_node_schema(session: AsyncSession, default_branch: Branch):
    registry.schema = SchemaManager()
    registry.schema.register_schema(schema=SchemaRoot(**internal_schema), branch=default_branch.name)

    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "level", "kind": "Number"},
            {"name": "color", "kind": "Text", "default_value": "#444444"},
            {"name": "description", "kind": "Text", "optional": True},
        ],
        "relationships": [
            {"name": "others", "peer": "Criticality", "optional": True, "cardinality": "many"},
        ],
    }
    node = NodeSchema(**SCHEMA)

    await registry.schema.load_node_to_db(node=node, session=session, branch=default_branch)

    node2 = registry.schema.get(name=node.kind, branch=default_branch)
    assert node2.id
    assert node2.relationships[0].id
    assert node2.attributes[0].id

    results = await SchemaManager.query(
        schema="NodeSchema", filters={"kind__value": "Criticality"}, branch=default_branch, session=session
    )
    assert len(results) == 1


async def test_load_node_to_db_generic_schema(session: AsyncSession, default_branch):
    registry.schema = SchemaManager()
    registry.schema.register_schema(schema=SchemaRoot(**internal_schema), branch=default_branch.name)

    SCHEMA = {
        "name": "generic_interface",
        "kind": "GenericInterface",
        "attributes": [
            {"name": "my_generic_name", "kind": "Text"},
        ],
    }
    node = GenericSchema(**SCHEMA)
    await registry.schema.load_node_to_db(node=node, session=session, branch=default_branch)

    results = await SchemaManager.query(
        schema="GenericSchema", filters={"kind__value": "GenericInterface"}, branch=default_branch, session=session
    )
    assert len(results) == 1


async def test_load_node_to_db_group_schema(session: AsyncSession, default_branch: Branch):
    registry.schema = SchemaManager()
    registry.schema.register_schema(schema=SchemaRoot(**internal_schema), branch=default_branch.name)

    SCHEMA = {
        "name": "generic_group",
        "kind": "GenericGroup",
    }

    node = GroupSchema(**SCHEMA)
    await registry.schema.load_node_to_db(node=node, session=session, branch=default_branch)

    results = await SchemaManager.query(
        schema="GroupSchema", filters={"kind__value": "GenericGroup"}, branch=default_branch, session=session
    )
    assert len(results) == 1


async def test_update_node_in_db_node_schema(session: AsyncSession, default_branch: Branch):
    SCHEMA = {
        "name": "criticality",
        "kind": "Criticality",
        "default_filter": "name__value",
        "attributes": [
            {"name": "name", "kind": "Text", "unique": True},
            {"name": "level", "kind": "Number"},
            {"name": "color", "kind": "Text", "default_value": "#444444"},
            {"name": "description", "kind": "Text", "optional": True},
        ],
        "relationships": [
            {"name": "others", "peer": "Criticality", "optional": True, "cardinality": "many"},
        ],
    }

    registry.schema = SchemaManager()
    registry.schema.register_schema(schema=SchemaRoot(**internal_schema), branch=default_branch.name)
    await registry.schema.load_node_to_db(node=NodeSchema(**SCHEMA), session=session, branch=default_branch)

    node = registry.schema.get(name="Criticality", branch=default_branch)

    new_node = node.duplicate()

    new_node.default_filter = "kind__value"
    new_node.attributes[0].unique = False

    await registry.schema.update_node_in_db(node=new_node, session=session, branch=default_branch)

    results = await SchemaManager.get_many(ids=[node.id, new_node.attributes[0].id], session=session)

    assert results[new_node.id].default_filter.value == "kind__value"
    assert results[new_node.attributes[0].id].unique.value is False


async def test_load_schema_to_db_internal_models(session: AsyncSession, default_branch: Branch):
    schema = SchemaRoot(**internal_schema)
    new_schema = registry.schema.register_schema(schema=schema, branch=default_branch.name)

    await registry.schema.load_schema_to_db(schema=new_schema, session=session, branch=default_branch.name)

    node_schema = registry.schema.get(name="NodeSchema", branch=default_branch)
    results = await SchemaManager.query(schema=node_schema, session=session)
    assert len(results) > 1


async def test_load_schema_to_db_core_models(
    session: AsyncSession, default_branch: Branch, register_internal_models_schema
):
    schema = SchemaRoot(**core_models)
    new_schema = registry.schema.register_schema(schema=schema, branch=default_branch.name)

    await registry.schema.load_schema_to_db(schema=new_schema, session=session)

    node_schema = registry.get_schema(name="GenericSchema")
    results = await SchemaManager.query(schema=node_schema, session=session)
    assert len(results) > 1


async def test_load_schema_to_db_simple_01(
    session: AsyncSession,
    default_branch: Branch,
    register_core_models_schema: SchemaRegistryBranch,
    schema_file_infra_simple_01,
):
    schema = SchemaRoot(**schema_file_infra_simple_01)
    new_schema = registry.schema.register_schema(schema=schema, branch=default_branch.name)
    await registry.schema.load_schema_to_db(schema=new_schema, session=session, branch=default_branch)

    node_schema = registry.schema.get(name="NodeSchema")
    results = await SchemaManager.query(
        schema=node_schema, filters={"kind__value": "Device"}, session=session, branch=default_branch
    )
    assert len(results) == 1


async def test_load_schema_to_db_w_generics_01(
    session: AsyncSession,
    default_branch: Branch,
    register_core_models_schema: SchemaRegistryBranch,
    schema_file_infra_w_generics_01,
):
    schema = SchemaRoot(**schema_file_infra_w_generics_01)
    new_schema = registry.schema.register_schema(schema=schema, branch=default_branch.name)
    await registry.schema.load_schema_to_db(schema=new_schema, session=session, branch=default_branch)

    node_schema = registry.schema.get(name="NodeSchema")
    results = await SchemaManager.query(
        schema=node_schema, filters={"kind__value": "InterfaceL3"}, session=session, branch=default_branch
    )
    assert len(results) == 1


@pytest.mark.xfail(
    reason="FIXME: Hash before and after should match, it's working if Criticality only has 2 attributes but not more"
)
async def test_load_schema_from_db(
    session: AsyncSession, reset_registry, default_branch: Branch, register_internal_models_schema
):
    FULL_SCHEMA = {
        "nodes": [
            {
                "name": "criticality",
                "kind": "Criticality",
                "default_filter": "name__value",
                "label": "Criticality",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "level", "kind": "Number", "label": "Level"},
                    {"name": "color", "kind": "Text", "label": "Color", "default_value": "#444444"},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
                "relationships": [
                    {"name": "tags", "peer": "Tag", "label": "Tags", "optional": True, "cardinality": "many"},
                    {
                        "name": "primary_tag",
                        "peer": "Tag",
                        "label": "Primary Tag",
                        "identifier": "primary_tag__criticality",
                        "optional": True,
                        "cardinality": "one",
                    },
                ],
            },
            {
                "name": "tag",
                "kind": "Tag",
                "label": "Tag",
                "default_filter": "name__value",
                "attributes": [
                    {"name": "name", "kind": "Text", "label": "Name", "unique": True},
                    {"name": "description", "kind": "Text", "label": "Description", "optional": True},
                ],
            },
        ],
        "generics": [
            {
                "name": "generic_interface",
                "kind": "GenericInterface",
                "label": "Generic Interface",
                "attributes": [
                    {"name": "my_generic_name", "kind": "Text", "label": "My Generic String"},
                ],
            },
        ],
        "groups": [
            {
                "name": "generic_group",
                "kind": "GenericGroup",
            },
        ],
    }

    schema1 = registry.schema.register_schema(schema=SchemaRoot(**FULL_SCHEMA), branch=default_branch.name)
    await registry.schema.load_schema_to_db(schema=schema1, session=session, branch=default_branch.name)
    schema11 = registry.schema.get_schema_branch(name=default_branch.name)
    schema2 = await registry.schema.load_schema_from_db(session=session, branch=default_branch.name)

    assert len(schema2.nodes) == 7
    assert len(schema2.generics) == 1
    assert len(schema2.groups) == 1

    assert hash(schema11.get(name="Criticality")) == hash(schema2.get(name="Criticality"))
    assert hash(schema11.get(name="Tag")) == hash(schema2.get(name="Tag"))
    assert hash(schema11.get(name="GenericInterface")) == hash(schema2.get(name="GenericInterface"))
    assert hash(schema11.get(name="GenericGroup")) == hash(schema2.get(name="GenericGroup"))
