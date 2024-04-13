import { useState } from 'react'
import './App.css'

import Kodos from './Kodos'
import KodosSettings from './KodosSettings'

function App() {
  const [count, setCount] = useState(0)
  const [isApp, goApp] = useState(false)

  const goBackToApp = () => {
    goApp(true)
  }

  return (
    <>
      <div className="card">
        {
          isApp ?
            <Kodos count={count} /> :
            <KodosSettings back={goBackToApp} />
        }
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <button onClick={ () => goApp(!isApp) }>
          Siwtch
        </button>
      </div>
    </>
  )
}

export default App
