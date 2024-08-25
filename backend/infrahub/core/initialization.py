import importlib
from typing import Optional
from uuid import uuid4

from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import WorkPoolCreate
from prefect.exceptions import ObjectAlreadyExists

from infrahub import config, lock
from infrahub.core import registry
from infrahub.core.branch import Branch
from infrahub.core.constants import (
    DEFAULT_IP_NAMESPACE,
    GLOBAL_BRANCH_NAME,
    AccountRole,
    GlobalPermissions,
    InfrahubKind,
)
from infrahub.core.graph import GRAPH_VERSION
from infrahub.core.node import Node
from infrahub.core.node.ipam import BuiltinIPPrefix
from infrahub.core.node.resource_manager.ip_address_pool import CoreIPAddressPool
from infrahub.core.node.resource_manager.ip_prefix_pool import CoreIPPrefixPool
from infrahub.core.node.resource_manager.number_pool import CoreNumberPool
from infrahub.core.protocols import CoreAccount
from infrahub.core.root import Root
from infrahub.core.schema import SchemaRoot, core_models, internal_schema
from infrahub.core.schema_manager import SchemaManager
from infrahub.database import InfrahubDatabase
from infrahub.exceptions import DatabaseError
from infrahub.log import get_logger
from infrahub.permissions import PermissionBackend
from infrahub.storage import InfrahubObjectStorage
from infrahub.utils import format_label
from infrahub.workflows.catalogue import worker_pools, workflows

log = get_logger()


async def get_root_node(db: InfrahubDatabase, initialize: bool = False) -> Root:
    roots = await Root.get_list(db=db)
    if len(roots) == 0 and not initialize:
        raise DatabaseError(
            "The Database hasn't been initialized for Infrahub, please run 'infrahub db init' or 'infrahub server start' to initialize the database."
        )

    if len(roots) == 0:
        await first_time_initialization(db=db)
        roots = await Root.get_list(db=db)

    elif len(roots) > 1:
        raise DatabaseError("The Database is corrupted, more than 1 root node found.")

    return roots[0]


async def get_default_ipnamespace(db: InfrahubDatabase) -> Optional[Node]:
    if not registry.schema._branches or not registry.schema.has(name=InfrahubKind.NAMESPACE):
        return None

    nodes = await registry.manager.query(db=db, schema=InfrahubKind.NAMESPACE, filters={"default__value": True})
    if len(nodes) == 0:
        return None

    if len(nodes) > 1:
        raise DatabaseError("More than 1 default namespace found.")

    return nodes[0]


def initialize_permission_backends() -> list[PermissionBackend]:
    permission_backends: list[PermissionBackend] = []
    for backend_module_path in config.SETTINGS.main.permission_backends:
        log.info("Loading permission backend", backend=backend_module_path)

        module, class_name = backend_module_path.rsplit(".", maxsplit=1)
        Backend = getattr(importlib.import_module(module), class_name)
        permission_backends.append(Backend())

    return permission_backends


async def initialize_registry(db: InfrahubDatabase, initialize: bool = False) -> None:
    # ---------------------------------------------------
    # Initialize the database and Load the Root node
    # ---------------------------------------------------
    root = await get_root_node(db=db, initialize=initialize)
    registry.id = str(root.get_uuid())
    registry.default_branch = root.default_branch

    # ---------------------------------------------------
    # Initialize the Storage Driver
    # ---------------------------------------------------
    registry.storage = await InfrahubObjectStorage.init(settings=config.SETTINGS.storage)

    # ---------------------------------------------------
    # Load existing branches into the registry
    # ---------------------------------------------------
    branches: list[Branch] = await Branch.get_list(db=db)
    for branch in branches:
        registry.branch[branch.name] = branch

    # ---------------------------------------------------
    # Load internal models into the registry
    # ---------------------------------------------------
    registry.node["Node"] = Node
    registry.node[InfrahubKind.IPPREFIX] = BuiltinIPPrefix
    registry.node[InfrahubKind.IPADDRESSPOOL] = CoreIPAddressPool
    registry.node[InfrahubKind.IPPREFIXPOOL] = CoreIPPrefixPool
    registry.node[InfrahubKind.NUMBERPOOL] = CoreNumberPool

    # ---------------------------------------------------
    # Instantiate permission backends
    # ---------------------------------------------------
    registry.permission_backends = initialize_permission_backends()


async def initialize_tasks() -> None:
    async with get_client(sync_client=False) as client:
        for worker in worker_pools:
            wp = WorkPoolCreate(
                name=worker,
                type="infrahub",
                description="Pool for internal tasks",
            )
            try:
                await client.create_work_pool(work_pool=wp)
                log.info(f"work pool {worker} created successfully ... ")
            except ObjectAlreadyExists:
                log.info(f"work pool {worker} already present ")

        # Create deployment
        for workflow in workflows:
            flow_id = await client.create_flow_from_name(workflow.name)
            await client.create_deployment(flow_id=flow_id, **workflow.to_deployment())


