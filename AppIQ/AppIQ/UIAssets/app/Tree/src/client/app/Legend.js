import React from 'react';
import uuid from 'uuid';
import { layout, select, behavior, event } from 'd3';

import LegendNode from './LegendNode.js';
import Tree from './Tree.js';

import './style.css';


var legend = [{
    "name": "AppProf",
    "level": "#27AAE1",
    "label": "Application Profile",
    "type": "#27AAE1",
    "trans": 0
}, {
    "name": "EPG",
    "level": "#025e91",
    "label": "End Point Group",
    "type": "#025e91",
    "trans": 2
}, {
    "name": "EP",
    "level": "#2DBBAD",
    "label": "End Point",
    "type": "#2DBBAD",
    "trans": 4
}, {
    "name": "Node",
    "level": "#C5D054",
    "label": "Node",
    "type": "#C5D054",
    "trans": 6
}]


var zoomButton = {
    "name": "Zoom",
    "level": "#2dbbac",
    "label": "Zoom",
    "type": "#2dbbac",
    "trans": 10
}

function zoomIn() {
    window.treeComponent.zoomInTree();
}

function zoomOut() {
    window.treeComponent.zoomOutTree();
}

export default class Legend extends React.Component {
    render() {

        return (
            <div>
                <svg width="100%" height="70px" style={{ backgroundColor: "rgb(224,224,226)" }}>
                    {legend.map(legend => (
                        <LegendNode
                            key={uuid.v4()}
                            nodeSvgShape={{ shape: 'circle', shapeProps: { r: 15 } }}
                            orientation='vertical'
                            transitionDuration={500}
                            nodeData={legend}
                            name={legend.name}
                            translate={{ x: 60 + legend.trans * 50, y: 25 }}
                            textLayout={{ textAnchor: "middle", y: 0 }}
                            styles={{ leafNode: { circle: { fill: "#DFF" } } }}
                        />
                    ))}

                <symbol id="icon-zoom-in" viewBox="0 0 5 5">
                <title>cog</title>
                <path d="M14.59 9.535c-0.839-1.454-0.335-3.317 1.127-4.164l-1.572-2.723c-0.449 0.263-0.972 0.414-1.529 0.414-1.68 0-3.042-1.371-3.042-3.062h-3.145c0.004 0.522-0.126 1.051-0.406 1.535-0.839 1.454-2.706 1.948-4.17 1.106l-1.572 2.723c0.453 0.257 0.845 0.634 1.123 1.117 0.838 1.452 0.336 3.311-1.12 4.16l1.572 2.723c0.448-0.261 0.967-0.41 1.522-0.41 1.675 0 3.033 1.362 3.042 3.046h3.145c-0.001-0.517 0.129-1.040 0.406-1.519 0.838-1.452 2.7-1.947 4.163-1.11l1.572-2.723c-0.45-0.257-0.839-0.633-1.116-1.113zM8 11.24c-1.789 0-3.24-1.45-3.24-3.24s1.45-3.24 3.24-3.24c1.789 0 3.24 1.45 3.24 3.24s-1.45 3.24-3.24 3.24z"></path>
                </symbol>

                </svg>

                <div className="legend-icon zoom-in-icon icon-search-plus" onClick={zoomIn}>
                    {/* &nbsp;<i className="icon-text icon-search-plus"></i> */}
                </div>

                <div className="legend-icon zoom-out-icon icon-search-minus" onClick={zoomOut}>
                    {/* &nbsp;<i className="icon-text icon-search-minus"></i> */}
                </div>

                <div className="legend-icon reload-icon icon-repeat" onClick={this.props.reloadController}>
                    {/* &nbsp;<i className="icon-text icon-repeat"></i> */}
                </div>

            </div>
        );


        /*
        return (
            <div>
                <div class="i-graph-button  i-ap-fvContractColorImg" data-qtip="Contract">
                <div class="graph-button-text">Contract</div>
                </div>
            </div>
        )
        */

    }
}

