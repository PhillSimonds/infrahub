/**
 * This file was auto-generated by openapi-typescript.
 * Do not make direct changes to the file.
 */

export interface paths {
  "/schema/": {
    /** Get Schema */
    get: operations["get_schema_schema__get"];
  };
  "/schema/load": {
    /** Load Schema */
    post: operations["load_schema_schema_load_post"];
  };
  "/transform/{transform_url}": {
    /** Transform Python */
    get: operations["transform_python_transform__transform_url__get"];
  };
  "/rfile/{rfile_id}": {
    /** Generate Rfile */
    get: operations["generate_rfile_rfile__rfile_id__get"];
  };
  "/config": {
    /** Get Config */
    get: operations["get_config_config_get"];
  };
  "/info": {
    /** Get Info */
    get: operations["get_info_info_get"];
  };
  "/diff/data": {
    /** Get Diff Data */
    get: operations["get_diff_data_diff_data_get"];
  };
  "/diff/files": {
    /** Get Diff Files */
    get: operations["get_diff_files_diff_files_get"];
  };
  "/dev/diff/data": {
    /** Get Diff Data */
    get: operations["get_diff_data_dev_diff_data_get"];
  };
  "/dev/diff/files": {
    /** Get Diff Files */
    get: operations["get_diff_files_dev_diff_files_get"];
  };
  "/query/{query_id}": {
    /** Graphql Query */
    get: operations["graphql_query_query__query_id__get"];
  };
}

export type webhooks = Record<string, never>;

