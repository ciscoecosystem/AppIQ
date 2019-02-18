Cisco AppIQ (Beta) is a stateful app.

This application pushes ACI Logical topology constructs regarding Tenant, Application profiles, End point groups, Bridge Domain, VRF and contracts to a service now instance.

PREREQUISITE:
THIS APP WILL NOT WORK WITHOUT THE CISCO APPLICATION ON AppDynamics
Mapped AppDynamics Nodes into ACI EPGs (via port groups)

HOWTO:
Once the app is installed, the user will be prompted for
AppDynamics instance url 
AppDynamics instance port
AppDynamics instance username
AppDynamics instance account
AppDynamics instance password


Components:
Frontend in UI Assets.
Backend in Services.
	start.sh starts the flask server for collecting data from the front end
	flask handler in plugin_server.py