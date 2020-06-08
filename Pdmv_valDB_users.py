#!/usr/bin/env python2.6

import os, sys
import urllib2
import subprocess
import json

from HTMLParser import HTMLParser

import logging
logging.basicConfig(level=logging.INFO, filename='./suds.log')
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

# enable the following for _much_ more debugging:
# logging.getLogger('suds.wsdl').setLevel(logging.DEBUG)
# logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)

# point this to your installation of suds:
sudsPath = os.path.join(os.environ['HOME'],'python')
sys.path.append(sudsPath)

from suds.client import Client
from suds.transport.http import HttpAuthenticated
from suds import WebFault

import netrc

import subprocess
import copy
import time

import service
from database_access import *
from sqlalchemy import create_engine

connectionDictionary = service.secrets['connections']['dev']["writer"]
engine = create_engine(service.getSqlAlchemyConnectionString(connectionDictionary),
        echo=False)

Session = sessionmaker(bind=engine)


possible_status_list = ["CSC", "TAU", "TRACKING", "BTAG", "JET", "ECAL", "RPC", "PHOTON",
        "MUON", "MET", "ELECTRON", "TK", "HCAL", "DT", "SUMMARY", "TAU", "JET", "HIGGS",
        "TOP", "MUON", "PHOTON", "MET", "ELECTRON", "EXOTICA", "SUSY", "HEAVYFLAVOR",
        "SUMMARY", "B", "HIGGS", "FWD", "TOP", "SMP", "EXOTICA", "SUSY", "B2G", "HIN",
        "CASTOR", "L1", "GEN", "MTD", "PPS", "SUMMARY"]

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    email = ""
    get_name = False
    name = ""
    def handle_data(self, data):
        if (data.find('@') != -1):
            self.email = data
        if (data.find('CMS Member Info:') != -1):
            self.get_name = True
            return False
        if self.get_name:
            self.name = data.decode('utf-8').encode('ascii', 'ignore')
            self.get_name = False

    def result(self):
        return self.email
    def userName(self):
        return self.name

def getMembers(egroup):

    # you need to authenticate with your NICE credentials to the web service,
    # so we get them from our ~/.netrc file:
    auth = netrc.netrc()
    login, acct, pwd = auth.authenticators('egroupsap.cern.ch')  # for the primary account

    #url = 'https://cra-ws.cern.ch/cra-ws/CraEgroupsWebService.wsdl' #old WSDL adress
    url = "https://foundservices.cern.ch/ws/egroups/v1/EgroupsWebService/EgroupsWebService.wsdl"
    client = Client(url, username=login, password=pwd)

    #for egroup in egList:
    groupRes = client.service.FindEgroupByName(egroup).result

    memList = groupRes.Members
    return memList

def write_to_twiki_file(outputFile, columns, full_name, user_Name, user_Email):
    for kind in columns:
        full_name = "Thomas Muller" if user_Name == "tmuller" else full_name
        twiki_output = '| %s | %s | %s | %s |\n' % (kind,
                full_name.encode('utf-8'), user_Name, user_Email)

        outputFile.write(twiki_output)

def get_HNews_info(user_name):
    if user_name.lower() == "defilip":    ##when users are registered in HN with
        user_name = "ndefilip"            ##different email than lxplus account
    elif user_name.lower() == "ligabue":
        user_name = "fligabue"
    hyperNews_url = 'https://hypernews.cern.ch/HyperNews/CMS/view-member.pl?' + user_name.lower()
    args = ['curl','--insecure', hyperNews_url, '-s']
    proc = subprocess.Popen(args, stdout = subprocess.PIPE)
    proc_output = proc.communicate()[0]

    parser = MyHTMLParser()
    html_resp = parser.feed(proc_output)
    return parser #return a HTML parser

def make_RDataList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrRDataStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['Reconstruction']['Data']: ##if adding new Category
                add_user = True
                usrRDataStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                str(user_FullName), user_Name, user_Email)
    else:
        usrRDataStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
            str(user_FullName), user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  RData: %s" % (usrRDataStatList))
    else:
        print("Nothing to do...")

    return add_user, usrRDataStatList

def make_HLTDataList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrHDataStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['HLT']['Data']: ##if adding new Category
                add_user = True
                usrHDataStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                user_FullName, user_Name, user_Email)

    else:
        usrHDataStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
                user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  HData: %s" % (usrHDataStatList))
    else:
        print("Nothing to do...")

    return add_user, usrHDataStatList

