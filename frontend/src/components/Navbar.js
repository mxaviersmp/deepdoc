import React from 'react'

const Navbar = () => {

  return (
    <div>
      <img  src={require('../static/img/logo-deepdoc.png')} 
            alt="logomarca da ferramenta deepdoc"
            className='logo'></img>
      <div className='grayBar' />
    </div>
  )
}

export default Navbar
