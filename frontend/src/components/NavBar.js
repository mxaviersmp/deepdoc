import React from 'react'

const NavBar = () => {

  return (
    <div>
      <img  src={require('../static/img/logo-deepdoc.png')}
            alt="logomarca da ferramenta deepdoc"
            className='logo' />
      <div className='grayBar' />
    </div>
  )
}

export default NavBar