def make_RFastFullList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrRFastStatList = []
    usrRFullStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['Reconstruction']['FullSim']: ##if adding new Category
                add_user = True
                usrRFullStatList.append(kind)
            if not kind in user_DB["validators"][user_Name]['Reconstruction']['FastSim']: ##if adding new Category
                add_user = True
                usrRFastStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                    user_FullName, user_Name, user_Email)

    else:
        usrRFullStatList = column
        usrRFastStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
                user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  RFull: %s RFast: %s" % (usrRFullStatList, usrRFastStatList))
    else:
        print("Nothing to do...")

    return add_user, usrRFastStatList, usrRFullStatList

def make_PAGsList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrPDataStatList = []
    usrPFastStatList = []
    usrPFullStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['PAGs']['Data']: ##if adding new Category
                add_user = True
                usrPDataStatList.append(kind)
            if not kind in user_DB["validators"][user_Name]['PAGs']['FullSim']: ##if adding new Category
                add_user = True
                usrPFullStatList.append(kind)
            if not kind in user_DB["validators"][user_Name]['PAGs']['FastSim']: ##if adding new Category
                add_user = True
                usrPFastStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                    user_FullName, user_Name, user_Email)

    else:
        usrPDataStatList = column
        usrPFullStatList = column
        usrPFastStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
               user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  PData: %s PFull: %s PFast: %s" % (usrPDataStatList, usrPFullStatList, usrPFastStatList))
    else:
        print("Nothing to do...")

    return add_user, usrPDataStatList, usrPFastStatList, usrPFullStatList

def make_HLTFastFullList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrHFastStatList = []
    usrHFullStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['HLT']['FullSim']: ##if adding new Category
                add_user = True
                usrHFullStatList.append(kind)
            if not kind in user_DB["validators"][user_Name]['HLT']['FastSim']: ##if adding new Category
                add_user = True
                usrHFastStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                    user_FullName, user_Name, user_Email)

    else:
        usrHFullStatList = column
        usrHFastStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
                user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  HFull: %s HFast: %s" %(usrHFullStatList, usrHFastStatList))
    else:
        print("Nothing to do...")

    return add_user, usrHFastStatList, usrHFullStatList

def make_GENFullList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrGGenStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            print("Checking GEN in user DB. column: %s" % (kind))
            if not kind in user_DB["validators"][user_Name]['GEN']['Gen']: ##if adding new Category
                add_user = True
                usrGGenStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind],
                    user_FullName, user_Name, user_Email)

    else:
        usrGGenStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
                user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  GEN/Gen: %s " % (usrGGenStatList))
    else:
        print("Nothing to do...")

    return add_user, usrGGenStatList

def make_HINDataFullList(user_Name, user_FullName, column, user_DB, user_Email, twikiFile):
    usrIDataStatList = []
    usrIFullStatList = []
    add_user = False
    if user_Name in user_DB["validators"]: ##if user in DB
        print("User: %s is in DB. Checking New columns" % (user_Name))
        for kind in column:
            if not kind in user_DB["validators"][user_Name]['IN']['Data']: ##if adding new Category
                add_user = True
                usrIDataStatList.append(kind)
            if not kind in user_DB["validators"][user_Name]['IN']['FullSim']: ##if adding new Category
                add_user = True
                usrIFullStatList.append(kind)
            write_to_twiki_file(twikiFile, [kind+"_HIN"],
                    user_FullName, user_Name, user_Email)

    else:
        usrIDataStatList = column
        usrIFullStatList = column
        add_user = True
        write_to_twiki_file(twikiFile, column,
                user_FullName, user_Name, user_Email)

    if add_user:
        print("Adding...")
        print("  IData: %s IFull: %s" % (usrIDataStatList, usrIFullStatList))
    else:
        print("Nothing to do...")

    return add_user, usrIDataStatList, usrIFullStatList

def get_Egroup_info(addr):
    args = ['curl', '--cookie', 'krbcookie', '-k', addr, '-s']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    proc_output = proc.communicate()[0]
    return proc_output

def check_options(info, egroup, acc_type):
    if acc_type != 'Account':
        return None
    else:
        if 'Cc' in info:
            return None
        if 'Upg' in info:
            return "Upg"
        else:
            return egroup

def get_user_inf_file(egroup_addr, user_DB):
    unser_name_list = []
    print("##debug## %s" % (egroup_addr))
    egroup = egroup_addr.keys()[0]

    usrRDataStatList = []
    usrRFastStatList = []
    usrRFullStatList = []
    usrPDataStatList = []
    usrPFastStatList = []
    usrPFullStatList = []
    usrHDataStatList = []
    usrHFastStatList = []
    usrHFullStatList = []
    usrIDataStatList = []
    usrIFastStatList = []
    usrIFullStatList = []
    usrGGenStatList = []
    twikiFile = open(egroup+'.txt', 'w')
    twikiFile.write(egroup+'\n')
    twikiFile.write('| *Category* | *Full name* | *User name* | *E-mail* |\n')
