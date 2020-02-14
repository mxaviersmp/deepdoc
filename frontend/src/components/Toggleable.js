import React, { useState, useImperativeHandle } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSortUp, faSortDown } from '@fortawesome/free-solid-svg-icons'

const Toggleable = React.forwardRef((props, ref) => {
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

export default Toggleable
