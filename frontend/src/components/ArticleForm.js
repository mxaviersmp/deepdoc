import React from 'react'
import { connect } from 'react-redux'
import { searchTerms } from '../reducers/articleReducer'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch } from '@fortawesome/free-solid-svg-icons'


const ArticleForm = (props) => {

  const searchArticle = (event) => {
    event.preventDefault()
    props.searchTerms(event.target.article.value)
  }

  return (
    <form onSubmit={searchArticle} className="search">
      <input name="article" className="searchBar" placeholder="Insira os termos de busca, separados por ','"/>
      <button type="submit" className="searchButton"><FontAwesomeIcon icon={faSearch} size="lg"/></button>
    </form>
  )
}

export default connect(
  null,
  { searchTerms }
)(ArticleForm)
