import React from 'react'
import { connect } from 'react-redux'
import Article from './Article'

const ArticleList = (props) => {

 if (props.visibleArticles == null)
  return <div />

 if (props.visibleArticles.length === 0)
  return (
    <div className="results">
      <h3 className="title noneFound">Nenhum documento encontrado</h3>
    </div>
  )

 return (
    <div className="results">
      {props.visibleArticles.map(article =>
        <Article
          key={article.path}
          article={article}
        />)}
    </div>
  )
}

const mapStateToProps = (state) => {
  return {
    visibleArticles: state.articles
  }
}

export default connect(
  mapStateToProps,
  null
)(ArticleList)
