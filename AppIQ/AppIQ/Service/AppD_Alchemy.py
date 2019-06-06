import pprint
from flask import current_app

__author__ = 'nilayshah'

from sqlalchemy import Column, Integer, String, ForeignKey, PickleType, update, Boolean, func, DateTime
from sqlalchemy import create_engine

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, mapper, relation, sessionmaker, relationship
from sqlalchemy.ext import mutable
from sqlalchemy import exists
import sqlalchemy.types as types
import datetime
import time, json

# app.debug = True
Base = declarative_base()


class Application(Base):
    __tablename__ = 'Application'
    appId = Column(Integer, primary_key=True)
    appName = Column(String)
    appMetrics = Column(PickleType)  # https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy
    timestamp = Column(DateTime)
    isViewEnabled = Column(Boolean, nullable=False)

    def __init__(self, appId, appName, appMetrics, timestamp, isViewEnabled=None):
        self.appId = appId
        self.appName = appName
        self.appMetrics = appMetrics
        self.timestamp = timestamp
        if isViewEnabled != None:
            self.isViewEnabled = isViewEnabled
        else:
            self.isViewEnabled = True


class Tiers(Base):
    __tablename__ = 'Tiers'
    tierId = Column(Integer, primary_key=True)
    tierName = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))
    tierHealth = Column(String)
    sepchild = relationship('ServiceEndpoints', primaryjoin='Tiers.tierId==ServiceEndpoints.tierId', backref='Tiers')
    hevchild = relationship('HealthViolations', primaryjoin='Tiers.tierId==HealthViolations.tierId', backref='Tiers')

    def __init__(self, tierId, tierName, appId, tierHealth):
        self.tierId = tierId
        self.tierName = tierName
        self.appId = appId
        self.tierHealth = tierHealth


class ServiceEndpoints(Base):
    __tablename__ = 'ServiceEndpoints'
    sepId = Column(Integer, primary_key=True)
    sep = Column(PickleType)  # List of serialized json #https://stackoverflow.com/questions/1378325/python-dicts-in-sqlalchemy
    timestamp = Column(DateTime)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    appId = Column(Integer, ForeignKey('Application.appId'))

    def __init__(self, sepId, sep, tierId, appId, timestamp):
        self.sepId = sepId
        self.sep = sep
        self.tierId = tierId
        self.appId = appId
        self.timestamp = timestamp


class HealthViolations(Base):
    __tablename__ = 'HealthViolations'
    violationId = Column(Integer, primary_key=True)
    startTime = Column(String)
    businessTransaction = Column(String)
    description = Column(String)
    severity = Column(String)
    timestamp = Column(DateTime)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    appId = Column(Integer, ForeignKey('Application.appId'))
    # violationId, startTime, businessTransaction,description,severity,tierId,appId
    def __init__(self, violationId, startTime, businessTransaction, description, severity, tierId, appId, timestamp):
        self.violationId = violationId
        self.startTime = startTime
        self.businessTransaction = businessTransaction
        self.description = description
        self.severity = severity
        self.tierId = tierId
        self.appId = appId
        self.timestamp = timestamp


class Nodes(Base):
    __tablename__ = 'Nodes'
    nodeId = Column(Integer, primary_key=True)
    nodeName = Column(String)
    tierId = Column(Integer, ForeignKey('Tiers.tierId'))
    nodeHealth = Column(String)
    ipAddress = Column(PickleType)
    timestamp = Column(DateTime)
    appId = Column(Integer, ForeignKey('Application.appId'))

    def __init__(self, nodeId, nodeName, tierId, nodeHealth, ipList, appId, timestamp):
        self.nodeId = nodeId
        self.nodeName = nodeName
        self.tierId = tierId
        self.nodeHealth = nodeHealth
        self.ipAddress = ipList
        self.appId = appId
        self.timestamp = timestamp


