import React, { useEffect } from 'react'
import { connect } from 'react-redux'
import ArticleForm from './components/ArticleForm'
import ArticleList from './components/ArticleList'
import NavBar from './components/NavBar'
import { initializeArticles } from './reducers/articleReducer'
import './static/style.css'

const App = (props) => {

  useEffect(() => {
    props.initializeArticles()
  })

  return (
    <div className="pageBody">
      <NavBar />
      <ArticleForm />
      <ArticleList />
    </div>
  )
}

export default connect(
  null,
  { initializeArticles }
)(App)
