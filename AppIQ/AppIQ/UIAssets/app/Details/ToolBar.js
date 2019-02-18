import React from 'react'
import './style.css'

class ToolBar extends React.Component {
    constructor(props) {
       super(props) 
       console.log("ToolBar : " + props.onReload);
    }
    
    render() {
        return (
            <div className="toolbar">
                <a onClick={this.props.onReload} className="icon-refresh" style={{color : "black", cursor : 'pointer'}} aria-hidden="true"></a>
            </div>
        )
    }
}

export default ToolBar