class EpgHistory(Base):
    __tablename__ = 'EpgHistory'
    epgDn = Column(String, primary_key=True)
    epgFaultRecords = Column(PickleType)
    epgHealthRecords = Column(PickleType)
    epgEventRecords = Column(PickleType)
    epgLogRecords = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, epgDn, epgFaultRecords, epgHealthRecords, epgEventRecords, epgLogRecords, timestamp):
        self.epgDn = epgDn
        self.epgFaultRecords = epgFaultRecords
        self.epgHealthRecords = epgHealthRecords
        self.epgEventRecords = epgEventRecords
        self.epgLogRecords = epgLogRecords
        self.timestamp = timestamp

class EpgSummary(Base):
    __tablename__ = 'EpgSummary'
    epgDn = Column(String, primary_key=True)
    epgDomains = Column(PickleType)
    epgSubnets = Column(PickleType)
    epgStaticEps = Column(PickleType)
    epgStaticLeaves = Column(PickleType)
    epgFcPaths = Column(PickleType)
    epgStaticPorts = Column(PickleType)
    epgIfConns = Column(PickleType)
    epgContracts = Column(PickleType)
    epgLabels = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, epgDn, epgDomains, epgSubnets, epgStaticEps, epgStaticLeaves, epgFcPaths, epgStaticPorts, epgIfConns, epgContracts, epgLabels, timestamp):
        self.epgDn = epgDn
        self.epgDomains = epgDomains
        self.epgSubnets = epgSubnets
        self.epgStaticEps = epgStaticEps
        self.epgStaticLeaves = epgStaticLeaves
        self.epgFcPaths = epgFcPaths
        self.epgStaticPorts = epgStaticPorts
        self.epgIfConns = epgIfConns
        self.epgContracts = epgContracts
        self.epgLabels = epgLabels
        self.timestamp = timestamp

class ApHistory(Base):
    __tablename__ = 'ApHistory'
    apDn = Column(String, primary_key=True)
    apFaultRecords = Column(PickleType)
    apHealthRecords = Column(PickleType)
    apEventRecords = Column(PickleType)
    apLogRecords = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, apDn, apFaultRecords, apHealthRecords, apEventRecords, apLogRecords, timestamp):
        self.apDn = apDn
        self.apFaultRecords = apFaultRecords
        self.apHealthRecords = apHealthRecords
        self.apEventRecords = apEventRecords
        self.apLogRecords = apLogRecords
        self.timestamp = timestamp

class ApSummary(Base):
    __tablename__ = 'ApSummary'
    apDn = Column(String, primary_key=True)
    apEpgs = Column(PickleType)
    apUsegEpgs = Column(PickleType)
    timestamp = Column(DateTime)

    def __init__(self, apDn, apEpgs, apUsegEpgs, timestamp):
        self.apDn = apDn
        self.apEpgs = apEpgs
        self.apUsegEpgs = apUsegEpgs
        self.timestamp = timestamp

class ACItemp(Base):
    # ACI temp gets all EPs in APIC for all tenants, UI will request based on tenant and get EPs for that tenant
    __tablename__ = 'ACItemp'
    dn = Column(String, primary_key=True)
    IP = Column(String)
    tenant = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))
    selector = Column(Integer, default=0)  # 0 or 1 (1 on user input selected, 0 on deselect)

    def __init__(self, dn, IP, tenant, appId=None, selector=0):
        self.dn = dn
        self.IP = IP
        self.tenant = tenant
        self.appId = appId  # Not required
        self.selector = selector


class ACIperm(Base):
    # ACI perm has user selected EPs for a given tenant and will show all selected EPs upon request for that tenant
    __tablename__ = 'ACIperm'
    IP = Column(String)
    dn = Column(String, primary_key=True)
    tenant = Column(String)
    appId = Column(Integer, ForeignKey('Application.appId'))

    def __init__(self, IP, dn, tenant, appId):
        self.IP = IP
        self.dn = dn
        self.tenant = tenant
        self.appId = appId


class Mapping(Base):
    # Map table will store mappings for each app. The appId is the primary key and the mapped data is a list of dicts
    __tablename__ = 'Mapping'
    appId = Column(String, primary_key=True)
    mapped_data = Column(PickleType)

    def __init__(self, appId, mapped_data):
        self.appId = appId
        self.mapped_data = mapped_data


