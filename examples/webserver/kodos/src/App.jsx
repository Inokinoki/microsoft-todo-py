import { useEffect, useState } from 'react'
import './App.css'

import Kodos from './Kodos'
import KodosSettings from './KodosSettings'

import baseURL from './URL.js'
import UserContext from './User'
import { login, getAuth } from './Utils'

function getParameterByName(name, url = window.location.href) {
  name = name.replace(/[\[\]]/g, '\\$&');
  var regex = new RegExp('[?&]' + name + '(=([^&#]*)|&|#|$)'),
      results = regex.exec(url);
  if (!results) return null;
  if (!results[2]) return '';
  return decodeURIComponent(results[2].replace(/\+/g, ' '));
}

function parseAndSetAuthInfo(setter, authInfo) {
  setter(authInfo)
  login(JSON.stringify(authInfo))
}

function App() {
  const [count, setCount] = useState(0)
  const [isApp, goApp] = useState(true)
  const [authInfo, setAuthInfo] = useState(null)
  const [isLoading, setLoading] = useState(true)
  const [refreshRate, setRefreshRate] = useState(60)

  const goBackToApp = () => {
    goApp(true)
  }
  
  function loadUser(state) {
    fetch(baseURL + '/auth_token?state=' + state).then(res => {
      if (res.status == 200) {
        res.json()
          .then(authInfo => parseAndSetAuthInfo(setAuthInfo, authInfo))
          .catch(error => {
            console.error(error)
          })
      }
    }).catch(error => {
      console.error("Failed to get info " + error)
    })
  }

  useEffect(() => {
    if (!authInfo) {
      setLoading(true)
      // Load from local storage
      try {
        const authInfo = JSON.parse(getAuth())
        if (authInfo) {
          parseAndSetAuthInfo(setAuthInfo, authInfo)
          return
        }
      } catch (error) {
        console.warn("Failed to parse auth info from local storage: " + error)
      }

      const state = getParameterByName("state")
      if (state) {
        loadUser(state)
      }
      setLoading(false)
    }
  })
  
  return (
    <div className="card">
      {
        authInfo ?
        <>
          <UserContext.Provider value={authInfo}>
            {
              isApp ?
                <Kodos refreshRate={refreshRate} count={count} goSetting={() => goApp(!isApp)} /> :
                <KodosSettings setRefreshRate={setRefreshRate} filters={[{name: "date", description: "截止日期", availableOptions: ["true", "false"]}, {name: "like", description: "收藏", availableOptions: ["true", "false"]}]} selectedFilter={"date"} back={goBackToApp} />
            }
          </UserContext.Provider>
        </> :
        <>
          <div>
          {
            isLoading ?
              <p>
              载入账号信息中...
              </p>
              :
              <p>
                您尚未登录 Micrsoft 账号
                请点击这里<a href="/">登录</a>
              </p>
          }
          </div>
        </>
      }
    </div>
  )
}

export default App
