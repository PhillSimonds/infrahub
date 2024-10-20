from graphql import graphql

from infrahub.core import registry
from infrahub.core.constants import InfrahubKind
from infrahub.core.node import Node
from infrahub.database import InfrahubDatabase
from infrahub.graphql.initialization import prepare_graphql_params


async def test_create_query_no_vars(db: InfrahubDatabase, default_branch, register_core_models_schema):
    query_value = """
    query MyQuery {
        CoreRepository {
            edges {
                node {
                    name {
                        value
                    }
                }
            }
        }
    }
    mutation MyMutation {
        CoreRepositoryCreate (data: {
            name: { value: "query1"},
            location: { value: "location1"},
        }) {
            ok
        }
    }
    """

    query = """
    mutation {
        CoreGraphQLQueryCreate(
            data: {
                name: { value: "query1"},
                query: { value: "%s" }}) {
            ok
            object {
                id
            }
        }
    }
    """ % query_value.replace("\n", " ").replace('"', '\\"')

    gql_params = prepare_graphql_params(db=db, include_subscription=False, branch=default_branch)
    result = await graphql(
        schema=gql_params.schema,
        source=query,
        context_value=gql_params.context,
        root_value=None,
        variable_values={},
    )

    assert result.errors is None
    assert result.data["CoreGraphQLQueryCreate"]["ok"] is True
    query_id = result.data["CoreGraphQLQueryCreate"]["object"]["id"]
    assert len(query_id) == 36  # length of an UUID

    query1 = await registry.manager.get_one(id=query_id, db=db)
    assert query1.depth.value == 6
    assert query1.height.value == 7
    assert query1.operations.value == ["mutation", "query"]
    assert query1.variables.value == []
    assert query1.models.value == [InfrahubKind.REPOSITORY]


async def test_create_query_with_vars(db: InfrahubDatabase, default_branch, register_core_models_schema):
    query_value = """
    query MyQuery {
        CoreRepository {
            edges {
                node {
                    name {
                        value
                    }
                    tags {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
            }
        }
    }
    mutation MyMutation($myvar: String) {
        CoreRepositoryCreate (data: {
            name: { value: $myvar},
            location: { value: "location1"},
        }) {
            ok
        }
    }
    """

    query = """
    mutation {
        CoreGraphQLQueryCreate(
            data: {
                name: { value: "query2"},
                query: { value: "%s" }}) {
            ok
            object {
                id
            }
        }
    }
    """ % query_value.replace("\n", " ").replace('"', '\\"')

    gql_params = prepare_graphql_params(db=db, include_subscription=False, branch=default_branch)
    result = await graphql(
        schema=gql_params.schema,
        source=query,
        context_value=gql_params.context,
        root_value=None,
        variable_values={},
    )

    assert result.errors is None
    assert result.data["CoreGraphQLQueryCreate"]["ok"] is True
    query_id = result.data["CoreGraphQLQueryCreate"]["object"]["id"]
    assert len(query_id) == 36  # length of an UUID

    query2 = await registry.manager.get_one(id=query_id, db=db)
    assert query2.depth.value == 8
    assert query2.height.value == 11
    assert query2.operations.value == ["mutation", "query"]
    assert query2.variables.value == [{"default_value": None, "name": "myvar", "required": False, "type": "String"}]
    assert query2.models.value == [InfrahubKind.TAG, InfrahubKind.REPOSITORY]


async def test_update_query(db: InfrahubDatabase, default_branch, register_core_models_schema):
    query_create = """
    query MyQuery {
        CoreRepository {
            edges {
                node {
                    name {
                        value
                    }
                }
            }
        }
    }
    """

    obj = await Node.init(db=db, branch=default_branch, schema=InfrahubKind.GRAPHQLQUERY)
    await obj.new(
        db=db,
        name="query1",
        query=query_create,
        depth=6,
        height=7,
        operations=["query"],
        variables=[],
        models=[InfrahubKind.REPOSITORY],
    )
    await obj.save(db=db)

    query_update = """
    query MyQuery {
        CoreRepository {
            edges {
                node {
                    name {
                        value
                    }
                    tags {
                        edges {
                            node {
                                id
                            }
                        }
                    }
                }
            }
        }
    }
    mutation MyMutation {
        CoreRepositoryCreate (data: {
            name: { value: "query1"},
            location: { value: "location1"},
        }) {
            ok
        }
    }
    """

    query = """
    mutation {
        CoreGraphQLQueryUpdate(
            data: {
                id: "%s"
                query: { value: "%s" }}) {
            ok
            object {
                id
            }
        }
    }
    """ % (
        obj.id,
        query_update.replace("\n", " ").replace('"', '\\"'),
    )

    gql_params = prepare_graphql_params(db=db, include_subscription=False, branch=default_branch)
    result = await graphql(
        schema=gql_params.schema,
        source=query,
        context_value=gql_params.context,
        root_value=None,
        variable_values={},
    )

    assert result.errors is None
    assert result.data["CoreGraphQLQueryUpdate"]["ok"] is True

    obj2 = await registry.manager.get_one(id=obj.id, db=db)
    assert obj2.depth.value == 8
    assert obj2.height.value == 11
    assert obj2.operations.value == ["mutation", "query"]
    assert obj2.variables.value == []
    assert obj2.models.value == [InfrahubKind.TAG, InfrahubKind.REPOSITORY]


async def test_update_query_no_update(db: InfrahubDatabase, default_branch, register_core_models_schema):
    query_create = """
    query MyQuery {
        CoreRepository {
            edges {
                node {
                    name {
                        value
                    }
                }
            }
        }
    }
    """

    obj = await Node.init(db=db, branch=default_branch, schema=InfrahubKind.GRAPHQLQUERY)
    await obj.new(
        db=db,
        name="query1",
        query=query_create,
        depth=6,
        height=7,
        operations=["query"],
        variables=[],
        models=[InfrahubKind.REPOSITORY],
    )
    await obj.save(db=db)

    query = """
    mutation {
        CoreGraphQLQueryUpdate(
            data: {
                id: "%s"
                description: { value: "new description" }}) {
            ok
            object {
                id
            }
        }
    }
    """ % (obj.id)

    gql_params = prepare_graphql_params(db=db, include_subscription=False, branch=default_branch)
    result = await graphql(
        schema=gql_params.schema,
        source=query,
        context_value=gql_params.context,
        root_value=None,
        variable_values={},
    )

    assert result.errors is None
    assert result.data["CoreGraphQLQueryUpdate"]["ok"] is True

    obj2 = await registry.manager.get_one(id=obj.id, db=db)
    assert obj2.depth.value == 6
    assert obj2.height.value == 7
    assert obj2.operations.value == ["query"]
    assert obj2.variables.value == []
    assert obj2.models.value == [InfrahubKind.REPOSITORY]
