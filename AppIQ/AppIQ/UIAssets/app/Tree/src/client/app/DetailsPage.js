import React, { Component } from "react";
import "./DetailsPage.css";
import EventAnalytics from "./DetailsPageChild/EventAnalytics";
import { Icon, Tab, Screen } from "blueprint-react";
import clone from "clone";
import DataTable from "./DetailsPageChild/DataTable.js";
import Operational from "./DetailsPageChild/Operational";

export default class DetailePage extends Component {
  constructor(props) {
    super(props);
    this.test = this.test.bind(this);
	this.getIPList = this.getIPList.bind(this);
    this.getQueryParams = this.getQueryParams.bind(this);
    this.state = {
      data: this.props.data,
      tabs: [

        {
          label: "Operational",
          key: "Operational",
          content: this.test("Operational")
        },
        {
          label: "Event Analytics",
          key: "EventAnalytics",
          content: this.test("event")
        }
      ]
    };
  }
  getQueryParams() {
    var query = false;
    console.log("with data");
    console.log(this.state.data);
    if (this.state.data.name === "AppProf") {
      query = "ap-" + this.state.data.sub_label
    } else if (this.state.data.name === "EPG") {
      const AppProf = "ap-" + this.state.data.parent.sub_label;
      const EPG = "epg-" + this.state.data.sub_label;
      query = AppProf + "/" + EPG;
    } else if (this.state.data.name === "EP") {
	
	  const AppProf = "ap-" + this.state.data.parent.parent.sub_label;
      const EPG = "epg-" + this.state.data.parent.sub_label;
	  query = AppProf + "/" + EPG
      //Pass
    }
    return query;
  }
  getIPList(){
	if(this.state.data.type === "grey"){
	return Object.values(this.state.data.attributes) || ""
	}
	else {
	return this.state.data.attributes.IP || ""
	}
	}

  componentWillMount() {
    const queryParams = this.getQueryParams()
    var clonedObj = clone(this.state.tabs)
    if (this.state.data.name == "AppProf" || this.state.data.name == "EPG") {
      clonedObj[1]["content"] = <EventAnalytics queryParams={queryParams} key="analytics"></EventAnalytics>;

    }
    if (this.state.data.name == "AppProf") {
      clonedObj.splice(0, 1);
      console.log(clonedObj);
    }
if (this.state.data.name == "EPG") {
      let moType = this.state.data.name.toLowerCase();
      let ipList = "";
      let param = queryParams + '",moType:"' + moType + '",ipList:"' + ipList

      clonedObj[0]["content"] = <Operational query={param}></Operational>
    }
    if (this.state.data.name == "EP") {
      clonedObj.splice(1, 1);
	  let moType = this.state.data.name.toLowerCase();
		let ipList = this.getIPList();
		
		let param = queryParams + '",moType:"' + moType + '",ipList:"' + ipList
		let query = {
		param, type : "GetOperationalInfo",
		list : "{operationalList}"
		}			
		clonedObj[0]["content"] = <DataTable key = "operational" query={query} index="3"/>
    }
    this.setState({ tabs: clonedObj });
  }

  test(props) {
    return <div style={{ margin: "11px" }}>{props} Details</div>;
  }

  render() {
    return (
      <Screen hideFooter={true} title={this.state.data.sub_label || this.state.data.label || "EndPoint Information"} allowMinimize={false} onClose={this.props.closeDetailsPage}>

        {/* // <div className="page-overlay">
      //   <div className="panel-header">
      //     {this.state.data.sub_label || this.state.data.label}
      //     <Icon
      //       type="icon-close"
      //       className="pull-right toggle"
      //       onClick={this.props.closeDetailsPage}
      //     />
      //   </div> */}

        <Tab type="secondary-tabs" tabs={this.state.tabs} />
      </Screen>
    );
  }
}
