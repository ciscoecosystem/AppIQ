import React from 'react'
import './style.css'

class App extends React.Component {
    constructor(props) {
        super(props)
    }

    render() {
        return (
            <div className="toolbar">
                <a onClick={this.props.onReload} className="icon-refresh" style={{ color: "black", cursor: 'pointer' }} aria-hidden="true"></a>
            </div>
        )
    }
}

export default App
