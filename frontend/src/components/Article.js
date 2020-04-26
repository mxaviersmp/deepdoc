import React from 'react'
import { connect } from 'react-redux'
import Toggleable from './Toggleable'

const Article = ({ article }) => {

  const divStyle = {
    padding: '1%',
    margin: '1%'
  }

  const tagComparator = (a, b) => {
    if (a[1] < b[1]) return 1;
    if (a[1] > b[1]) return -1;
    return 0;
  }

  const terms = Object.entries(JSON.parse(article.occurrences))
  const categories = Object.entries(JSON.parse(article.categories))

  return (
    <div key={article.path} style={divStyle}>
      <h3>
        <a  className="title" href={`http://localhost:5000/pdf?file=${article.path}`}
          target='_blank' rel="noopener noreferrer">{article.title}</a>
      </h3>
      <div className="occurrences">
        <span className="keyWords">Palavras-chave: </span>
          {terms.map(t =>
            <>
              <span className="term">{t[0]}</span>
              {" "}
              <span className="occurrencesChip">{t[1]}</span>
            </>
          )}
      </div>
      <div>
      <Toggleable>
        <table className="categories">
          <tbody>
          {categories.map(
            c =>  <tr>
                    <td className="categoryChip">{c[0]}</td>
                    <td>{c[1].sort(tagComparator).map(k =>
                      <span className="tagChip">{` ${k[0]} (${k[1]}) `}</span>
                      )}</td>
                  </tr>
          )}
          </tbody>
        </table>
      </Toggleable>
      </div>
      <div className="smallGrayBar" />
    </div>
  )
}

export default connect(
  null,
  null
)(Article)
