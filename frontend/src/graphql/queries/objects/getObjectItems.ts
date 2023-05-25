declare const Handlebars: any;

export const getObjectItems = Handlebars.compile(`
query {{kind}} {
  {{name}}{{#if filters}}({{{filters}}}){{/if}} {
    count
    edges {
      node {
        id
        display_label

        {{#each attributes}}
          {{this.name}} {
              value
          }
        {{/each}}

        {{#each relationships}}
          {{this.name}} {
              display_label
          }
        {{/each}}
      }
    }
  }
}
`);
