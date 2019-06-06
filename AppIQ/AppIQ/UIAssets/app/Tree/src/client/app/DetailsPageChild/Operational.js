import React from "react";
import { Tab } from "blueprint-react";
import "../DetailsPage.css";

import clone from "clone";
import DataTable from "./DataTable.js";

export default class Operational extends React.Component {
    constructor(props) {
        super(props)
        this.state = {
            query: this.props.query,
            tabs: [
                {
                    label: "Client End-points",
                    key: "cep",
                    content: <div>No Component</div>, //add your component here
                    gqlCall: "GetOperationalInfo",
                    list: "{operationalList}"

                },
                {
                    label: "Configured Access Policies",
                    key: "cap",
                    content: <div>NO Component</div>, //add your component here
                    gqlCall: "GetEvents",
                    list: "{eventsList}"
                },
                {
                    label: "Contracts",
                    key: "contracts",
                    content: <div>No Component</div>, //add your component here
                    gqlCall: "GetAuditLogs",
                    list: "{auditLogsList}"
                },
                {
                    label: "Controller End-Points",
                    key: "cep",
                    content: <div>No Component</div>, //add your component here
                    gqlCall: "GetAuditLogs",
                    list: "{auditLogsList}"

                }
            ],
            nestedTabs: [
                {
                    label: "To EPG Traffic",
                    key: "tep",
                    content: <div>No nested Component</div>, //add your component here
                    gqlCall: "GetAuditLogs",
                    list: "{auditLogsList}"

                },
                {
                    label: "Subnets",
                    key: "subnets",
                    content: <div>No nested Component</div>, //add your component here
                    gqlCall: "GetAuditLogs",
                    list: "{auditLogsList}"

                }
            ]
        }
    }
    componentDidMount() {
        let temp = clone(this.state.tabs)
        let query = {
            param: this.state.query,
            type: temp[0]['gqlCall'],
            list: temp[0]['list']
        }
        temp[0]['content'] = <DataTable key="cep" query={query} index="3"></DataTable>
        temp[2]['content'] = <Tab tabs={this.state.nestedTabs}></Tab>
        this.setState({ tabs: temp })
    }
    render() {
        return (
            <Tab type="secondary-tabs" tabs={this.state.tabs} />)
    }
}