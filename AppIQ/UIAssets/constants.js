export const PROFILE_NAME = "datacenterName";

export const DC_DETAILS_QUERY_PAYLOAD = (tn) => {
    return { query: 'query{Details(tn:"' + tn + '"){details}}' }
}

export const TREE_VIEW_QUERY_PAYLOAD = (tn) => {
    return { query: 'query{Run(tn:"' + tn + '"){response}}' }
}