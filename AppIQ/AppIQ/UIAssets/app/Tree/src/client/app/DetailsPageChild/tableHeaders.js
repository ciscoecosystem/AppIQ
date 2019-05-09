    const ROWS_FAULTS = [ {
        "code": "F0956",
        "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
        "severity": "cleared",
        "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
        "created": "2019-01-23T02:05:42.497-07:00"
      },
      {
        "code": "F0956",
        "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
        "severity": "warning",
        "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
        "created": "2019-01-22T23:16:02.555-07:00"
      },
      {
        "code": "F0956",
        "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX0-leaf102]",
        "severity": "cleared",
        "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX0-leaf102 of class vmmDomP",
        "created": "2019-01-17T03:07:42.083-07:00"
      },
      {
        "code": "F0956",
        "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX1-Leaf102]",
        "severity": "cleared",
        "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX1-Leaf102 of class infraDomP",
        "created": "2018-11-16T17:39:07.208-07:00"
      },
      {
        "code": "F0956",
        "affected": "uni/tn-AppDynamics/ap-AppD-AppProfile1/epg-AppD-Ord/rsdomAtt-[uni/vmmp-VMware/dom-ESX1-Leaf102]",
        "severity": "cleared",
        "descr": "Failed to form relation to MO uni/vmmp-VMware/dom-ESX1-Leaf102 of class infraDomP",
        "created": "2018-11-16T16:38:54.692-07:00"
      }];
   
    const TABLE_COLUMNS_FAULTS = [
        {
            Header: 'Severity',
            accessor:'severity'
           
        },
        {
            Header: 'Code',
            accessor: 'code'
        },
        {
            Header: 'Affected Object',
            accessor: 'affected'
        },
        {
            Header: 'Description',
           accessor: 'descr'
        },
        {
            Header: 'Creation Time',
            accessor: 'created'
        }];
        const TABLE_COLUMNS_EVENTS = [
            {
                Header: 'Severity',
                accessor:'severity'
               
            },
            {
                Header: 'Code',
                accessor: 'code'
            },
            {
                Header: 'Cause',
                accessor: 'cause'
            },
            {
                Header: 'Affected Object',
                accessor: 'affected'
            },
            {
                Header: 'Description',
               accessor: 'description'
            },
            {
                Header: 'Creation Time',
                accessor: 'created'
            }];
            const TABLE_COLUMNS_AUDIT_LOG = [
                {
                    Header: 'ID',
                    accessor:'id'
                   
                },
                {
                    Header: 'Affected Object',
                    accessor: 'affected'
                },
                {
                    Header: 'Description',
                   accessor: 'descr'
                },
                {
                    Header: 'Action',
                   accessor: 'action'
                },
                {
                    Header: 'User',
                   accessor: 'user'
                },
                {
                    Header: 'Creation Time',
                    accessor: 'created'
                }];
                
export { ROWS_FAULTS, TABLE_COLUMNS_FAULTS,TABLE_COLUMNS_AUDIT_LOG,TABLE_COLUMNS_EVENTS}
