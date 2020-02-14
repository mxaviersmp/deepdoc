import articleService from '../services/articles'

const articleReducer = (state = [], action) => {
  switch(action.type) {
    case 'INIT_ARTICLES':
      return action.data
    case 'SEARCH_TERMS':
      return action.data
    default:
      return state
  }
}

export const initializeArticles = () => {
  return async dispatch => {
    dispatch({
      type: 'INIT_ARTICLES',
      data: null
    })
  }
}

export const searchTerms = search => {
  return async dispatch => {
    const articles = await articleService.searchTerms(search)
    dispatch({
      type: 'SEARCH_TERMS',
      data: articles.results
    })
  }
}

export default articleReducer