###open Upg File
    twikiFileUpg = open(egroup+'-Upg.txt', 'w')
    twikiFileUpg.write(egroup+'\n')
    twikiFileUpg.write('| *Category* | *Full name* | *User name* | *E-mail* |\n')

###
    memberList = getMembers(egroup)
###

    for index, elem in enumerate(memberList):
        if not "Comments" in elem:
            continue ##no comments field -> ussually its another e-group address

        fileName = check_options(elem["Comments"], egroup, elem["Type"])

        if fileName != None:
            if fileName == 'Upg':
                fileWrite = twikiFileUpg
            else:
                fileWrite = twikiFile
        #if ((elem[0] == 'A') and (elem.find('Cc') == -1)):
            add = False
            __adding_HIN = False
            #user_params = ["",memberList[index].Name, memberList[index].Comments]
            if memberList[index].Name.lower() == 'perrotta':  # for 3 users with different CMS accounts
                memberList[index].Name = 'aperrott'
            if memberList[index].Name.lower() == 'gobbo':
                memberList[index].Name = 'benigno'
            if memberList[index].Name.lower() == 'gbrona':
                memberList[index].Name = 'brona'

            parser = get_HNews_info(memberList[index].Name)
            if parser.result() == '':
                print("%s Doesnt exists in HyperNews. Skipping" % (elem.Name))
                continue

            eGroup_script = memberList[index].Email.lower()
            hyperNews_data = parser.result().lower()
            if  eGroup_script == hyperNews_data:
                user_Email = memberList[index].Email ##if user emails in egroup & hypernews are same, add egroup mail
            else:
                print("%s Different emails." % (memberList[index].Name.lower()))
                print("  Using H-News email.")
                user_Email = parser.result() ##if users email is different -> add HN mail
            user_Name = memberList[index].Name.lower()
            user_name_list.append(user_Name)  ##add to full username_List
            memberList[index].Comments = memberList[index].Comments.replace(' Upg', '')
            if (memberList[index].Comments.upper() == 'TRACKER'):
                print("User: %s TRACKER colum set to TK" % (user_Name))
                memberList[index].Comments = 'TK'
            if (memberList[index].Comments.upper() == 'EXO'):
                memberList[index].Comments = 'EXOTICA'
            if (memberList[index].Comments == 'Admin'):  #in case we want to add an Admin (this is only for adding validators)
                print("%s is Admin: Skipping" % (user_Name))
                continue
            column = memberList[index].Comments.upper()
            columns = column.split('/')
            for index,element in enumerate(columns):
                if (element.upper() == 'TRACKER'):
                     columns[index] = 'TK'
                if (element.upper() == 'EXO'):
                    columns[index] = 'EXOTICA'
            new_columns = []
            catSubCat = ""
            for element in columns:
                if element.upper().replace(" ","") in possible_status_list:
                    new_columns.append(element.upper())
                elif element.find("_HIN") != -1:
                    __adding_HIN = True
                    new_columns.append(element.upper())
                else:
                    print("%s: %s %s Not in column list" % (user_Name, egroup, element))
            if new_columns == []:
                add = False
            column = new_columns
            if egroup == 'cms-PPD-PdmV-DATAval':
                if __adding_HIN:
                    catSubCat = 'IN/Data'
                    _hin_columns = []
                    for el in column:
                        _hin_columns.append(el.replace("_HIN", ""))
                    #another use case for HIN section
                    result = make_HINDataFullList(user_Name, parser.name, _hin_columns, user_DB,
                            user_Email, fileWrite)

                    add = result[0]
                    usrIDataStatList = result[1]
                else:
                    catSubCat = 'Reconstruction/Data'
                    result = make_RDataList(user_Name, parser.name, column, user_DB,
                            user_Email, fileWrite)

                usrRDataStatList = result[1]
                add = result[0]
            if egroup == 'cms-PPD-PdmV-HLTDATAval':
                catSubCat = 'HLT/Data'
                result = make_HLTDataList(user_Name, parser.name, column, user_DB,
                        user_Email, fileWrite)

                add = result[0]
                usrHDataStatList = result[1]
            if egroup == 'cms-PPD-PdmV-MCval':

                if "GEN" in column:
                    catSubCat = "/GEN/GEN/Gen"
                    # use case for GEN section while users are in MC list
                    result = make_GENFullList(user_Name, parser.name, column, user_DB,
                            user_Email, fileWrite)
                    add = result[0]
                    usrGGenStatList = result[1]
                elif __adding_HIN:
                    catSubCat = "HIN/Data/FullSim"
                    _hin_columns = []
                    for el in column:
                        _hin_columns.append(el.replace("_HIN", ""))
                    #another use case for HIN section
                    result = make_HINDataFullList(user_Name, parser.name, _hin_columns, user_DB,
                            user_Email, fileWrite)
                    add = result[0]
                    # usrIDataStatList = result[1]
                    usrIFullStatList = result[2]
                else:
                    catSubCat = 'Reconstruction/FullSim/FastSim'
                    result = make_RFastFullList(user_Name, parser.name, column, user_DB,
                            user_Email, fileWrite)
                    add = result[0]
                    usrRFastStatList = result[1]
                    usrRFullStatList = result[2]
            if egroup == 'cms-PPD-PdmV-PAGval':
                catSubCat = 'PAGs/Data/FullSim/FastSim'
                result = make_PAGsList(user_Name, parser.name, column, user_DB,
                        user_Email, fileWrite)

                add = result[0]
                usrPDataStatList = result[1]
                usrPFastStatList = result[2]
                usrPFullStatList = result[3]
            if egroup == 'cms-PPD-PdmV-HLTval':
                catSubCat = 'HLT/FullSim/FastSim'
                result = make_HLTFastFullList(user_Name, parser.name, column, user_DB,
                        user_Email, fileWrite)

                add = result[0]
                usrHFastStatList = result[1]
                usrHFullStatList = result[2]
            if add:
                print("Adding user: %s in: %s" % (user_Name, catSubCat))
                check1 = addUser(user_Name, Session, user_Email)
                check2 = grantValidatorRights(user_Name, Session)
                check3 = grantValidatorRightsForStatusKindList(user_Name,
                    usrRDataStatList, usrRFullStatList, usrRFastStatList,
                    usrHDataStatList, usrHFullStatList,
                    usrPDataStatList, usrPFullStatList, usrPFastStatList,
                    usrIDataStatList, usrIFullStatList, usrIFastStatList,
                    usrGGenStatList, Session) #3 empty for HIN & 1 for GEN

            usrRDataStatList = []
            usrRFastStatList = []
            usrRFullStatList = []
            usrPDataStatList = []
            usrPFastStatList = []
            usrPFullStatList = []
            usrHDataStatList = []
            usrHFastStatList = []
            usrHFullStatList = []
            usrIDataStatList = []
            usrIFullStatList = []
            usrIFastStatList = []
            usrGGenStatList = []
            print("")

    twikiFile.close()
    twikiFileUpg.close()
    return user_name_list

