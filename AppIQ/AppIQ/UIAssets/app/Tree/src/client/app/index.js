import React from 'react';
import { render } from 'react-dom';
import TestComponent from './TestComponent.js';
import Header from './Header.js'

var treedata;

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

window.APIC_DEV_COOKIE = getCookie("app_Cisco_AppIQ_token");
window.APIC_URL_TOKEN = getCookie("app_Cisco_AppIQ_urlToken");

var headerInstanceName;

function getData() {
    var apicHeaders = new Headers();

    var urlToParse = location.search;
    let urlParams = {};
    urlToParse.replace(
        new RegExp("([^?=&]+)(=([^&]*))?", "g"),
        function ($0, $1, $2, $3) {
            urlParams[$1] = $3;
        }
    );
    let result = urlParams;

    let payload = { query: 'query{Run(tn:"' + result['tn'] + '",appId:"' + result['appId'] + '"){response}}' }
    let xhr = new XMLHttpRequest();
    let url = document.location.origin + "/appcenter/Cisco/AppIQ/graphql.json";

    try {
        xhr.open("POST", url, false);

        xhr.setRequestHeader("Content-type", "application/json");
        xhr.setRequestHeader("DevCookie", window.APIC_DEV_COOKIE);
        xhr.setRequestHeader("APIC-challenge", window.APIC_URL_TOKEN);

        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4){
                if(xhr.status == 200) {
                    let json = JSON.parse(xhr.responseText);
                    if('errors' in json) {
                        // Error related to query
                        localStorage.setItem('message', JSON.stringify(json.errors));
                        const message_set = true;
                        window.location.href = "index.html?gqlerror=1";
                    }
                    else {
                        // Response successful
                        const response = JSON.parse(json.data.Run.response);
                        if(response.status_code != "200") {
                            // Problem with backend fetching data
                            const message = {"errors": [{
                                "message": response.message
                            }]}
                            localStorage.setItem('message', JSON.stringify(message.errors));
                            const message_set = true;
                            window.location.href = "index.html?gqlerror=1";
                        }
                        else {
                            // Success
                            var treedata_raw = JSON.parse(json.data.Run.response).payload;
                            headerInstanceName = JSON.parse(json.data.Run.response).instanceName;
                            treedata = JSON.parse(treedata_raw);
                        }
                    }
                }
                else {
                    // Status code of XHR request not 200
                    console.log("Cannot fetch data to fetch Tree data.");
                    if(typeof message_set !== 'undefined') {
                        const message = {"errors": [{"message": "Error while fetching data for Tree. Status code" + xhr.status}]}
                        localStorage.setItem('message', JSON.stringify(message.errors));
                    }
                    window.location.href = "index.html?gqlerror=1";
                }
            }
        }
        xhr.send(JSON.stringify(payload));
    }
    catch(except) {
        console.log("Cannot fetch data to fetch Tree data.")
        if(typeof message_set == 'undefined') {
            const message = {"errors": [{
                "message": "Error while fetching data for Tree"
              }]}
            localStorage.setItem('message', JSON.stringify(message.errors));
        }

        window.location.href = "index.html?gqlerror=1";
    }
}

function getStaticData() {
    var rawData = [
    ];
    treedata = rawData;
}

function loadingBoxShow() {
    document.getElementById("loading-box").style.display="visible";
}

function loadingBoxHide() {
    document.getElementById("loading-box").style.display="none";
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            reloadCount : 0,
        }

        this.reload = this.reload.bind(this);
        let myVar = setInterval(this.reload, 60000);
    }

    reload() {
        // alert("Reloading");
        // loadingBoxShow();
        this.setState({
            reloadCount : this.state.reloadCount + 1,
        })
    }

    render() {
        loadingBoxShow();
        getData();
        loadingBoxHide();
        let apptext = " List of Applications";
        let title = " | View"
        return (
            <div>
                <Header text={title} applinktext={apptext} instanceName={headerInstanceName}/>
                <TestComponent data={treedata} reloadController={this.reload}/>
            </div>
        );
    }
}

render(<App />, document.getElementById('app'));

