
function KodosItem(props) {
  if (props.task.dueDateTime && props.showDDL) {
    return <>
      <div className="kodos-item">
        <p>
          <span>{ props.task.subject }</span>
          <br/>
          <span className="kodos-item-ddl">{ new Date(props.task.dueDateTime.dateTime).toLocaleString() }</span>
        </p>
      </div>
    </>
  }
  return <>
    <div className="kodos-item">
      <p>{ props.task.subject }</p>
    </div>
  </>
}

export default KodosItem