async def initialization(db: InfrahubDatabase) -> None:
    if config.SETTINGS.database.db_type == config.DatabaseType.MEMGRAPH:
        session = await db.session()
        await session.run(query="SET DATABASE SETTING 'log.level' TO 'INFO'")
        await session.run(query="SET DATABASE SETTING 'log.to_stderr' TO 'true'")
        await session.run(query="STORAGE MODE IN_MEMORY_ANALYTICAL")

    # ---------------------------------------------------
    # Initialize the database and Load the Root node
    # ---------------------------------------------------
    async with lock.registry.initialization():
        log.debug("Checking Root Node")
        await initialize_registry(db=db, initialize=True)

        # Add Indexes to the database
        if db.manager.index.initialized:
            log.debug("Loading database indexes ..")
            await db.manager.index.add()
        else:
            log.warning("The database index manager hasn't been initialized.")

        await initialize_tasks()

    # ---------------------------------------------------
    # Load all schema in the database into the registry
    #  ... Unless the schema has been initialized already
    # ---------------------------------------------------
    if not registry.schema_has_been_initialized():
        registry.schema = SchemaManager()
        schema = SchemaRoot(**internal_schema)
        registry.schema.register_schema(schema=schema)

        # Import the default branch
        default_branch: Branch = registry.get_branch_from_registry(branch=registry.default_branch)
        hash_in_db = default_branch.active_schema_hash.main
        schema_default_branch = await registry.schema.load_schema_from_db(db=db, branch=default_branch)
        registry.schema.set_schema_branch(name=default_branch.name, schema=schema_default_branch)

        if default_branch.update_schema_hash():
            log.warning(
                "New schema detected after pulling the schema from the db",
                hash_current=hash_in_db,
                hash_new=default_branch.active_schema_hash.main,
                branch=default_branch.name,
            )

        for branch in list(registry.branch.values()):
            if branch.name in [default_branch.name, GLOBAL_BRANCH_NAME]:
                continue

            hash_in_db = branch.active_schema_hash.main
            log.info("Importing schema", branch=branch.name)
            await registry.schema.load_schema(db=db, branch=branch)

            if branch.update_schema_hash():
                log.warning(
                    f"New schema detected after pulling the schema from the db :"
                    f" {hash_in_db!r} >> {branch.active_schema_hash.main!r}",
                    branch=branch.name,
                )

    # ---------------------------------------------------
    # Load Default Namespace
    # ---------------------------------------------------
    ip_namespace = await get_default_ipnamespace(db=db)
    if ip_namespace:
        registry.default_ipnamespace = ip_namespace.id


async def create_root_node(db: InfrahubDatabase) -> Root:
    root = Root(graph_version=GRAPH_VERSION, default_branch=config.SETTINGS.initial.default_branch)
    await root.save(db=db)
    log.info(f"Generated instance ID : {root.uuid} (v{GRAPH_VERSION})")

    registry.id = root.id
    registry.default_branch = root.default_branch

    return root


async def create_default_branch(db: InfrahubDatabase) -> Branch:
    branch = Branch(
        name=registry.default_branch,
        status="OPEN",
        description="Default Branch",
        hierarchy_level=1,
        is_default=True,
        sync_with_git=True,
    )
    await branch.save(db=db)
    registry.branch[branch.name] = branch

    log.info("Created default branch", branch=branch.name)

    return branch


async def create_global_branch(db: InfrahubDatabase) -> Branch:
    branch = Branch(
        name=GLOBAL_BRANCH_NAME,
        status="OPEN",
        description="Global Branch",
        hierarchy_level=1,
        is_global=True,
        sync_with_git=False,
    )
    await branch.save(db=db)
    registry.branch[branch.name] = branch

    log.info("Created global branch", branch=branch.name)

    return branch


async def create_branch(
    branch_name: str, db: InfrahubDatabase, description: str = "", isolated: bool = True, at: Optional[str] = None
) -> Branch:
    """Create a new Branch, currently all the branches are based on Main

    Because all branches are based on main, the hierarchy_level of hardcoded to 2."""
    description = description or f"Branch {branch_name}"
    branch = Branch(
        name=branch_name,
        status="OPEN",
        hierarchy_level=2,
        description=description,
        is_default=False,
        sync_with_git=False,
        created_at=at,
        branched_from=at,
        is_isolated=isolated,
    )

    origin_schema = registry.schema.get_schema_branch(name=branch.origin_branch)
    new_schema = origin_schema.duplicate(name=branch.name)
    registry.schema.set_schema_branch(name=branch.name, schema=new_schema)

    branch.update_schema_hash()
    await branch.save(db=db)
    registry.branch[branch.name] = branch

    log.info("Created branch", branch=branch.name)

    return branch


