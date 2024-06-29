import KodosItem from './KodosItem'

function Kodos(props) {
  return <>
    <div className="bottom-button">
      <button type="button" className="setting-button" onClick={ () => props.goSetting() }>
        刷新
      </button>
      <button type="button" className="setting-button" onClick={ () => props.goSetting() }>
        设置
      </button>
    </div>
    <div className="kodos-app">
      {
        Array.apply(0, Array(props.count)).map(function (x, i) {
          return <KodosItem />;
        })
      }
    </div>
  </>
}

export default Kodos