class Database():
    def __init__(self):
        self.engine = create_engine("sqlite:///AppD_Test.db?check_same_thread=False")

        # get a handle on the table object
        # self.Application_table = Application.__table__
        # get a handle on the metadata
        self.metadata = Base.metadata
        Session = sessionmaker(bind=self.engine)
        self.conn = self.engine.connect()
        try:
            self.conn.execute("PRAGMA journal_mode = WAL")
        except Exception as ex:
            current_app.logger.info("Exception setting journal mode to WAL : " + str(ex))
        
        self.session = Session(bind=self.conn)

    def createTables(self):  # Add Exception
        try:
            self.metadata.create_all(self.engine)
            return None
        except Exception as e:
            current_app.logger.info('Exception in creating tables: ' + str(e))
            # Log: internal backend error: could not create tables
            return None

    def flushSession(self):
        try:
            current_app.logger.info('Session Flushed!')
            self.session.flush()
        except Exception as e:
            current_app.logger.info('Could not flush the session!')

    def commitSession(self):
        try:
            self.session.commit()
        #             current_app.logger.info('Session Commited!')
        # Log: internal backend error: could not create tables
        #             return "Session Committed"
        except Exception as e:
            current_app.logger.info('Exception in Committing session: ' + str(e))
            self.flushSession()

    def insertInto(self, table, data):
        try:
            if table == 'Mapping':
                #  appId, mapped_data [{dn, ipAddress}]
                self.session.add(Mapping(data[0], data[1]))

            if table == 'Application':
                # appId, appName, appMetrics
                self.session.add(Application(data[0], str(data[1]), data[2], data[3]))
                # return self.session.query(Application).filter(Application.appId == data[0])

            if table == 'Tiers':
                # tierId, tierName, appId, tierHealth
                self.session.add(Tiers(data[0], str(data[1]), data[2], data[3]))
                # self.session.add(Tiers(data[0], data[1], data[2], data[3]))

            if table == 'Nodes':
                # nodeId, nodeName, tierId,nodeHealth, ipAddress, appId
                self.session.add(Nodes(data[0], data[1], data[2], data[3], data[4], data[5], data[6]))

            if table == 'ServiceEndpoints':
                # sepId, sep, tierId, appId
                self.session.add(ServiceEndpoints(data[0], data[1], data[2], data[3], data[4]))

            if table == 'HealthViolations':
                # violationId, startTime, businessTransaction,description,severity,tierId,appId
                self.session.add(HealthViolations(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7]))

            if table == 'ACItemp':
                # IP, dn, appId, selector (0 or 1)
                self.session.add(ACItemp(data[0], data[1], data[2]))

            if table == 'ACIPerm':
                # IP, dn, appId
                self.session.add(ACIperm(data[0], data[1], data[2], data[3]))
                # self.commitSession()
                # current_app.logger.info('Values populated into Table '+str(table))
        except Exception as e:
            current_app.logger.info('Exception in Insert: ' + str(e))
            self.commitSession()
            # return json.dumps({"payload": {}, "status_code": "300", "message": "Internal backend error: could not insert into database. Error: "+str(e)})

    def update(self, table, data):
        try:
            if table == 'Mapping':
                self.session.query(Mapping).filter(Mapping.appId == data[0]).update({'mapped_data': data[1]})

            if table == 'Application':
                # appId, appName, appMetrics
                self.session.query(Application).filter(Application.appId == data[0]).update(
                    {'appName': str(data[1]), 'appMetrics': data[2], 'timestamp': data[3]})
                # return self.session.query(Application).filter(Application.appId == data[0])

            if table == 'Tiers':
                # tierId, tierName, appId, tierHealth
                self.session.query(Tiers).filter(Tiers.tierId == data[0]).update(
                    {'tierName': data[1], 'appId': data[2], 'tierHealth': data[3]})

            if table == 'Nodes':
                # nodeId, nodeName, tierId, nodeHealth, ipAddress
                self.session.query(Nodes).filter(Nodes.nodeId == data[0]).update({'nodeName': data[1], 'tierId': data[2], 'nodeHealth': data[3], 'ipAddress': data[4], 'appId': data[5], 'timestamp': data[6]})

            if table == 'ServiceEndpoints':
                # sepId, sep, tierId
                self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == data[0]).update(
                    {'sep': data[1], 'tierId': data[2], 'timestamp': data[3]})
                #
            if table == 'HealthViolations':
                # violationId, startTime, businessTransaction,description,severity,tierId,appId
                self.session.query(HealthViolations).filter(HealthViolations.violationId == data[0]).update(
                    {'startTime': data[1], 'businessTransaction': data[2], 'description': data[3], 'severity': data[4],
                     'tierId': data[5], 'appId': data[6], 'timestamp': data[7]}, synchronize_session='fetch')
                #
            if table == 'ACItemp':
                # IP, dn, appId, selector (0 or 1)
                self.session.query(ACItemp).filter(ACItemp.dn == data[0]).update({'IP': data[1], 'tenant': data[2]})

                #
            if table == 'ACIPerm':
                # IP, dn, appId
                self.session.query(Tiers).filter(Tiers.tierId == data[0]).update(
                    {'tierName': data[1], 'appId': data[2], 'tierHealth': data[3]})

                # self.commitSession()
                # current_app.logger.info('Table Updated '+str(table))
        except Exception as e:
            current_app.logger.info('Exception in Update:' + str(e))
            self.commitSession()

    def returnValues(self, table):
        try:
            if table == 'Mapping':
                return self.session.query(Mapping).all()
            if table == 'Application':
                # query = self.session.query(Application).all()
                return self.session.query(Application).all()
                # return self.session.query(Application).filter(Application.appId == data[0])
            if table == 'Tiers':
                return self.session.query(Tiers).all()
            if table == 'Nodes':
                return self.session.query(Nodes).all()
            if table == 'ServiceEndpoints':
                return self.session.query(ServiceEndpoints).all()
            if table == 'HealthViolations':
                return self.session.query(HealthViolations).all()
            if table == 'ACItemp':
                return self.session.query(ACItemp).all()
            if table == 'ACIperm':
                return self.session.query(ACIperm).all()
            else:
                return []
        except Exception as e:
            current_app.logger.info('Exception in returning values for table: ' + str(table) + ', Error:' + str(e))
            self.commitSession()
            return []

    def deleteEntry(self, table, deleteid):
        try:
            current_app.logger.info('To delete from table: ' + str(table) + '; id -' + str(deleteid))
            if table == 'Application':
                self.session.query(Application).filter(Application.appId == int(deleteid)).delete()

            if table == 'Mapping':
                self.session.query(Mapping).filter(Mapping.appId == str(deleteid)).delete()

            if table == 'Tiers':
                self.session.query(Tiers).filter(Tiers.tierId == int(deleteid)).delete()

            if table == 'Nodes':
                self.session.query(Nodes).filter(Nodes.nodeId == int(deleteid)).delete()

            if table == 'ServiceEndpoints':
                self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == int(deleteid)).delete()

            if table == 'HealthViolations':
                self.session.query(HealthViolations).filter(HealthViolations.violationId == int(deleteid)).delete()
                # if table == 'ACItemp':
                #     self.session.query(ACItemp).filter(appId=int(id)).delete()
                # if table == 'ACIperm':
                #     self.session.query(ACIperm).filter(appId=int(id)).delete()
                # if table == 'Mapping':
                #    self.session.query(Mapping).filter(Mapping.appId == int(deleteid)).delete()
                # current_app.logger.info('Table Values deleted for - '+str(table))
        except Exception as e:
            current_app.logger.info('Exception Deleting values in table - ' + str(e))
            self.commitSession()

    def checkAndDelete(self, table, idList):
        try:
            tabledata = self.returnValues(table)
        except Exception as e:
            current_app.logger.info('Exception Deleting values in table - ' + str(e))  # return "Nothing to delete"
        if not tabledata:
            current_app.logger.info('Nothing to Delete')
        if tabledata:
            tableids = []
            if table == 'Application':
                for each in tabledata: tableids.append(each.appId)
            if table == 'Tiers':
                for each in tabledata: tableids.append(each.tierId)
            if table == 'Nodes':
                for each in tabledata: tableids.append(each.nodeId)
            if table == 'ServiceEndpoints':
                for each in tabledata: tableids.append(each.sepId)
            if table == 'HealthViolations':
                for each in tabledata: tableids.append(each.violationId)
            deleteList = list(set(tableids) - set(idList))
            current_app.logger.info('Delete for table:'+str(table)+', idlist: '+str(idList))
            try:
                for each in deleteList: self.deleteEntry(table, each)
            except Exception as e:
                current_app.logger.info('Exception in Check and Delete: ' + str(e))
                self.commitSession()

    def insertOrUpdate(self, table, key, data):
        try:
            if table == "EpgHistory":
                recordExists = self.session.query(exists().where(EpgHistory.epgDn == key)).scalar()
                
                if recordExists:
                    data_dict = {
                        "epgFaultRecords": data[0],
                        "epgHealthRecords": data[1],
                        "epgEventRecords": data[2],
                        "epgLogRecords": data[3],
                        "timestamp": data[4]
                    }
                    action = "Updating"
                    self.session.query(EpgHistory).filter(EpgHistory.epgDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgHistoryRecord = EpgHistory(epgDn = key, epgFaultRecords = data[0], epgHealthRecords = data[1], epgEventRecords = data[2], epgLogRecords = data[3], timestamp = data[4])
                    self.session.add(epgHistoryRecord)
                
            elif table == "EpgSummary":
                recordExists = self.session.query(exists().where(EpgSummary.epgDn == key)).scalar()
                
                if recordExists:
                    data_dict = {
                        "epgDomains": data[0],
                        "epgSubnets": data[1],
                        "epgStaticEps": data[2],
                        "epgStaticLeaves": data[3],
                        "epgFcPaths": data[4],
                        "epgStaticPorts": data[5],
                        "epgIfConns": data[6],
                        "epgContracts": data[7],
                        "epgLabels": data[8],
                        "timestamp": data[9]
                    }
                    action = "Updating"
                    self.session.query(EpgSummary).filter(EpgSummary.epgDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgSummaryRecord = EpgSummary(epgDn = key, epgDomains = data[0], epgSubnets = data[1], epgStaticEps = data[2], epgStaticLeaves = data[3], epgFcPaths = data[4], 
                    epgStaticPorts = data[5], epgIfConns = data[6], epgContracts = data[7], epgLabels = data[8], timestamp = data[9])
                    self.session.add(epgSummaryRecord)
            elif table == "ApHistory":
                recordExists = self.session.query(exists().where(ApHistory.apDn == key)).scalar()
                
                if recordExists:
                    data_dict = {
                        "apFaultRecords": data[0],
                        "apHealthRecords": data[1],
                        "apEventRecords": data[2],
                        "apLogRecords": data[3],
                        "timestamp": data[4]
                    }
                    action = "Updating"
                    self.session.query(ApHistory).filter(ApHistory.apDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    epgHistoryRecord = ApHistory(apDn = key, apFaultRecords = data[0], apHealthRecords = data[1], apEventRecords = data[2], apLogRecords = data[3], timestamp = data[4])
                    self.session.add(epgHistoryRecord)
            elif table == "ApSummary":
                recordExists = self.session.query(exists().where(ApSummary.apDn == key)).scalar()
                
                if recordExists:
                    data_dict = {
                        "apEpgs": data[0],
                        "apUsegEpgs": data[1],
                        "timestamp": data[2]
                    }
                    action = "Updating"
                    self.session.query(ApSummary).filter(ApSummary.apDn == key).update(data_dict)
                else:
                    action = "Inserting"
                    apSummaryRecord = ApSummary(apDn = key, apEpgs = data[0], apUsegEpgs = data[1], timestamp = data[2])
                    self.session.add(apSummaryRecord)
                    
            self.commitSession()

        except Exception as ex:
            current_app.logger.info('Exception while ' + action + ' Record in: \n Table : ' + table + "\n " + str(ex))
            self.commitSession()
        
                
    # Gets Data From Table and Updates or Inserts a record with given ID
    def checkIfExistsandUpdate(self, table, data):
        try:
            dataId = data[0]
            tableids = []

            # Step 1: Insert or Update
            tabledata = self.returnValues(table)

            if tabledata:
                if table == 'Mapping':
                    for each in tabledata: tableids.append(each.appId)
                if table == 'Application':
                    for each in tabledata: tableids.append(each.appId)
                if table == 'Tiers':
                    for each in tabledata: tableids.append(each.tierId)
                if table == 'Nodes':
                    for each in tabledata: tableids.append(each.nodeId)
                if table == 'ServiceEndpoints':
                    for each in tabledata: tableids.append(each.sepId)
                if table == 'HealthViolations':
                    for each in tabledata: tableids.append(each.violationId)
                if table == 'ACItemp':
                    for each in tabledata: tableids.append(each.dn)
            if tableids:
                if dataId in tableids:
                    current_app.logger.info('Update table:' + str(table) + ' with Values:' + str(data))
                    self.update(table, data)
                else:
                    current_app.logger.info('Insert into table:' + str(table) + ' with Values:' + str(data))
                    self.insertInto(table, data)
                    # update
            else:
                current_app.logger.info('Insert into table:' + str(table) + ' with Values:' + str(data))
                self.insertInto(table, data)
            # current_app.logger.info('Insert/Update executed for Table:'+str(table))
            self.commitSession()
        except Exception as e:
            current_app.logger.info('Exception in Insert: ' + str(e))
            self.commitSession()

    # Returns values from database based on query filers (IDs)
    def returnApplication(self, query_type, query_params):
        try:
            if query_type == 'appId':
                # query = self.session.query(Application).all()

                return self.session.query(Application).filter(Application.appId == query_params)
            if query_type == 'appName':
                return self.session.query(Application).filter(Application.appName == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return Application details. Error: " + str(
                                   e)})

    def returnFaults(self, dn):
        try:
            faults_list = []
            if "/epg-" in dn:
                epg_records = self.session.query(EpgHistory.epgDn, EpgHistory.epgFaultRecords).filter(EpgHistory.epgDn == dn)
                for epg in epg_records:
                    faults_list = epg.epgFaultRecords["faultRecords"]
                
            elif "/ap-" in dn:
                ap_records = self.session.query(ApHistory.apDn, ApHistory.apFaultRecords).filter(ApHistory.apDn == dn)
                for ap in ap_records:
                    faults_list = ap.apFaultRecords["faultRecords"]
            
            return {
                "payload" : faults_list,
                "status" : True,
                "message" : ""
            }
                
        except Exception as ex:
            return {
                "payload": [],
                "status": False,
                "message": "Internal backend error: could not return Fault details. Error: " + str(ex)
            }
    
    def returnEvents(self, dn):
        try:
            events_list = []
            if "/epg-" in dn:
                epg_records = self.session.query(EpgHistory.epgDn, EpgHistory.epgEventRecords).filter(EpgHistory.epgDn == dn)
                for epg in epg_records:
                    events_list = epg.epgEventRecords["eventRecords"]
                
            elif "/ap-" in dn:
                ap_records = self.session.query(ApHistory.apDn, ApHistory.apEventRecords).filter(ApHistory.apDn == dn)
                for ap in ap_records:
                    events_list = ap.apEventRecords["eventRecords"]
            
            return {
                "payload" : events_list,
                "status" : True,
                "message" : ""
            }
                
        except Exception as ex:
            return {
                "payload": [],
                "status": False,
                "message": "Internal backend error: could not return Event details. Error: " + str(ex)
            }
    
    def returnAuditLogs(self, dn):
        try:
            audit_logs_list = []
            if "/epg-" in dn:
                epg_records = self.session.query(EpgHistory.epgDn, EpgHistory.epgLogRecords).filter(EpgHistory.epgDn == dn)
                for epg in epg_records:
                    audit_logs_list = epg.epgLogRecords["auditLogRecords"]
                
            elif "/ap-" in dn:
                ap_records = self.session.query(ApHistory.apDn, ApHistory.apLogRecords).filter(ApHistory.apDn == dn)
                for ap in ap_records:
                    audit_logs_list = ap.apLogRecords["auditLogRecords"]
            
            return {
                "payload" : audit_logs_list,
                "status" : True,
                "message" : ""
            }
                
        except Exception as ex:
            return {
                "payload": [],
                "status": False,
                "message": "Internal backend error: could not return Audit Log details. Error: " + str(ex)
            }

    def returnTiers(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                # query = self.session.query(Application).all()
                return self.session.query(Tiers).filter(Tiers.tierId == query_params)
            if query_type == 'tierName':
                return self.session.query(Tiers).filter(Tiers.tierName == query_params)
            if query_type == 'appId':
                return self.session.query(Tiers).filter(Tiers.appId == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return Tier details. Error: " + str(e)})


    def returnNodes(self, query_type, query_params):
        try:
            if query_type == 'nodeId':
                # query = self.session.query(Application).all()
                return self.session.query(Nodes).filter(Nodes.nodeId == query_params)
            if query_type == 'nodeName':
                return self.session.query(Nodes).filter(Nodes.nodeName == query_params)
            if query_type == 'tierId':
                return self.session.query(Nodes).filter(Nodes.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(Nodes).filter(Nodes.appId == query_params)
            if query_type == 'ipAddress':
                return self.session.query(Nodes).filter(func.json_contains(Nodes.ipAddress, query_params) == 1).all()
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return Node details. Error: " + str(e)})

    def returnServiceEndpoints(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                # query = self.session.query(Application).all()
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.appId == query_params)
            if query_type == 'sepId':
                return self.session.query(ServiceEndpoints).filter(ServiceEndpoints.sepId == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return service endpoints. Error: " + str(
                                   e)})

    def returnHealthViolations(self, query_type, query_params):
        try:
            if query_type == 'tierId':
                # query = self.session.query(Application).all()
                return self.session.query(HealthViolations).filter(HealthViolations.tierId == query_params)
            if query_type == 'appId':
                return self.session.query(HealthViolations).filter(HealthViolations.appId == query_params)
            if query_type == 'violationId':
                return self.session.query(HealthViolations).filter(HealthViolations.violationId == query_params)
            if query_type == 'severity':
                return self.session.query(HealthViolations).filter(HealthViolations.severity == query_params)
            if query_type == 'startTime':
                return self.session.query(HealthViolations).filter(HealthViolations.startTime == query_params)
            if query_type == 'businessTransaction':
                return self.session.query(HealthViolations).filter(HealthViolations.businessTransaction == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return Health violations. Error: " + str(
                                   e)})

    # Returns values from database based on query filers for ACI objects
    def returnACItemp(self, query_type, query_params):
        try:
            if query_type == 'IP':
                return self.session.query(ACItemp).filter(ACItemp.IP == query_params)
            if query_type == 'dn':
                return self.session.query(ACItemp).filter(ACItemp.dn == query_params)
            if query_type == 'selector':
                return self.session.query(ACItemp).filter(ACItemp.selector == query_params)
            if query_type == 'appId':
                return self.session.query(ACIperm).filter(ACIperm.appId == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return ACI objects. Error: " + str(e)})

    def returnACIperm(self, query_type, query_params):
        try:
            if query_type == 'IP':
                return self.session.query(ACIperm).filter(ACIperm.IP == query_params)
            if query_type == 'dn':
                return self.session.query(ACIperm).filter(ACIperm.dn == query_params)
            if query_type == 'appId':
                return self.session.query(ACIperm).filter(ACIperm.appId == query_params)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not return ACI objects. Error: " + str(e)})

    def storechangesinACItemp(self, data):
        try:
            self.session.query(ACItemp).filter(ACItemp.dn == data).update(
                {'selector': 1})
            self.commitSession()
            return "Stored"
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not store data into databse. Error: " + str(
                                   e)})

    def getappList(self):
        try:
            appList = self.session.query(Application).all()
            applicationList = []
            for app in appList:
                application = {'appId': app.appId, 'appName': str(app.appName),
                               'appHealth': str(app.appMetrics['data'][0]['severitySummary']['performanceState']),
                               'isViewEnabled': app.isViewEnabled}
                applicationList.append(application)
            self.commitSession()
            return applicationList
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not retrieve Application list. Error: " + str(
                                   e)})

    def enableViewUpdate(self, appId, bool):
        try:
            self.session.query(Application).filter(Application.appId == appId).update(
                {'isViewEnabled': bool})
            return self.commitSession()
        except Exception as e:
            self.flushSession()
            # return json.dumps({"payload": {}, "status_code": "300", "message": "Could not enable the view for application"+str(appId)+". Error: "+str(e)})

    def saveMappings(self, appId, mapped_data):
        try:
            self.checkIfExistsandUpdate('Mapping', [appId, mapped_data])
            return "Mapping Saved."
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not save mappings. Error: " + str(e)})

    def returnMapping(self, query_params):
        try:
            table_data = self.session.query(Mapping).filter(Mapping.appId == query_params)
            for first in table_data:
                return first.mapped_data
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not retrieve mappings. Error: " + str(e)})

    def ipsforapp(self, appId):
        try:
            return self.returnNodes('appId', appId)
        except Exception as e:
            self.flushSession()
            return json.dumps({"payload": {}, "status_code": "300",
                               "message": "Internal backend error: could not retrieve nodes. Error: " + str(e)})

