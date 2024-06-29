import KodosItem from './KodosItem'

import UserContext from './User'

import { useContext, useEffect, useState } from 'react'


function Kodos(props) {
  const user = useContext(UserContext)

  const [todayTasks, setTodayTasks] = useState([])
  const [importantTasks, setImportantTasks] = useState([])
  const [ddlTasks, setDDLTasks] = useState([])

  function get_tasks(token, isImportant, isToday, isDDL) {
    var queryString = "status+ne+'completed'"
    if (isImportant) {
      queryString += "and+importance+eq+'high'"
    } else if (isDDL || isToday) {
      queryString += "and+dueDateTime+ne+null"
    }

    fetch("https://graph.microsoft.com/beta/me/outlook/tasks?$top=100&$filter=" + queryString, {
      headers: {
        Authorization: "Bearer " + token,
        "Content-Type": "application/json"
      }
    })
    .then(res => res.json())
    .then(
      res => {
        if (isToday) {
          let today = new Date()
          today.setUTCHours(0)
          today.setMinutes(0)
          today.setSeconds(0)
          today.setDate(today.getDate() - 1)
          let tomorrow = new Date(today)
          tomorrow.setDate(tomorrow.getDate() + 1)

          setTodayTasks(res.value.filter(task => {
            const dt = new Date(task.dueDateTime.dateTime)
            return dt >= today && dt < tomorrow
          }))
        }
        if (isDDL) {
          setDDLTasks(res.value)
        } else if (isImportant) {
          setImportantTasks(res.value)
        }
      }
    )
    .catch(err => console.log(err))
  }
  useEffect(() => {
    get_tasks(user.access_token, true, false, false)
    get_tasks(user.access_token, false, true, true)
  }, [user])

  return <>
    <div className="bottom-button">
      <button type="button" className="setting-button" onClick={ () => {
        get_tasks(user.access_token, true, false, false)
        get_tasks(user.access_token, false, true, true)
      } }>
        刷新
      </button>
      <button type="button" className="setting-button" onClick={ () => props.goSetting() }>
        设置
      </button>
    </div>
    <div className="kodos-app">
      <h2>今日</h2>
      <div className="kodos-list">
      {
        todayTasks.length > 0 ? todayTasks.map(function (task, i) {
          return <KodosItem task={task} />;
        }) : <p>暂无</p>
      }
      </div>
      <h2>重要</h2>
      <div className="kodos-list">
      {
        importantTasks.length > 0 ? importantTasks.map(function (task, i) {
          return <KodosItem task={task} />;
        }) : <p>暂无</p>
      }
      </div>
      <h2>死线</h2>
      <div className="kodos-list">
      {
        ddlTasks.length > 0 ? ddlTasks.map(function (task, i) {
          return <KodosItem task={task} showDDL={true} />;
        }) : <p>暂无</p>
      }
      </div>
    </div>
  </>
}

export default Kodos