async def create_account(
    db: InfrahubDatabase,
    name: str = "admin",
    role: str = "admin",
    password: Optional[str] = None,
    token_value: Optional[str] = None,
) -> CoreAccount:
    token_schema = db.schema.get_node_schema(name=InfrahubKind.ACCOUNTTOKEN)
    obj = await Node.init(db=db, schema=CoreAccount)
    await obj.new(db=db, name=name, account_type="User", role=role, password=password)
    await obj.save(db=db)
    log.info(f"Created Account: {name}", account_name=name)

    if token_value:
        token = await Node.init(db=db, schema=token_schema)
        await token.new(db=db, token=token_value, name="Created automatically", account=obj)
        await token.save(db=db)

    return obj


async def create_ipam_namespace(
    db: InfrahubDatabase,
    name: str = DEFAULT_IP_NAMESPACE,
    description: str = "Used to provide a default space of IP resources",
) -> Node:
    obj = await Node.init(db=db, schema=InfrahubKind.NAMESPACE)
    await obj.new(db=db, name=name, description=description, default=True)
    await obj.save(db=db)
    log.info(f"Created IPAM Namespace: {name}")

    return obj


async def create_global_permissions(db: InfrahubDatabase) -> list[Node]:
    objs: list[Node] = []

    for permission in GlobalPermissions:
        obj = await Node.init(db=db, schema=InfrahubKind.GLOBALPERMISSION)
        await obj.new(db=db, name=format_label(permission.value), action=permission.value)
        await obj.save(db=db)
        objs.append(obj)
        log.info(f"Created global permission: {permission}")

    return objs


async def create_administrator_role(db: InfrahubDatabase, global_permissions: Optional[list[Node]] = None) -> Node:
    role_name = "Administrator"
    obj = await Node.init(db=db, schema=InfrahubKind.USERROLE)
    await obj.new(db=db, name=role_name, permissions=global_permissions)
    await obj.save(db=db)
    log.info(f"Created User Role: {role_name}")

    return obj


async def create_administrators_group(db: InfrahubDatabase, role: Node, admin_accounts: list[CoreAccount]) -> Node:
    group_name = "Administrators"
    group = await Node.init(db=db, schema=InfrahubKind.USERGROUP)
    await group.new(db=db, name=group_name, roles=[role])
    await group.save(db=db)
    log.info(f"Created User Group: {group_name}")

    for admin_account in admin_accounts:
        await group.members.add(db=db, data=admin_account)  # type: ignore[attr-defined]
        await group.members.save(db=db)  # type: ignore[attr-defined]
        log.info(f"Assigned User Group: {group_name} to {admin_account.name.value}")

    return group


async def first_time_initialization(db: InfrahubDatabase) -> None:
    # --------------------------------------------------
    # Create the default Branch
    # --------------------------------------------------
    await create_root_node(db=db)
    default_branch = await create_default_branch(db=db)
    await create_global_branch(db=db)

    # --------------------------------------------------
    # Load the internal and core schema in the database
    # --------------------------------------------------
    registry.schema = SchemaManager()
    schema = SchemaRoot(**internal_schema)
    schema_branch = registry.schema.register_schema(schema=schema, branch=default_branch.name)
    schema_branch.load_schema(schema=SchemaRoot(**core_models))
    schema_branch.process()
    await registry.schema.load_schema_to_db(schema=schema_branch, branch=default_branch, db=db)
    registry.schema.set_schema_branch(name=default_branch.name, schema=schema_branch)
    default_branch.update_schema_hash()
    await default_branch.save(db=db)
    log.info("Created the Schema in the database", hash=default_branch.active_schema_hash.main)

    # --------------------------------------------------
    # Create Default Users and Groups
    # --------------------------------------------------
    admin_accounts: list[CoreAccount] = []
    admin_accounts.append(
        await create_account(
            db=db,
            name="admin",
            password=config.SETTINGS.initial.admin_password,
            token_value=config.SETTINGS.initial.admin_token,
        )
    )

    if config.SETTINGS.initial.create_agent_user:
        password = config.SETTINGS.initial.agent_password or str(uuid4())

        admin_accounts.append(
            await create_account(
                db=db,
                name="agent",
                password=password,
                role=AccountRole.READ_WRITE.value,
                token_value=config.SETTINGS.initial.agent_token,
            )
        )

    # --------------------------------------------------
    # Create Global Permissions and assign them
    # --------------------------------------------------
    global_permissions = await create_global_permissions(db=db)
    administrator_role = await create_administrator_role(db=db, global_permissions=global_permissions)
    await create_administrators_group(db=db, role=administrator_role, admin_accounts=admin_accounts)

    # --------------------------------------------------
    # Create Default IPAM Namespace
    # --------------------------------------------------
    await create_ipam_namespace(db=db)
