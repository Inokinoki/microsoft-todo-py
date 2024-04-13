import './App.css'

function KodosSettings(props) {
  return <>
    <div className="kodos-settings">
      <div className="title-bar">
        <h1>Kindle To Do - Kodos</h1>
      </div>
      <div>
        <h2>账户</h2>
      </div>
      <div>
        <h2>显示设置</h2>
        {
          // TODO: Add event listeners for radios and checkboxes
          props.filters ? props.filters.map(
            (filter) => {
              return <>
                <input type="radio" radioGroup='filter' name="filter" value={filter.name}/>
                <label>{filter.description}</label>
                <br/>
                {
                  filter.availableOptions && props.selectedFilter == filter.name ? filter.availableOptions.map(
                    (option) => {
                      return <>
                        <span>&nbsp;&nbsp;&nbsp;&nbsp;</span>
                        <input type="checkbox" value={option}></input>
                        <label>{option}</label>
                        <br/>
                      </>
                    })
                  : <></>
                }
              </>
            }) : <p>没有可用的过滤条件，将显示全部项</p>
        }
        <hr/>
        <input type="checkbox"/><label>显示完成按钮</label>
        <hr/>
        <label>刷新频率：</label>
        <select>
          <option value="10">10 秒</option>
          <option value="30">30 秒</option>
          <option value="60">1 分钟</option>
          <option value="120">2 分钟</option>
          <option value="300">5 分钟</option>
          <option value="600">10 分钟</option>
          <option value="1800">30 分钟</option>
          <option value="3600">1 小时</option>
        </select>
      </div>
      <br/>
      <div>
        <button className="setting-button" onClick={() => props.back()}>关闭</button>
      </div>
    </div>
  </>
}

export default KodosSettings