export interface components {
  schemas: {
    /**
     * AnalyticsSettings
     * @description Base class for settings, allowing values to be overridden by environment variables.
     *
     * This is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),
     * Heroku and any 12 factor app design.
     */
    AnalyticsSettings: {
      /**
       * Enable
       * @default true
       */
      enable?: boolean;
      /** Address */
      address?: string;
      /** Api Key */
      api_key?: string;
    };
    /** AttributeSchema */
    AttributeSchema: {
      read_only: boolean | undefined;
      /** Id */
      id?: string;
      /** Name */
      name: string;
      /** Kind */
      kind: string;
      /** Label */
      label?: string;
      /** Description */
      description?: string;
      /** Default Value */
      default_value?: Record<string, never>;
      /** Enum */
      enum?: Record<string, never>[];
      /** Regex */
      regex?: string;
      /** Max Length */
      max_length?: number;
      /** Min Length */
      min_length?: number;
      /**
       * Inherited
       * @default false
       */
      inherited?: boolean;
      /**
       * Unique
       * @default false
       */
      unique?: boolean;
      /**
       * Branch
       * @default true
       */
      branch?: boolean;
      /**
       * Optional
       * @default false
       */
      optional?: boolean;
      /** Order Weight */
      order_weight?: number;
    };
    /** BranchDiffRelationship */
    BranchDiffRelationship: {
      /** Branch */
      branch: string;
      /** Id */
      id: string;
      /** Identifier */
      identifier: string;
      /** Name */
      name: string;
      peer: components["schemas"]["infrahub__api__diff__BranchDiffRelationshipPeerNode"];
      /** Properties */
      properties: components["schemas"]["infrahub__api__diff__BranchDiffProperty"][];
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
    };
    /** BranchDiffRelationshipMany */
    BranchDiffRelationshipMany: {
      /** @default RelationshipMany */
      type?: components["schemas"]["DiffElementType"];
      /** Branch */
      branch: string;
      /** Identifier */
      identifier: string;
      /**
       * Summary
       * @default {
       *   "added": 0,
       *   "removed": 0,
       *   "updated": 0
       * }
       */
      summary?: components["schemas"]["DiffSummary"];
      /** Name */
      name: string;
      /** Peers */
      peers?: components["schemas"]["BranchDiffRelationshipManyElement"][];
    };
    /** BranchDiffRelationshipManyElement */
    BranchDiffRelationshipManyElement: {
      /** Branch */
      branch: string;
      /** Id */
      id: string;
      /** Identifier */
      identifier: string;
      /**
       * Summary
       * @default {
       *   "added": 0,
       *   "removed": 0,
       *   "updated": 0
       * }
       */
      summary?: components["schemas"]["DiffSummary"];
      peer: components["schemas"]["infrahub__api__dev_diff__BranchDiffRelationshipPeerNode"];
      /** Properties */
      properties?: components["schemas"]["infrahub__api__dev_diff__BranchDiffProperty"][];
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
    };
    /** BranchDiffRelationshipOne */
    BranchDiffRelationshipOne: {
      /** @default RelationshipOne */
      type?: components["schemas"]["DiffElementType"];
      /** Branch */
      branch: string;
      /** Id */
      id: string;
      /** Identifier */
      identifier: string;
      /**
       * Summary
       * @default {
       *   "added": 0,
       *   "removed": 0,
       *   "updated": 0
       * }
       */
      summary?: components["schemas"]["DiffSummary"];
      /** Name */
      name: string;
      peer: components["schemas"]["BranchDiffRelationshipOnePeerValue"];
      /** Properties */
      properties?: components["schemas"]["infrahub__api__dev_diff__BranchDiffProperty"][];
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
    };
    /** BranchDiffRelationshipOnePeerValue */
    BranchDiffRelationshipOnePeerValue: {
      new?: components["schemas"]["infrahub__api__dev_diff__BranchDiffRelationshipPeerNode"];
      previous?: components["schemas"]["infrahub__api__dev_diff__BranchDiffRelationshipPeerNode"];
    };
    /** ConfigAPI */
    ConfigAPI: {
      main: components["schemas"]["MainSettings"];
      logging: components["schemas"]["LoggingSettings"];
      analytics: components["schemas"]["AnalyticsSettings"];
    };
    /**
     * DiffAction
     * @description An enumeration.
     * @enum {unknown}
     */
    DiffAction: "added" | "removed" | "updated";
    /**
     * DiffElementType
     * @description An enumeration.
     * @enum {unknown}
     */
    DiffElementType: "Attribute" | "RelationshipOne" | "RelationshipMany";
    /** DiffSummary */
    DiffSummary: {
      /**
       * Added
       * @default 0
       */
      added?: number;
      /**
       * Removed
       * @default 0
       */
      removed?: number;
      /**
       * Updated
       * @default 0
       */
      updated?: number;
    };
    /** FilterSchema */
    FilterSchema: {
      /** Name */
      name: string;
      kind: components["schemas"]["FilterSchemaKind"];
      /** Enum */
      enum?: Record<string, never>[];
      /** Object Kind */
      object_kind?: string;
      /** Description */
      description?: string;
    };
    /**
     * FilterSchemaKind
     * @description An enumeration.
     * @enum {string}
     */
    FilterSchemaKind: "Text" | "Number" | "Boolean" | "Object" | "MultiObject" | "Enum";
    /**
     * GenericSchema
     * @description A Generic can be either an Interface or a Union depending if there are some Attributes or Relationships defined.
     */
    GenericSchema: {
      /** Id */
      id?: string;
      /** Name */
      name: string;
      /** Kind */
      kind: string;
      /** Description */
      description?: string;
      /** Default Filter */
      default_filter?: string;
      /** Display Labels */
      display_labels?: string[];
      /** Attributes */
      attributes?: components["schemas"]["AttributeSchema"][];
      /** Relationships */
      relationships?: components["schemas"]["RelationshipSchema"][];
      /**
       * Branch
       * @default true
       */
      branch?: boolean;
      /** Label */
      label?: string;
      /** Used By */
      used_by?: string[];
    };
    /** GroupSchema */
    GroupSchema: {
      /** Id */
      id?: string;
      /** Name */
      name: string;
      /** Kind */
      kind: string;
      /** Description */
      description?: string;
    };
    /** HTTPValidationError */
    HTTPValidationError: {
      /** Detail */
      detail?: components["schemas"]["ValidationError"][];
    };
    /** InfoAPI */
    InfoAPI: {
      /** Deployment Id */
      deployment_id: string;
      /** Version */
      version: string;
    };
    /**
     * LoggingSettings
     * @description Base class for settings, allowing values to be overridden by environment variables.
     *
     * This is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),
     * Heroku and any 12 factor app design.
     */
    LoggingSettings: {
      /**
       * Remote
       * @default {
       *   "enable": false
       * }
       */
      remote?: components["schemas"]["RemoteLoggingSettings"];
    };
    /**
     * MainSettings
     * @description Base class for settings, allowing values to be overridden by environment variables.
     *
     * This is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),
     * Heroku and any 12 factor app design.
     */
    MainSettings: {
      /**
       * Default Branch
       * @default main
       */
      default_branch?: string;
      /**
       * Internal Address
       * @default http://localhost:8000
       */
      internal_address?: string;
    };
    /** NodeExtensionSchema */
    NodeExtensionSchema: {
      /** Kind */
      kind: string;
      /** Attributes */
      attributes?: components["schemas"]["AttributeSchema"][];
      /** Relationships */
      relationships?: components["schemas"]["RelationshipSchema"][];
    };
    /** NodeSchema */
    NodeSchema: {
      /** Id */
      id?: string;
      /** Name */
      name: string;
      /** Kind */
      kind: string;
      /** Description */
      description?: string;
      /** Default Filter */
      default_filter?: string;
      /** Display Labels */
      display_labels?: string[];
      /** Attributes */
      attributes?: components["schemas"]["AttributeSchema"][];
      /** Relationships */
      relationships?: components["schemas"]["RelationshipSchema"][];
      /** Label */
      label?: string;
      /** Inherit From */
      inherit_from?: string[];
      /** Groups */
      groups?: string[];
      /**
       * Branch
       * @default true
       */
      branch?: boolean;
      /** Filters */
      filters?: components["schemas"]["FilterSchema"][];
    };
    /**
     * RelationshipCardinality
     * @description An enumeration.
     * @enum {string}
     */
    RelationshipCardinality: "one" | "many";
    /**
     * RelationshipKind
     * @description An enumeration.
     * @enum {string}
     */
    RelationshipKind: "Generic" | "Attribute" | "Component" | "Parent";
    /** RelationshipSchema */
    RelationshipSchema: {
      read_only: any;
      /** Id */
      id?: string;
      /** Name */
      name: string;
      /** Peer */
      peer: string;
      /** @default Generic */
      kind?: components["schemas"]["RelationshipKind"];
      /** Label */
      label?: string;
      /** Description */
      description?: string;
      /** Identifier */
      identifier?: string;
      /**
       * Inherited
       * @default false
       */
      inherited?: boolean;
      /** @default many */
      cardinality?: components["schemas"]["RelationshipCardinality"];
      /**
       * Branch
       * @default true
       */
      branch?: boolean;
      /**
       * Optional
       * @default true
       */
      optional?: boolean;
      /** Filters */
      filters?: components["schemas"]["FilterSchema"][];
      /** Order Weight */
      order_weight?: number;
    };
    /**
     * RemoteLoggingSettings
     * @description Base class for settings, allowing values to be overridden by environment variables.
     *
     * This is useful in production for secrets you do not wish to save in code, it plays nicely with docker(-compose),
     * Heroku and any 12 factor app design.
     */
    RemoteLoggingSettings: {
      /**
       * Enable
       * @default false
       */
      enable?: boolean;
      /** Frontend Dsn */
      frontend_dsn?: string;
      /** Api Server Dsn */
      api_server_dsn?: string;
      /** Git Agent Dsn */
      git_agent_dsn?: string;
    };
    /** SchemaExtension */
    SchemaExtension: {
      /** Nodes */
      nodes?: components["schemas"]["NodeExtensionSchema"][];
    };
    /** SchemaLoadAPI */
    SchemaLoadAPI: {
      /** Version */
      version: string;
      /** Generics */
      generics?: components["schemas"]["GenericSchema"][];
      /** Nodes */
      nodes?: components["schemas"]["NodeSchema"][];
      /** Groups */
      groups?: components["schemas"]["GroupSchema"][];
      /**
       * Extensions
       * @default {
       *   "nodes": []
       * }
       */
      extensions?: components["schemas"]["SchemaExtension"];
    };
    /** SchemaReadAPI */
    SchemaReadAPI: {
      /** Nodes */
      nodes: components["schemas"]["NodeSchema"][];
      /** Generics */
      generics: components["schemas"]["GenericSchema"][];
    };
    /** ValidationError */
    ValidationError: {
      /** Location */
      loc: (string | number)[];
      /** Message */
      msg: string;
      /** Error Type */
      type: string;
    };
    /** BranchDiffAttribute */
    infrahub__api__dev_diff__BranchDiffAttribute: {
      /** @default Attribute */
      type?: components["schemas"]["DiffElementType"];
      /** Name */
      name: string;
      /** Id */
      id: string;
      /** Changed At */
      changed_at?: string;
      /**
       * Summary
       * @default {
       *   "added": 0,
       *   "removed": 0,
       *   "updated": 0
       * }
       */
      summary?: components["schemas"]["DiffSummary"];
      action: components["schemas"]["DiffAction"];
      value?: components["schemas"]["infrahub__api__dev_diff__BranchDiffProperty"];
      /** Properties */
      properties: components["schemas"]["infrahub__api__dev_diff__BranchDiffProperty"][];
    };
    /** BranchDiffFile */
    infrahub__api__dev_diff__BranchDiffFile: {
      /** Branch */
      branch: string;
      /** Location */
      location: string;
      action: components["schemas"]["DiffAction"];
    };
    /** BranchDiffNode */
    infrahub__api__dev_diff__BranchDiffNode: {
      /** Branch */
      branch: string;
      /** Kind */
      kind: string;
      /** Id */
      id: string;
      /**
       * Summary
       * @default {
       *   "added": 0,
       *   "removed": 0,
       *   "updated": 0
       * }
       */
      summary?: components["schemas"]["DiffSummary"];
      /** Display Label */
      display_label: string;
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
      /** Elements */
      elements?: {
        [key: string]:
          | (
              | components["schemas"]["BranchDiffRelationshipOne"]
              | components["schemas"]["BranchDiffRelationshipMany"]
              | components["schemas"]["infrahub__api__dev_diff__BranchDiffAttribute"]
            )
          | undefined;
      };
    };
    /** BranchDiffProperty */
    infrahub__api__dev_diff__BranchDiffProperty: {
      /** Branch */
      branch: string;
      /** Type */
      type: string;
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
      value: components["schemas"]["infrahub__api__dev_diff__BranchDiffPropertyValue"];
    };
    /** BranchDiffPropertyValue */
    infrahub__api__dev_diff__BranchDiffPropertyValue: {
      /** New */
      new?: Record<string, never>;
      /** Previous */
      previous?: Record<string, never>;
    };
    /** BranchDiffRelationshipPeerNode */
    infrahub__api__dev_diff__BranchDiffRelationshipPeerNode: {
      /** Id */
      id: string;
      /** Kind */
      kind: string;
      /** Display Label */
      display_label?: string;
    };
    /** BranchDiffRepository */
    infrahub__api__dev_diff__BranchDiffRepository: {
      /** Branch */
      branch: string;
      /** Id */
      id: string;
      /** Display Name */
      display_name?: string;
      /** Files */
      files?: components["schemas"]["infrahub__api__dev_diff__BranchDiffFile"][];
    };
    /** BranchDiffAttribute */
    infrahub__api__diff__BranchDiffAttribute: {
      /** Name */
      name: string;
      /** Id */
      id: string;
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
      /** Properties */
      properties: components["schemas"]["infrahub__api__diff__BranchDiffProperty"][];
    };
    /** BranchDiffFile */
    infrahub__api__diff__BranchDiffFile: {
      /** Branch */
      branch: string;
      /** Location */
      location: string;
      action: components["schemas"]["DiffAction"];
    };
    /** BranchDiffNode */
    infrahub__api__diff__BranchDiffNode: {
      /** Branch */
      branch: string;
      /** Kind */
      kind: string;
      /** Id */
      id: string;
      /** Display Label */
      display_label: string;
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
      /** Attributes */
      attributes?: components["schemas"]["infrahub__api__diff__BranchDiffAttribute"][];
      /** Relationships */
      relationships?: components["schemas"]["BranchDiffRelationship"][];
    };
    /** BranchDiffProperty */
    infrahub__api__diff__BranchDiffProperty: {
      /** Branch */
      branch: string;
      /** Type */
      type: string;
      /** Changed At */
      changed_at?: string;
      action: components["schemas"]["DiffAction"];
      value: components["schemas"]["infrahub__api__diff__BranchDiffPropertyValue"];
    };
    /** BranchDiffPropertyValue */
    infrahub__api__diff__BranchDiffPropertyValue: {
      /** New */
      new?: Record<string, never>;
      /** Previous */
      previous?: Record<string, never>;
    };
    /** BranchDiffRelationshipPeerNode */
    infrahub__api__diff__BranchDiffRelationshipPeerNode: {
      /** Id */
      id: string;
      /** Kind */
      kind: string;
      /** Display Label */
      display_label?: string;
    };
    /** BranchDiffRepository */
    infrahub__api__diff__BranchDiffRepository: {
      /** Branch */
      branch: string;
      /** Id */
      id: string;
      /** Display Name */
      display_name?: string;
      /** Files */
      files?: components["schemas"]["infrahub__api__diff__BranchDiffFile"][];
    };
  };
  responses: never;
  parameters: never;
  requestBodies: never;
  headers: never;
  pathItems: never;
}

