import React from 'react';
import Tree from './Tree.js';
import Legend from './Legend.js'
import './style.css';

import clone from 'clone';
import request from 'request';

var dataList;
var treeNumber = 0
export default class TestComponent extends React.Component {

    constructor(props) {
        super(props);
        this.getInList = this.getInList.bind(this);
        this.newData = clone(props.data)
        dataList = this.newData.map(item=>{
            return [item];
        })
    }

    getInList(item) {
        let list = [];
        list.push(item);
        return list;
    }

    render() {
        return (
            <div>
                <Legend  reloadController={this.props.reloadController}/>
                <div id="treeWrapper">
                    <Tree data={this.props.data} treeNum={treeNumber+1} orientation='vertical' textLayout={{ textAnchor: "middle", y: 0 }} nodeSvgShape={{ shape: 'circle', shapeProps: { r: 20 } }} styles={{ nodes: { node: { circle: { fill: "#DFF" }, attributes: { fill: "#000" } }, leafNode: { circle: { fill: "#DFF" } } } }} translate={{ x: 400, y: 60}}/>
                </div >
                {/* <div className="navigation-panel-bottom">
                    <div className="x-btn x-box-item x-btn-default-small x-noicon x-btn-noicon x-btn-default-small-noicon"
                     id="button-3680" style={{margin : "5px", float : "right", border : "1px solid #ff0000"}} >
                        <em id="button-3680-btnWrap" style={{float : "right", border : "1px solid #00ff00"}}>
                            <button id="button-3680-btnEl" type="button" className="x-btn-center" hidefocus="true"
                            role="button" autocomplete="off" style={{float : "right", border : "1px solid #0000ff"}}>
                                <span id="button-3680-btnInnerEl" className="x-btn-inner" style={{paddingTop : "7px", border : "1px solid #000000"}}>
                                    Cancel
                                </span>
                            </button>
                        </em>
                    </div>
                </div> */}

                {/* <div className="navigation-panel-bottom">
                <button className="tree-back-button"
                        onClick={() => {window.location.href = "index.html";}}>
                    Back
                </button>
                </div> */}

                <div className="health-indicators">
                    <h4 style={{marginTop : "5px"}}>Health Legend</h4>
                    <hr/>
                    <div className="health-indicators-table" width="100%">
                        <table width="90%" style={{margin : "5%"}}>
                            <tr className="health-row">
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Normal </td>
                                <td width="19%">
                                    <div className="health-normal" style={{height : "15px"}}>&nbsp;</div>
                                </td>
                            </tr>
                            <tr className="health-row">
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Warning </td>
                                <td width="19%">
                                    <div className="health-warning_" style={{height : "15px"}}>&nbsp;</div>
                                </td>
                            </tr>
                            <tr className="health-row" style={{border : "0px"}}>
                                <td width="80%" className="legend-title" style={{padding : "1em"}}> Critical </td>
                                <td width="19%">
                                    <div className="health-critical_" style={{height : "15px"}}>&nbsp;</div>
                                </td>
                            </tr>
                        </table>
                    </div>
                </div>
            </div>
        );
    }
}