def delete_removed_users(new_userList, DB_userList): ##  if user is in DB
    for user in DB_userList:                        ###   but not in the new userList column 
        if user not in new_userList:               ###   -> delete him from DB
            # removeUser(user, Session)
            print("User to be removed: %s" % (user))

def get_coockie():
    args = ['cern-get-sso-cookie', '--krb', '-u', 'https://e-groups.cern.ch', '-o', 'krbcookie', '--nocertverify']
    proc = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
    proc_output = proc.communicate()[0]

if __name__ == '__main__':
    egroups = [{'cms-PPD-PdmV-DATAval' : 'https://e-groups.cern.ch/e-groups/cern.cra.EgroupsFileServlet?id=10016432'},
            {'cms-PPD-PdmV-HLTDATAval' : 'https://e-groups.cern.ch/e-groups/cern.cra.EgroupsFileServlet?id=10058359'},
            {'cms-PPD-PdmV-HLTval' : 'https://e-groups.cern.ch/e-groups/cern.cra.EgroupsFileServlet?id=10021320'},
            {'cms-PPD-PdmV-MCval' : 'https://e-groups.cern.ch/e-groups/cern.cra.EgroupsFileServlet?id=10016411'},
            {'cms-PPD-PdmV-PAGval' : 'https://e-groups.cern.ch/e-groups/cern.cra.EgroupsFileServlet?id=10016451'}]

    user_name_list = []
    DB_user_info = json.loads(getAllUsersInfo('*', Session))

    ##get Shibboleth cookie from kerberos token
    get_coockie()

    for elem in egroups:
        print("#####")
        print("Working on: %s" % (elem.items()[0][0]))
        print("####")
        user_name_list += get_user_inf_file(elem, DB_user_info)
    user_name_list = list(set(user_name_list)) ## make userName list unique
    delete_removed_users(user_name_list, DB_user_info["validators"])
