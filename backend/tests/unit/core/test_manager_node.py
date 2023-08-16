import uuid

from neo4j import AsyncSession

from infrahub.core import registry
from infrahub.core.branch import Branch
from infrahub.core.initialization import create_branch
from infrahub.core.manager import NodeManager, identify_node_class
from infrahub.core.node import Node
from infrahub.core.query.node import NodeToProcess
from infrahub.core.schema import NodeSchema
from infrahub.core.timestamp import Timestamp


async def test_get_one_attribute(session: AsyncSession, default_branch: Branch, criticality_schema):
    obj1 = await Node.init(session=session, schema=criticality_schema)
    await obj1.new(session=session, name="low", level=4)
    await obj1.save(session=session)
    obj2 = await Node.init(session=session, schema=criticality_schema)
    await obj2.new(session=session, name="medium", level=3, description="My desc", color="#333333")
    await obj2.save(session=session)

    obj = await NodeManager.get_one(session=session, id=obj2.id)

    assert obj.id == obj2.id
    assert obj.db_id == obj2.db_id
    assert obj.name.value == "medium"
    assert obj.name.id
    assert obj.level.value == 3
    assert obj.level.id
    assert obj.description.value == "My desc"
    assert obj.description.id
    assert obj.color.value == "#333333"
    assert obj.color.id

    obj = await NodeManager.get_one(session=session, id=obj1.id)

    assert obj.id == obj1.id
    assert obj.db_id == obj1.db_id
    assert obj.name.value == "low"
    assert obj.name.id
    assert obj.level.value == 4
    assert obj.level.id
    assert obj.description.value is None
    assert obj.description.id
    assert obj.color.value == "#444444"
    assert obj.color.id


async def test_get_one_attribute_with_node_property(
    session, default_branch, criticality_schema, first_account, second_account
):
    obj1 = await Node.init(session=session, schema=criticality_schema)
    await obj1.new(session=session, name="low", level=4, _source=first_account)
    await obj1.save(session=session)
    obj2 = await Node.init(session=session, schema=criticality_schema)
    await obj2.new(
        session=session,
        name="medium",
        level={"value": 3, "source": second_account.id},
        description="My desc",
        color="#333333",
        _source=first_account,
    )
    await obj2.save(session=session)

    obj = await NodeManager.get_one(session=session, id=obj2.id, include_source=True)

    assert obj.id == obj2.id
    assert obj.db_id == obj2.db_id
    assert obj.name.value == "medium"
    assert obj.name.id
    assert obj.name.source_id == first_account.id
    assert obj.level.value == 3
    assert obj.level.id
    assert obj.level.source_id == second_account.id
    assert obj.description.value == "My desc"
    assert obj.description.id
    assert obj.description.source_id == first_account.id
    assert obj.color.value == "#333333"
    assert obj.color.id
    assert obj.color.source_id == first_account.id


async def test_get_one_attribute_with_flag_property(
    session, default_branch, criticality_schema, first_account, second_account
):
    obj1 = await Node.init(session=session, schema=criticality_schema)
    await obj1.new(
        session=session, name={"value": "low", "is_protected": True}, level={"value": 4, "is_visible": False}
    )
    await obj1.save(session=session)

    obj = await NodeManager.get_one(session=session, id=obj1.id, fields={"name": True, "level": True, "color": True})

    assert obj.id == obj1.id
    assert obj.db_id == obj1.db_id
    assert obj.name.value == "low"
    assert obj.name.id
    assert obj.name.is_visible is True
    assert obj.name.is_protected is True

    assert obj.level.value == 4
    assert obj.level.id
    assert obj.level.is_visible is False
    assert obj.level.is_protected is False

    assert obj.color.value == "#444444"
    assert obj.color.id
    assert obj.color.is_visible is True
    assert obj.color.is_protected is False


async def test_get_one_relationship(session: AsyncSession, default_branch: Branch, car_person_schema):
    car = registry.get_schema(name="TestCar")
    person = registry.get_schema(name="TestPerson")

    p1 = await Node.init(session=session, schema=person)
    await p1.new(session=session, name="John", height=180)
    await p1.save(session=session)

    c1 = await Node.init(session=session, schema=car)
    await c1.new(session=session, name="volt", nbr_seats=4, is_electric=True, owner=p1)
    await c1.save(session=session)
    c2 = await Node.init(session=session, schema=car)
    await c2.new(session=session, name="accord", nbr_seats=5, is_electric=False, owner=p1.id)
    await c2.save(session=session)

    c11 = await NodeManager.get_one(session=session, id=c1.id)

    assert c11.name.value == "volt"
    assert c11.nbr_seats.value == 4
    assert c11.is_electric.value is True
    c11_peer = await c11.owner.get_peer(session=session)
    assert c11_peer.id == p1.id

    p11 = await NodeManager.get_one(session=session, id=p1.id)
    assert p11.name.value == "John"
    assert p11.height.value == 180
    assert len(list(await p11.cars.get(session=session))) == 2