export type external = Record<string, never>;

export interface operations {
  /** Get Schema */
  get_schema_schema__get: {
    parameters: {
      query: {
        branch?: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["SchemaReadAPI"];
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Load Schema */
  load_schema_schema_load_post: {
    parameters: {
      query: {
        branch?: string;
      };
    };
    requestBody: {
      content: {
        "application/json": components["schemas"]["SchemaLoadAPI"];
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Transform Python */
  transform_python_transform__transform_url__get: {
    parameters: {
      query: {
        branch?: string;
        at?: string;
        rebase?: boolean;
      };
      path: {
        transform_url: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Generate Rfile */
  generate_rfile_rfile__rfile_id__get: {
    parameters: {
      query: {
        branch?: string;
        at?: string;
        rebase?: boolean;
      };
      path: {
        rfile_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "text/plain": string;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Config */
  get_config_config_get: {
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["ConfigAPI"];
        };
      };
    };
  };
  /** Get Info */
  get_info_info_get: {
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": components["schemas"]["InfoAPI"];
        };
      };
    };
  };
  /** Get Diff Data */
  get_diff_data_diff_data_get: {
    parameters: {
      query: {
        branch?: string;
        time_from?: string;
        time_to?: string;
        branch_only?: boolean;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": {
            [key: string]:
              | components["schemas"]["infrahub__api__diff__BranchDiffNode"][]
              | undefined;
          };
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Diff Files */
  get_diff_files_diff_files_get: {
    parameters: {
      query: {
        branch?: string;
        time_from?: string;
        time_to?: string;
        branch_only?: boolean;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": {
            [key: string]:
              | {
                  [key: string]:
                    | components["schemas"]["infrahub__api__diff__BranchDiffRepository"]
                    | undefined;
                }
              | undefined;
          };
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Diff Data */
  get_diff_data_dev_diff_data_get: {
    parameters: {
      query: {
        branch?: string;
        time_from?: string;
        time_to?: string;
        branch_only?: boolean;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": {
            [key: string]:
              | components["schemas"]["infrahub__api__dev_diff__BranchDiffNode"][]
              | undefined;
          };
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Get Diff Files */
  get_diff_files_dev_diff_files_get: {
    parameters: {
      query: {
        branch?: string;
        time_from?: string;
        time_to?: string;
        branch_only?: boolean;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": {
            [key: string]:
              | {
                  [key: string]:
                    | components["schemas"]["infrahub__api__dev_diff__BranchDiffRepository"]
                    | undefined;
                }
              | undefined;
          };
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
  /** Graphql Query */
  graphql_query_query__query_id__get: {
    parameters: {
      query: {
        branch?: string;
        at?: string;
        rebase?: boolean;
      };
      path: {
        query_id: string;
      };
    };
    responses: {
      /** @description Successful Response */
      200: {
        content: {
          "application/json": Record<string, never>;
        };
      };
      /** @description Validation Error */
      422: {
        content: {
          "application/json": components["schemas"]["HTTPValidationError"];
        };
      };
    };
  };
}
