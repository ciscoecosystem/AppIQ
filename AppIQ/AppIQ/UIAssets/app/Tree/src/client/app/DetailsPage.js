import React, {Component} from "react";
import "./DetailsPage.css";
import EventAnalytics from "./DetailsPageChild/EventAnalytics";
import { Icon, Tab, Screen } from "blueprint-react";
import clone from "clone";
export default class DetailePage extends Component {
  constructor(props) {
    super(props);
    this.test = this.test.bind(this);
  
    this.getQueryParams = this.getQueryParams.bind(this);
    this.state = {
      data: this.props.data,
      tabs: [
        {
          label: "Overview",
          key: "Overview",
          content: this.test("Overview")
        },
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
      //RIght now nothing
      //this.setState({queryParams:false})
    } else if (this.state.data.name === "EPG") {
      const AppProf = "ap-" + this.state.data.parent.sub_label;
      const EPG = "epg-" + this.state.data.sub_label;
      query = AppProf + "/" + EPG;
    } else {
      //RIght now nothing
      //this.setState({queryParams:false})
    }
    return query;
  }


  componentWillMount(){
    const queryParams = this.getQueryParams()
    var clonedObj = clone(this.state.tabs)
    clonedObj[2]["content"] = <EventAnalytics queryParams={queryParams} key="analytics"></EventAnalytics>;
    this.setState({tabs:clonedObj});
  }

  test(props) {
    return <div style={{ margin: "11px" }}>{props} Details</div>;
  }

  render() {
    return (
      <div className="page-overlay">
        <div className="panel-header">
          {this.state.data.sub_label}
          <Icon
            type="icon-close"
            className="pull-right toggle"
            onClick={this.props.closeDetailsPage}
          />
        </div>

        <Tab type="secondary-tabs" tabs={this.state.tabs} />
      </div>
    );
  }
}
