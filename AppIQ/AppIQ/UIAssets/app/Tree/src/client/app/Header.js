import React from 'react'
import './hstyle.css'
import {Button} from "blueprint-react"
class Header extends React.Component {
    constructor(props) {
        super(props)
        this.handleLogoutClick = this.handleLogoutClick.bind(this);
    }

    handleLogoutClick() {
     
    window.location.href = "login.html?reset=1";
    }

    render() {
        return (
            <div className="clearfix-new">
                <a href="index.html" className="header-new floal">{this.props.applinktext}</a>
                <div className="header-new floal">{this.props.text}</div>
                <div className="floar">
                    <div className="instancetext">{this.props.instanceName}</div>
                    <Button  onClick={this.handleLogoutClick} type="btn--primary" size="btn--small">Logout</Button>
                  
                </div>
            </div>
        )
    }
}

export default Header