# ======= MAIN ========
# databaseObject = Database()
# databaseObject.createTables()
# x= databaseObject.returnServiceEndpoints('tierId',8)
# print x
# for each in x:
#     print type(each.sep)
#     if isinstance(each.sep,dict):
#         print True
#     else:
#         print each.sep
# x = databaseObject.returnHealthViolations('tierId',8)
# print x
# for each in x:
#     print type(x.violationId)
# tiers =  databaseObject.returnValues('Tiers')
# for each in tiers:
#     print each.tierId

# print databaseObject.returnValues('Application')
# x= databaseObject.returnValues('Nodes')
# for each in x:
#     print x.nodeId
# for each in databaseObject.returnValues('Mapping'):
#     print(str(each.appId))
#     print(str(each.mapped_data))

#
# for appid in range(0,4):
#     (databaseObject.insertInto('Application', [appid, 'App1', {'m1': 'v1', 'm2': 'v2'}]))
# databaseObject.commitSession()
#
# print "============"
# time.sleep(5)
# vals = databaseObject.returnValues('ACItemp')
#
# for each in vals:
#     print str(each.dn) + "  /  " + str(each.IP)
#     print each.tenant
#     print each.appId
#     print each.selector
#
# time.sleep(3)
#
# databaseObject.checkIfExistsandUpdate('Application',[1, 'App1', {'m1': 'v1', 'm2': 'v2'}])
# databaseObject.getappList()
# databaseObject.checkIfExistsandUpdate('Map', [5, [{'IP': '10.10.10.20', 'dn': 'uni/tn-appd/ap-ap1/epg-epg1'},
#                                               {'IP': '10.10.10.15', 'dn': 'uni/tn-appd/ap-ap2/epg-epg2'}]])
# x =  databaseObject.returnMapping(8)
# print x
# for each in x:
#     print each.appId
#     print each.mapped_data
# for each in databaseObject.ipsforapp(5):
#     print each.ipAddress
# mapped_data = [{'ipaddress':'20.20.20.12','domains': [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Ecomm',
#                'recommended': False}]}, {'ipaddress':'20.20.20.11','domains': [{'domainName': 'uni/tn-AppDynamics/ap-AppD-AP1-EcommerceApp/epg-AppD-Pay',
#                'recommended': False}]}]
# appId = 8
# databaseObject.saveMappings(appId,mapped_data)
