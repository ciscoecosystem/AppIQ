import React from 'react'
import './style.css'

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
            <div className="clearfix">
                <a href="index.html" className="header floal">{this.props.applinktext}</a>
                <div className="header floal">{this.props.text}</div>
                <div className="floar">
                    <div className="instancetext">{this.props.instanceName}</div>
                    <button className="button-logout view-button" onClick={this.handleLogoutClick}> Logout </button>
                </div>
            </div>
        )
    }
}

export default Header
