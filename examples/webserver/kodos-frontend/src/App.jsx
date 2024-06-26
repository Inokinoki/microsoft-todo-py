import { useState } from 'react'
import './App.css'

import Kodos from './Kodos'
import KodosSettings from './KodosSettings'

import baseURL from './URL.js'
import UserContext from './User'
import { login } from './Utils'

function getParameterByName(name, url = window.location.href) {
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function loadUser(state) {
  console.log(state)
  fetch(baseURL + '/auth_token?state=' + state,
    {
      mode: 'no-cors',
      method: 'GET'
    }
  ).then(res => {
    console.log("Test")
    console.log(res)
    res.json()
      .then(authInfo => setAuthInfo(authInfo))
      .catch(error => {console.error(error)})
  }).catch(error => {
    console.error("Failed to get info " + error)
  })
}

setTimeout(() => loadUser(getParameterByName("state")), 1000)

function App() {
  const [count, setCount] = useState(0)
  const [isApp, goApp] = useState(false)
  const [authInfo, setAuthInfo] = useState()

  const goBackToApp = () => {
    goApp(true)
  }

  
  return (
    <>
      <div className="card">
        {
          authInfo ?
          <>
            <UserContext.Provider value={authInfo.id_token_claims}>
              {
                isApp ?
                  <Kodos count={count} /> :
                  <KodosSettings filters={[{name: "date", description: "截止日期", availableOptions: ["true", "false"]}, {name: "like", description: "收藏", availableOptions: ["true", "false"]}]} selectedFilter={"date"} back={goBackToApp} />
              }
            </UserContext.Provider>
            <button onClick={() => setCount((count) => count + 1)}>
              count is {count}
            </button>
            <button onClick={ () => goApp(!isApp) }>
              Siwtch
            </button>
          </> :
          <>
            载入账号信息中...
          </>
        }
      </div>
    </>
  )
}

export default App