async def test_get_one_relationship_with_flag_property(
    session: AsyncSession, default_branch: Branch, car_person_schema
):
    p1 = await Node.init(session=session, schema="TestPerson")
    await p1.new(session=session, name="John", height=180)
    await p1.save(session=session)

    c1 = await Node.init(session=session, schema="TestCar")
    await c1.new(
        session=session,
        name="volt",
        nbr_seats=4,
        is_electric=True,
        owner={"id": p1.id, "_relation__is_protected": True, "_relation__is_visible": False},
    )
    await c1.save(session=session)

    c2 = await Node.init(session=session, schema="TestCar")
    await c2.new(
        session=session,
        name="accord",
        nbr_seats=5,
        is_electric=False,
        owner={"id": p1.id, "_relation__is_visible": False},
    )
    await c2.save(session=session)

    c11 = await NodeManager.get_one(session=session, id=c1.id)

    assert c11.name.value == "volt"
    assert c11.nbr_seats.value == 4
    assert c11.is_electric.value is True
    c11_peer = await c11.owner.get_peer(session=session)
    assert c11_peer.id == p1.id
    rel = await c11.owner.get(session=session)
    assert rel.is_visible is False
    assert rel.is_protected is True

    p11 = await NodeManager.get_one(session=session, id=p1.id)
    assert p11.name.value == "John"
    assert p11.height.value == 180

    rels = await p11.cars.get(session=session)
    assert len(rels) == 2
    assert rels[0].is_visible is False
    assert rels[1].is_visible is False


async def test_get_one_by_id_or_default_filter(
    session: AsyncSession,
    default_branch: Branch,
    criticality_schema: NodeSchema,
    criticality_low: Node,
    criticality_medium: Node,
):
    node1 = await NodeManager.get_one_by_id_or_default_filter(
        session=session, id=criticality_low.id, schema_name=criticality_schema.kind
    )
    assert isinstance(node1, Node)
    assert node1.id == criticality_low.id

    node2 = await NodeManager.get_one_by_id_or_default_filter(
        session=session, id=criticality_low.name.value, schema_name=criticality_schema.kind
    )
    assert isinstance(node2, Node)
    assert node2.id == criticality_low.id


async def test_get_many(session: AsyncSession, default_branch: Branch, criticality_low, criticality_medium):
    nodes = await NodeManager.get_many(session=session, ids=[criticality_low.id, criticality_medium.id])
    assert len(nodes) == 2


async def test_get_many_prefetch(session: AsyncSession, default_branch: Branch, person_jack_tags_main):
    nodes = await NodeManager.get_many(session=session, ids=[person_jack_tags_main.id], prefetch_relationships=True)

    assert len(nodes) == 1
    assert nodes[person_jack_tags_main.id]
    tags = await nodes[person_jack_tags_main.id].tags.get(session=session)
    assert len(tags) == 2
    assert tags[0]._peer
    assert tags[1]._peer


async def test_query_no_filter(
    session: AsyncSession,
    default_branch: Branch,
    criticality_schema: NodeSchema,
    criticality_low: Node,
    criticality_medium: Node,
    criticality_high: Node,
):
    nodes = await NodeManager.query(session=session, schema=criticality_schema)
    assert len(nodes) == 3


async def test_query_with_filter_string_int(
    session: AsyncSession,
    default_branch: Branch,
    criticality_schema,
    criticality_low: Node,
    criticality_medium: Node,
    criticality_high: Node,
):
    nodes = await NodeManager.query(session=session, schema=criticality_schema, filters={"color__value": "#333333"})
    assert len(nodes) == 2

    nodes = await NodeManager.query(
        session=session, schema=criticality_schema, filters={"description__value": "My other desc"}
    )
    assert len(nodes) == 1

    nodes = await NodeManager.query(
        session=session, schema=criticality_schema, filters={"level__value": 3, "color__value": "#333333"}
    )
    assert len(nodes) == 1


