import KodosItem from './KodosItem'

function Kodos(props) {
  return <>
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
