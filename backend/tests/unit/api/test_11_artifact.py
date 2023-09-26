import pytest
from deepdiff import DeepDiff
from fastapi.testclient import TestClient

from infrahub.core.node import Node
from infrahub.database import InfrahubDatabase
from infrahub.message_bus.events import (
    ArtifactMessageAction,
    InfrahubRPCResponse,
    MessageType,
    RPCStatusCode,
)
from infrahub.message_bus.rpc import InfrahubRpcClientTesting


@pytest.fixture
def patch_rpc_client():
    import infrahub.message_bus.rpc

    infrahub.message_bus.rpc.InfrahubRpcClient = InfrahubRpcClientTesting


async def test_artifact_definition_endpoint(
    db: InfrahubDatabase,
    admin_headers,
    default_branch,
    patch_rpc_client,
    register_core_models_schema,
    car_person_data_generic,
    authentication_base,
):
    from infrahub.server import app

    client = TestClient(app)

    g1 = await Node.init(db=db, schema="CoreStandardGroup")
    await g1.new(db=db, name="group1", members=[car_person_data_generic["c1"], car_person_data_generic["c2"]])
    await g1.save(db=db)

    t1 = await Node.init(db=db, schema="CoreTransformPython")
    await t1.new(
        db=db,
        name="transform01",
        query=str(car_person_data_generic["q1"].id),
        url="mytransform",
        repository=str(car_person_data_generic["r1"].id),
        file_path="transform01.py",
        class_name="Transform01",
        rebase=False,
    )
    await t1.save(db=db)

    ad1 = await Node.init(db=db, schema="CoreArtifactDefinition")
    await ad1.new(
        db=db,
        name="artifactdef01",
        targets=g1,
        transformation=t1,
        content_type="application/json",
        artifact_name="myartifact",
        parameters='{"name": "name__value"}',
    )
    await ad1.save(db=db)

    # Must execute in a with block to execute the startup/shutdown events
    with client:
        mock_response = InfrahubRPCResponse(
            status=RPCStatusCode.OK,
            response={"artifact_id": "XXXXX", "changed": True, "checksum": "YYYYYY", "storage_id": "DDDDDDDDDD"},
        )
        await client.app.state.rpc_client.add_response(
            response=mock_response, message_type=MessageType.ARTIFACT, action=ArtifactMessageAction.GENERATE
        )
        await client.app.state.rpc_client.add_response(
            response=mock_response, message_type=MessageType.ARTIFACT, action=ArtifactMessageAction.GENERATE
        )

        response = client.post(
            f"/api/artifact/generate/{ad1.id}",
            headers=admin_headers,
        )

    assert response.status_code == 200
    assert response.json() is not None
    result = response.json()

    expected_result = {
        "nodes": [
            car_person_data_generic["c1"].id,
            car_person_data_generic["c2"].id,
        ]
    }
    assert DeepDiff(result, expected_result, ignore_order=True).to_dict() == {}