async def test_query_with_filter_bool_rel(
    session: AsyncSession,
    person_john_main,
    person_jane_main,
    car_accord_main,
    car_volt_main,
    car_yaris_main,
    car_camry_main,
    branch: Branch,
):
    car = registry.get_schema(name="TestCar")

    # Check filter with a boolean
    nodes = await NodeManager.query(session=session, schema=car, branch=branch, filters={"is_electric__value": False})
    assert len(nodes) == 3

    # Check filter with a relationship
    nodes = await NodeManager.query(session=session, schema=car, branch=branch, filters={"owner__name__value": "John"})
    assert len(nodes) == 2


async def test_query_non_default_class(
    session: AsyncSession,
    default_branch: Branch,
    criticality_schema: NodeSchema,
    criticality_low: Node,
    criticality_medium: Node,
):
    class TestCriticality(Node):
        def always_true(self):
            return True

    registry.node["TestCriticality"] = TestCriticality

    nodes = await NodeManager.query(session=session, schema=criticality_schema)
    assert len(nodes) == 2
    assert isinstance(nodes[0], TestCriticality)
    assert nodes[0].always_true()


async def test_query_class_name(
    session: AsyncSession,
    default_branch: Branch,
    criticality_schema: NodeSchema,
    criticality_low: Node,
    criticality_medium: Node,
):
    nodes = await NodeManager.query(session=session, schema="TestCriticality")
    assert len(nodes) == 2


async def test_identify_node_class(session, car_schema, default_branch):
    node = NodeToProcess(
        schema=car_schema,
        node_id=33,
        node_uuid=str(uuid.uuid4()),
        updated_at=Timestamp().to_string(),
        branch=default_branch,
    )

    class Car(Node):
        pass

    class Vehicule(Node):
        pass

    assert identify_node_class(node=node) == Node

    registry.node["TestVehicule"] = Vehicule
    assert identify_node_class(node=node) == Vehicule

    registry.node["TestCar"] = Car
    assert identify_node_class(node=node) == Car


# ------------------------------------------------------------------------
# WITH BRANCH
# ------------------------------------------------------------------------


async def test_get_one_local_attribute_with_branch(session: AsyncSession, default_branch: Branch, criticality_schema):
    obj1 = await Node.init(session=session, schema=criticality_schema)
    await obj1.new(session=session, name="low", level=4)
    await obj1.save(session=session)

    second_branch = await create_branch(branch_name="branch2", session=session)

    obj2 = await Node.init(session=session, schema=criticality_schema, branch=second_branch)
    await obj2.new(session=session, name="medium", level=3, description="My desc", color="#333333")
    await obj2.save(session=session)

    obj = await NodeManager.get_one(session=session, id=obj2.id, branch=second_branch)

    assert obj.id == obj2.id
    assert obj.db_id == obj2.db_id
    assert obj.name.value == "medium"
    assert obj.name.id
    assert obj.level.value == 3
    assert obj.level.id
    assert obj.description.value == "My desc"
    assert obj.description.id
    assert obj.color.value == "#333333"
    assert obj.color.id

    obj = await NodeManager.get_one(session=session, id=obj1.id, branch=second_branch)

    assert obj.id == obj1.id
    assert obj.db_id == obj1.db_id
    assert obj.name.value == "low"
    assert obj.name.id
    assert obj.level.value == 4
    assert obj.level.id
    assert obj.description.value is None
    assert obj.description.id
    assert obj.color.value == "#444444"
    assert obj.color.id


# ------------------------------------------------------------------------
# WITH BRANCH
# ------------------------------------------------------------------------

async def test_get_one_global(session: AsyncSession, default_branch: Branch, base_dataset_12):
    # obj1 = await Node.init(session=session, schema=criticality_schema)
    # await obj1.new(session=session, name="low", level=4)
    # await obj1.save(session=session)

    # second_branch = await create_branch(branch_name="branch2", session=session)

    # obj2 = await Node.init(session=session, schema=criticality_schema, branch=second_branch)
    # await obj2.new(session=session, name="medium", level=3, description="My desc", color="#333333")
    # await obj2.save(session=session)

    obj1 = await NodeManager.get_one(session=session, id="p1", branch="branch1")

    assert obj1.id == "p1"
    assert obj1.db_id
    assert obj1.name.value == "John Doe"
    assert obj1.height.value is None

    obj2 = await NodeManager.get_one(session=session, id="c1", branch="branch1")

    assert obj2.id == "c1"
    assert obj2.db_id
    assert obj2.name.value == "accord"
    assert obj2.nbr_seats.value == 5
    assert obj2.color.value == "#444444"
    assert obj2.is_electric.value is True


