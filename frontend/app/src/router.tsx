import { createBrowserRouter, Navigate, Outlet } from "react-router-dom";
import { IPAM_ROUTE } from "@/screens/ipam/constants";
import { ARTIFACT_OBJECT, GRAPHQL_QUERY_OBJECT } from "@/config/constants";
import { Root } from "@/Root";
import { ReactRouter6Adapter } from "use-query-params/adapters/react-router-6";
import queryString from "query-string";
import { RequireAuth } from "@/hooks/useAuth";
import { QueryParamProvider } from "use-query-params";

export const router = createBrowserRouter([
  {
    path: "",
    element: (
      <Root>
        <RequireAuth>
          <QueryParamProvider
            adapter={ReactRouter6Adapter}
            options={{
              searchStringToObject: queryString.parse,
              objectToSearchString: queryString.stringify,
            }}>
            <Outlet />
          </QueryParamProvider>
        </RequireAuth>
      </Root>
    ),
    children: [
      {
        path: "/",
        lazy: () => import("@/screens/layout/layout"),
        children: [
          {
            path: "/branches/:branchName",
            lazy: () => import("@/screens/branches/branch-item-details"),
          },
          {
            path: "/branches",
            lazy: () => import("@/screens/branches/branches-items"),
          },
          {
            path: `/objects/${ARTIFACT_OBJECT}/:objectid`,
            lazy: () => import("@/screens/artifacts/object-item-details-paginated"),
          },
          {
            path: `/objects/${GRAPHQL_QUERY_OBJECT}/:graphqlQueryId`,
            lazy: () => import("@/screens/graphql/details/graphql-query-details-page"),
          },
          {
            path: "/objects",
            lazy: () => import("@/pages/objects/layout"),
            children: [
              {
                path: ":objectKind",
                lazy: () => import("@/pages/objects/object-items"),
              },
              {
                path: ":objectKind/:objectid",
                lazy: () => import("@/pages/objects/object-details"),
              },
            ],
          },
          {
            path: "/profile",
            lazy: () => import("@/screens/user-profile/user-profile"),
          },
          {
            path: "/proposed-changes/new",
            lazy: () => import("@/pages/proposed-changes/new"),
          },
          {
            path: "/proposed-changes/:proposedchange",
            lazy: () => import("@/screens/proposed-changes/proposed-changes-details"),
          },
          {
            path: "/proposed-changes",
            lazy: () => import("@/screens/proposed-changes/proposed-changes-items"),
          },
          {
            path: "/tasks/:task",
            lazy: () => import("@/screens/tasks/task-item-details-screen"),
          },
          {
            path: "/tasks",
            lazy: () => import("@/screens/tasks/task-items-screen"),
          },
          {
            path: "/graphql/:branch",
            lazy: () => import("@/screens/graphql/redirect-to-graphql-sandbox-page"),
          },
          {
            path: "graphql",
            lazy: () => import("@/screens/graphql/graphql-sandbox-page"),
          },
          {
            path: "/resource-manager",
            lazy: () => import("@/pages/resource-manager"),
          },
          {
            path: "/resource-manager/:resourcePoolId",
            lazy: () => import("@/pages/resource-manager/resource-pool-details"),
            children: [
              {
                path: "resources/:resourceId",
                lazy: () => import("@/pages/resource-manager/resource-allocation-details"),
              },
            ],
          },
          {
            path: "/schema",
            lazy: () => import("@/pages/schema"),
          },
          {
            path: IPAM_ROUTE.INDEX,
            lazy: () => import("@/screens/ipam/ipam-page"),
            children: [
              {
                index: true,
                lazy: () => import("@/screens/ipam/ipam-router"),
              },
              {
                path: IPAM_ROUTE.ADDRESSES,
                lazy: () => import("@/screens/ipam/ipam-router"),
                children: [
                  {
                    path: ":ip_address",
                    lazy: () => import("@/screens/ipam/ipam-router"),
                  },
                ],
              },
              {
                path: IPAM_ROUTE.PREFIXES,
                lazy: () => import("@/screens/ipam/ipam-router"),
                children: [
                  {
                    path: ":prefix",
                    lazy: () => import("@/screens/ipam/ipam-router"),
                    children: [
                      {
                        path: ":ip_address",
                        lazy: () => import("@/screens/ipam/ipam-router"),
                      },
                    ],
                  },
                ],
              },
            ],
          },
          {
            path: "/",
            lazy: () => import("@/pages/homepage"),
          },
          {
            path: "*",
            element: <Navigate to="/" />,
          },
        ],
      },
    ],
  },
  {
    path: "/signin",
    lazy: () => import("@/screens/sign-in/sign-in"),
  },
]);
