#plural pages
{
    pages {
            children {
              slug
              title
              id
            }
        }
}

{
    images {
        title
    }
}

{
    sites {
        port
        hostname
    }
}

{
    page(slug:"blog") {
        ...on BlogPage {
            title
          id
        }
    }
}


{
    page(slug:"blog") {
        ...on BlogPage {
          title
          summary
          author
          id
          date
          body {
            		id
            		rawValue
            ...on ImageChooserBlock {
                    image {
                        file
                    }
                }
          }
        }
    }
}


{
    page(slug:"blog") {
        ...on BlogPage {
          title
          summary
          id
          date
          body {
... on TextAndButtonsBlock {
                mainbutton {
                    ... on ButtonBlock {
                        buttonText
                        buttonLink
                    }
                }
                buttons {
                    ... on ButtonBlock {
                        buttonText
                        buttonLink
                    }
                }
            }
          }
        }
    }
}









