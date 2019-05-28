__author__ = 'nilayshah'
import graphene
# from graphene import relay
# from graphene_sqlalchemy import SQLAlchemyConnectionField, SQLAlchemyObjectType
# import sqlite3
import plugin_server as app

class Check(graphene.ObjectType):
    checkpoint = graphene.String()


class LoginApp(graphene.ObjectType):
    loginStatus = graphene.String()
    # loginMessage = graphene.String()


class Application(graphene.ObjectType):
    apps = graphene.String()


class Mapping(graphene.ObjectType):
    mappings = graphene.String()


class SaveMapping(graphene.ObjectType):
    savemapping = graphene.String()


class GetFaults(graphene.ObjectType):
    faultsList = graphene.String()

class GetEvents(graphene.ObjectType):
    eventsList = graphene.String()

class GetAuditLogs(graphene.ObjectType):
    auditLogsList = graphene.String()

class SetPollingInterval(graphene.ObjectType):
    status = graphene.String()
    message = graphene.String()


class Run(graphene.ObjectType):
    response = graphene.String()


# class EnableView(graphene.ObjectType):
#     view = graphene.String()

class Details(graphene.ObjectType):
    details = graphene.String()


class Query(graphene.ObjectType):
    Check = graphene.Field(Check)
    LoginApp = graphene.Field(LoginApp, ip=graphene.String(), port=graphene.String(), username=graphene.String(),
                              account=graphene.String(),
                              password=graphene.String())
    Application = graphene.Field(Application, tn=graphene.String())
    Mapping = graphene.Field(Mapping, tn=graphene.String(), appId=graphene.String())
    SaveMapping = graphene.Field(SaveMapping, appId=graphene.String(),tn=graphene.String(),
                                 data=graphene.String())  # data can be a list or string.. Check!
    Run = graphene.Field(Run, tn=graphene.String(), appId=graphene.String())

    GetFaults = graphene.Field(GetFaults, dn=graphene.String())
    GetEvents = graphene.Field(GetEvents, dn=graphene.String())
    GetAuditLogs = graphene.Field(GetAuditLogs, dn=graphene.String())
    SetPollingInterval = graphene.Field(SetPollingInterval, interval = graphene.String())

    # EnableView = graphene.Field(EnableView,view=graphene.String())
    Details = graphene.Field(Details, tn=graphene.String(), appId=graphene.String())

    def resolve_GetFaults(self, info, dn):
        GetFaults.faultsList = app.getFaults(dn)
        return GetFaults

    def resolve_GetEvents(self, info, dn):
        GetEvents.eventsList = app.getEvents(dn)
        return GetEvents

    def resolve_GetAuditLogs(self, info, dn):
        GetAuditLogs.auditLogsList = app.getAuditLogs(dn)
        return GetAuditLogs

    def resolve_SetPollingInterval(self, info, interval):
        status, message = app.setPollingInterval(interval)
        SetPollingInterval.status = status
        SetPollingInterval.message = message
        return SetPollingInterval

    
    def resolve_Check(self,info): #On APIC
    #def resolve_Check(self, args, context, info):  # On local desktop
        Check.checkpoint = app.checkFile()
        return Check

    def resolve_LoginApp(self, info, ip, port, username, account, password):  # On APIC
        app_creds = {"appd_ip": ip, "appd_port": port, "appd_user": username, "appd_account": account,
                     "appd_pw": password}
        # def resolve_LoginApp(self, args, context, info): # On local desktop
        #    app_creds = {"appd_ip": args.get('ip'),"appd_port": args.get('port'), "appd_user": args.get('username'), "appd_account": args.get('account'),
        #                "appd_pw": args.get('password')}
        loginResp = app.login(app_creds)
        # print loginResp
        LoginApp.loginStatus = loginResp
        # LoginApp.loginMessage = loginResp['message']

        return LoginApp

    def resolve_Application(self, info, tn):  # On APIC
        # def resolve_Application(self,args,context,info): # On local desktop
        Application.apps = app.apps(tn)
        return Application

    def resolve_Mapping(self, info, tn, appId):  # args, context, info): # On APIC
        # def resolve_Mapping(self, args, context, info): # On local desktop
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Mapping.mappings = app.mapping(tn, int(appId))  # Add params to plugin_server for this method
        return Mapping

    def resolve_SaveMapping(self, info, appId, tn, data):  # On APIC
        # def resolve_SaveMapping(self,args,context,info): # On local desktop (Uncomment appId and data args)
        #    appId = int(args.get('appId'))
        #    mappedData = args.get('data')
        mappedData = data
        #print info
        SaveMapping.savemapping = app.saveMapping(int(appId), str(tn), mappedData)
        return SaveMapping

    def resolve_Run(self, info, tn, appId):  # On APIC
        # def resolve_Run(self,args,context,info): # On local desktop (Uncomment appId and tn args)
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Run.response = app.tree(tn, int(appId))
        return Run

    def resolve_Details(self, info, tn, appId):  # On APIC
        # def resolve_Details(self,args,context,info):# On local desktop (Uncomment appId and tn args)
        #    tn = args.get('tn')
        #    appId = int(args.get('appId'))
        Details.details = app.get_details(tn, int(appId))
        return Details

        # def resolve_EnableView(self, args, context, info):
        #
        #     return EnableView


schema = graphene.Schema(query=Query)





# query{
#   Mapping(tn:"AppDControllerTenant", appId:"7"){
#     mappings
#   }
# }

# query{
#   Application {
#     apps
#   }
# }

# query{
#   SaveMapping(appId:"7"
#     ,data:"[{'domains':[{'domainName':'uni/tn-AppDControllerTenant/ap-AppDController-AP1/epg-AppDControllerEPG1'}],'ipaddress': '192.168.128.16'}]")
#   {
#     savemapping
#   }
# }

# query{
#   Details(tn:"AppDControllerTenant",appId:"7"){
#     details
#   }
# }

# query{
#   Run(tn:"AppDControllerTenant",appId:"7"){
#     response
#   }
# }

# query{
#   Details(tn:"AppDControllerTenant",appId:"7"){
#     details
#   }
# }




# ====== DMZ =======
# query{
#   Check{
#     checkpoint
#   }
# }

# query{
#   LoginApp(ip:"192.168.132.125",username:"user1",account:"customer1",password:"Cisco!123"){
#     loginStatus
#     loginMessage
#   }
# }

# query{
#   Application {
#     apps
#   }
# }

# query{
#   Mapping(tn:"AppDynamics", appId:"5"){
#     mappings
#   }

# query{
#   SaveMapping(appId:"5"
#     ,data:"[{'domains':[{'domainName':'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ecomm'}],'ipaddress': '10.10.10.15'},{'domains':[{'domainName':'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Pay'}],'ipaddress': '10.10.10.21'}]")
#   {
#     savemapping
#   }
# }

# query{
#   Details(tn:"AppDynamics",appId:"5"){
#     details
#   }
# }

# query{
#   Run(tn:"AppDynamics",appId:"5"){
#     response
#   }
# }
#
