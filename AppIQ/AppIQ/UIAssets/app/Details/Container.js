import React from 'react'
import Header from '../Header'
import DetailsTable from './DetailsTable'
import './style.css'

function getCookieVal(offset) {
    var endstr = document.cookie.indexOf(";", offset);
    if (endstr == -1) {
        endstr = document.cookie.length;
    }
    return unescape(document.cookie.substring(offset, endstr));
}

function getCookie(name) {
    var arg = name + "=";
    var alen = arg.length;
    var clen = document.cookie.length;
    var i = 0;
    var j = 0;
    while (i < clen) {
        j = i + alen;
        if (document.cookie.substring(i, j) == arg) {
            return getCookieVal(j);
        }
        i = document.cookie.indexOf(" ", i) + 1;
        if (i === 0) {
            break;
        }
    }
    return null;
}

var params_appid;
var params_tn;
var details_raw;

var urlToParse = location.search;
var urlParams = {};
urlToParse.replace(
    new RegExp("([^?=&]+)(=([^&]*))?", "g"),
    function ($0, $1, $2, $3) {
        urlParams[$1] = $3;
    }
);
var result = urlParams;

var headerInstanceName;

class Container extends React.Component {
    constructor(props) {
        super(props);

        this.getData = this.getData.bind(this);
        this.reload = this.reload.bind(this);

        params_appid = result['appId'];
        params_tn = result['tn'];

        this.getData();

        this.state = {
            "data": JSON.parse(details_raw).payload
        };

        this.handleBackClick = this.handleBackClick.bind(this);

        let reloader = setInterval(this.reload, 30000);
    }


    getData() {
        /**
        * Use this.httpGet to get data from REST API
        */
        let payload = {
            query: 'query{Details(tn:"' + result['tn'] + '",appId:"' + result['appId'] + '"){details}}'
        }

        details_raw = "[]";
        try {
            let main_data_raw = this.httpGet(document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json", payload);
            let rawJsonData = JSON.parse(JSON.parse(main_data_raw).data.Details.details)
            let main_data_json = JSON.parse(main_data_raw);

            if ('errors' in main_data_json) {
                // Error related to query
                localStorage.setItem('message', JSON.stringify(main_data_json.errors));
                const message_set = true;
                window.location.href = "index.html?gqlerror=1";
            }
            else {
                if (rawJsonData.status_code != "200") {
                    // Problem with backend fetching data
                    const message = {
                        "errors": [{
                            "message": rawJsonData.message
                        }]
                    }
                    localStorage.setItem('message', JSON.stringify(message.errors));
                    const message_set = true;
                    window.location.href = "index.html?gqlerror=1";
                }
                else {
                    // Success
                    headerInstanceName = rawJsonData.instanceName;
                    details_raw = JSON.parse(main_data_raw).data.Details.details;
                }
            }
        }
        catch (e) {
            // Problem fetching data
            if (typeof message_set == 'undefined') {
                const message = {
                    "errors": [{
                        "message": "Error while fetching data for details."
                    }]
                }
                localStorage.setItem('message', JSON.stringify(message.errors));
            }
            window.location.href = "index.html?gqlerror=1";
        }
    }


    /**
    * @param {string} theUrl The URL of the REST API
    *
    * @return {string} The response received from portal
    */
    httpGet(theUrl, payload) {
        window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
        window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");
        var xmlHttp = new XMLHttpRequest();

        xmlHttp.open("POST", theUrl, false); // false for synchronous request
        xmlHttp.setRequestHeader("Content-type", "application/json");
        xmlHttp.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        xmlHttp.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);
        xmlHttp.send(JSON.stringify(payload));
        return xmlHttp.responseText;
    }

    handleBackClick() {
        window.location.href = "app.html";
    }

    reload() {
        this.getData();

        this.setState({
            "data": JSON.parse(details_raw).payload
        });
    }

    render() {
        console.log("Container : " + this.reload);
        let title = " | Details";
        let apptext = " List of Applications";
        return (
            <div>
                <Header text={title} applinktext={apptext} instanceName={headerInstanceName}/>
            <div className="container">
                <DetailsTable data={this.state.data} appId={params_appid} tn={params_tn} onReload={this.reload} />
                {/* <button className="button view-button" onClick={this.handleBackClick}> Back </button> */}
            </div>
            </div>
        )
    }
}

export default Container
