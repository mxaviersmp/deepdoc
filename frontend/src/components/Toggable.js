import React, { useState, useImperativeHandle } from 'react'
import PropTypes from 'prop-types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSortUp, faSortDown } from '@fortawesome/free-solid-svg-icons'

const Togglable = React.forwardRef((props, ref) => {
  const [visible, setVisible] = useState(false)

  const hideWhenVisible = { display: visible ? 'none' : '' }
  const showWhenVisible = { display: visible ? '' : 'none' }

  const toggleVisibility = () => {
    setVisible(!visible)
  }

  useImperativeHandle(ref, () => ({
    toggleVisibility,
  }))

  return (
    <div>
      <div style={hideWhenVisible}>
        <button className="viewCategories" 
                type="button" 
                onClick={toggleVisibility} 
                onKeyDown={toggleVisibility}>Ver categorias <FontAwesomeIcon icon={faSortDown} size="lg"/></button>
      </div>
      <div style={showWhenVisible}>
        <button className="viewCategories"
                type="button"
                onClick={toggleVisibility}
                onKeyDown={toggleVisibility}>Esconder categorias <FontAwesomeIcon icon={faSortUp} size="lg"/></button>
        {props.children}
      </div>
    </div>
  )
})

Togglable.propTypes = {
  buttonLabel: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
}

export default Togglable
