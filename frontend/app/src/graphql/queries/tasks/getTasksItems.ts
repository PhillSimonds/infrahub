import Handlebars from "handlebars";

export const getTasksItems = Handlebars.compile(`
query GetTasks($offset: Int, $limit: Int) {
  {{kind}}(offset: $offset, limit: $limit, {{#if relatedNode}}related_node__ids: ["{{relatedNode}}"]{{/if}}) {
    count
    edges {
      node {
        conclusion
        created_at
        id
        related_node
        related_node_kind
        title
        updated_at
      }
    }
  }
}
`);
