var app = angular.module('strap', ['ui.bootstrap']).config(function($locationProvider){$locationProvider.html5Mode(true);});

function tableController($scope, $http, $location){
  $scope.releaseList = [];
  $scope.shortInfoReleases = [];
  $scope.shortInfo = [];
  $scope.underscore = _;
  $scope.orderedMenu = ["Reconstruction", "HLT", "PAGs", "IN", "GEN"];
  $scope.menus = {"Reconstruction":{
                    subcats: {"Data":{
                               name: "Data",
                               show:false
                               },
                              "FullSim":{
                               name: "FullSim",
                               show:false},
                              "FastSim":{
                               name:"FastSim",
                               show:false}
                    },
                    name:"Reconstruction",
                    showSubCat : false,
                    priority: 1},
                  "HLT":{
                    subcats: {"Data":{
                               name: "Data",
                               show:false
                               },
                              "FullSim":{
                               name: "FullSim",
                               show:false},
                    },
                    name: "HLT",
                    showSubCat : false,
                    priority: 2},
                  "PAGs":{
                    subcats: {"Data":{
                               name: "Data",
                               show:false
                               },
                              "FullSim":{
                               name: "FullSim",
                               show:false},
                              "FastSim":{
                               name:"FastSim",
                               show:false}
                    },
                    name:"PAGs",
                    showSubCat : false,
                    priority: 3},
                  "IN":{
                    subcats: {"Data":{
                               name: "Data",
                               show:false
                               },
                              "FullSim":{
                               name: "FullSim",
                               show:false},
                              // "FastSim":{ //Beacause Heavy Ions
                              //  name:"FastSim",
                              //  show:false}
                    },
                    name:"IN",
                    showSubCat : false,
                    priority: 4},
                  "GEN":{
                    subcats: {"Gen":{
                               name: "Gen",
                               show:false
                               },
                    },
                    name:"GEN",
                    showSubCat : false,
                    priority: 5}
  };
  $scope.Headers = {"Reconstruction":
      [{name:"Release Name", db_name:"Release_Name"}, {name:"Tracker", db_name:"TK"}, {name:"Ecal", db_name:"Ecal"}, {name:"HGcal", db_name:"HGCAL"}, {name:"Hcal", db_name:"Hcal"}, {name:"CASTOR", db_name:"CASTOR"}, {name:"DT",db_name:"DT"}, {name:"CSC", db_name:"CSC"}, 
       {name:"RPC", db_name:"RPC"}, {name:"GEM", db_name:"GEM"}, {name:"MTD", db_name:"MTD"}, {name:"PPS", db_name:"PPS"}, {name:"L1", db_name:"L1"}, {name:"Tracking", db_name:"Tracking"}, {name:"Electron", db_name:"Electron"}, {name:"Photon", db_name:"Photon"}, {name:"Muon", db_name:"Muon"}, 
       {name:"Jet", db_name:"Jet"}, {name:"MET", db_name:"MET"}, {name:"bTag", db_name:"bTag"}, {name:"Tau", db_name:"Tau"}, {name:"PF", db_name: "PF"}, {name:"Info", db_name:"Summary"}, {name:"RelMon", db_name:"RelMon"}],
      "HLT":
      [{name:"Release Name", db_name:"Release_Name"}, {name:"Tracking", db_name:"Tracking"}, {name:"Electron", db_name:"Electron"}, {name:"Photon", db_name:"Photon"}, {name:"Muon", db_name:"Muon"}, 
       {name:"Jet", db_name:"Jet"}, {name:"MET", db_name: "MET"},{name:"bTag", db_name: "bTag"}, {name:"Tau", db_name:"Tau"},{name:"SMP", db_name:"SMP"}, {name:"Higgs", db_name:"Higgs"},{name:"Top", db_name:"Top"},
       {name:"Susy", db_name:"Susy"}, {name:"Exotica", db_name:"Exotica"}, {name:"B2G", db_name:"B2G"}, {name:"B", db_name:"B"},{name:"Fwd", db_name:"Fwd"},{name:"HIN", db_name:"HIN"}, {name:"Info", db_name:"Summary"}, {name:"RelMon", db_name:"RelMon"}],
      "PAGs":
      [{name:"Release Name", db_name:"Release_Name"}, {name:"SMP", db_name:"SMP"}, {name:"Higgs", db_name:"Higgs"}, {name:"Top", db_name:"Top"}, {name:"Susy", db_name:"Susy"}, 
       {name:"Exotica", db_name:"Exotica"},{name:"B2G", db_name:"B2G"},{name:"B", db_name:"B"}, {name:"Fwd", db_name:"Fwd"}, {name:"HIN", db_name:"HIN"},{name:"Info", db_name: "Summary"},{name:"RelMon", db_name:"RelMon"}],
      "IN":
      [{name:"Release Name", db_name:"Release_Name"}, {name:"Tracking", db_name:"Tracking"}, {name:"Electron", db_name:"Electron"}, {name:"Photon", db_name:"Photon"}, {name:"Muon", db_name:"Muon"}, {name:"Jet", db_name:"Jet"}, {name:"Info", db_name: "Summary"}, {name:"RelMon", db_name:"RelMon"}],
      "GEN":
      [{name:"Release Name", db_name:"Release_Name"}, {name:"GEN", db_name:"GEN"}, {name:"Info", db_name: "Summary"}, {name:"RelMon", db_name:"RelMon"}]
  };
  $scope.status_icons= {
            "NOT YET DONE" : "media/minus.gif",
            "OK" : "media/choice-yes.gif",
            "FAILURE" : "media/choice-no.gif",
            "CHANGES EXPECTED" : "media/target.gif",
            "IN PROGRESS" : "media/wip.gif",
            "KNOWN ISSUE" : "media/mechanics.gif",
            "OK TO BE SIGNED-OFF BY THE VALIDATORS" : "media/thumbs-up.gif",
            "FAILURE TO BE SIGNED-OFF BY THE VALIDATORS":"media/thumbs-down.gif",
            "RelMon" : "media/arrowlink.gif",
            "Info" : "media/help.gif"
  };
  $scope.getReleaseList = function(){
    $http({method:'POST',url:'submit',data:{releaseName: $scope.searchableName}}).
      success(function(data,status){
        $scope.releaseList = data;
        $scope.showSearchLength = true;
      }).
      error(function(data,status){
        alert("Error: " + status);
      });
  };
  $scope.addSelectedRelease = function(){
    if ($scope.selectedRelease){
      if ($scope.shortInfoReleases.indexOf($scope.selectedRelease) == -1){
        $scope.shortInfoReleases.push($scope.selectedRelease);
        $location.search('selected', $scope.shortInfoReleases.join(","))
        $scope.getReleaseData($scope.selectedRelease);
      }
    }
  };
  $scope.getReleaseData = function(releaseName){
    $http({method:'POST', url:'testSQL',data:{releaseName: releaseName}}).
      success(function(data,status){
        _.each(data, function(elem,key){
          if (key != "RELEASE_NAME"){
            if (_.keys(elem).length == 0){
              delete(data[key]);
            }
          }
        });
        var exists = false;
        _.each($scope.shortInfo, function(elem, index){  //if release is already in display: if so -> remove and push newest info
          if (releaseName == elem["RELEASE_NAME"]){
            //$scope.shortInfo = $scope.shortInfo.splice(index+1,1); 
            $scope.shortInfo[index] = data;
            exists = true;
          }
        });
        if (!exists){
          $scope.shortInfo.push(data);
        }
    }).error(function(data,status){
        alert("Error: "+status);
    });
  };
  $scope.addAllReleases = function(){
    $scope.shortInfoReleases = _.clone($scope.releaseList);
    _.each($scope.shortInfoReleases, function(releaseName){
      $scope.getReleaseData(releaseName);
    });
  };
  $scope.removeReleaseFromList = function(releaseName){
    $scope.shortInfoReleases = _.without($scope.shortInfoReleases, releaseName);
    $location.search('selected', $scope.shortInfoReleases.join(","))
    $scope.shortInfo = _.filter($scope.shortInfo, function(elem){
    return elem["RELEASE_NAME"] != releaseName;});
  };
  $scope.showSubCategory = function(category){
    if ($scope.menus[category].showSubCat){
      $scope.menus[category].showSubCat=false;
    }else{
      $scope.menus[category].showSubCat=true;
    }
  };
  $scope.showTable = function(category, subcategory){
    if ($scope.menus[category].subcats[subcategory].show){
      $scope.menus[category].subcats[subcategory].show = false;
    }else{
      $scope.menus[category].subcats[subcategory].show = true;
    }
  };
  $scope.showAllSubMenus = function(subCat){
    if ($scope.menus[subCat].showSubCat){
      var close_sub_menus = false;
      _.each($scope.menus[subCat]["subcats"], function(element){
        if(element.show){
          close_sub_menus = true;
        }else{
        close_sub_menus = false;
        }
      });
      if(close_sub_menus){
        $scope.menus[subCat].showSubCat = false;
        _.each($scope.menus[subCat]["subcats"], function(element){
          element.show = false;
        });
      }else{
        $scope.menus[subCat].showSubCat = true;
        _.each($scope.menus[subCat]["subcats"], function(element){
          element.show = true;
        });
      }
    }else{
      $scope.menus[subCat].showSubCat = true;
      _.each($scope.menus[subCat]["subcats"], function(element){
        element.show = true;
      });
    }
  };
  $scope.showAllMenus = function(){
    $scope.showAllSubMenus("Reconstruction");
    $scope.showAllSubMenus("HLT");
    $scope.showAllSubMenus("PAGs");
    $scope.showAllSubMenus("IN");
    $scope.showAllSubMenus("GEN");
  };
  $scope.openAddReleaseModal = function(){
    $scope.addReleaseModal = true;
  };
  $scope.getUserList = function(){
    $scope.searchUserModal = true;
  };
  $scope.openRemoveUser = function(){
    $scope.removeUserModal = true;
  };
  $scope.openAddUser = function(){
    $scope.addUserModal = true;
  };
  $scope.changeSort = function()
  {
    if ($scope.sort_ascending == true)
    {
      $scope.sort_ascending = false;
    }else
    {
      $scope.sort_ascending = true;
    }
  };

  //watch length of pending HTTP requests -> if there are display loading;
  $scope.$watch(function(){ return $http.pendingRequests.length;}, function(v){
    if (v == 0){  //if HTTP requests pending == 0
      $scope.pendingRequests = false;
    }else
      $scope.pendingRequests = true;
  });
  $scope.$watch("searchableName",function(v){
    if(v){
      $location.search("srch",v);
    }
  });
  $scope.$watch("menus", function(v){
    _.each($scope.menus, function(single_menu){
      if(single_menu.showSubCat){
        $location.search(single_menu.name,'true');
      }else{
        $location.search(single_menu.name,null);
      }
      _.each(single_menu.subcats, function(subcat){
        if (subcat.show){
          $location.search(""+single_menu.name[0]+subcat.name.substring(0,4)+"",'true');
        }else{
          $location.search(""+single_menu.name[0]+subcat.name.substring(0,4)+"",null);
        }
      });
    });
  },true);

  if ($location.search()['srch']){
    $scope.searchableName = $location.search()['srch'];
    $scope.getReleaseList();
   }else{
    $scope.searchableName = "";
  }
  if ($location.search()['selected']){
    $scope.shortInfoReleases = $location.search()['selected'].split(',');
    _.each($scope.shortInfoReleases, function(release){
      $scope.getReleaseData(release);
    });
   }else{
    $scope.shortInfoReleases = [];
  }
  if($location.search()['Reconstruction']){
    $scope.menus['Reconstruction']['showSubCat'] = true;
  }
  if($location.search()['HLT']){
    $scope.menus['HLT']['showSubCat'] = true;
  }
  if($location.search()['PAGs']){
    $scope.menus['PAGs']['showSubCat'] = true;
  }
  if($location.search()['IN']){
    $scope.menus['IN']['showSubCat'] = true;
  }
  if($location.search()['GEN']){
    $scope.menus['GEN']['showSubCat'] = true;
  }
  if($location.search()['RData']){
    $scope.menus['Reconstruction']['showSubCat'] = true;
    $scope.menus['Reconstruction']['subcats']['Data']['show']=true;
  }
  if($location.search()['RFull']){
    $scope.menus['Reconstruction']['showSubCat'] = true;
    $scope.menus['Reconstruction']['subcats']['FullSim']['show']=true;
  }
  if($location.search()['RFast']){
    $scope.menus['Reconstruction']['showSubCat'] = true;
    $scope.menus['Reconstruction']['subcats']['FastSim']['show']=true;
  }
  if($location.search()['HData']){
    $scope.menus['HLT']['showSubCat'] = true;
    $scope.menus['HLT']['subcats']['Data']['show']=true;
  }
  if($location.search()['HFull']){
    $scope.menus['HLT']['showSubCat'] = true;
    $scope.menus['HLT']['subcats']['FullSim']['show']=true;
  }
  if($location.search()['PData']){
    $scope.menus['PAGs']['showSubCat'] = true;
    $scope.menus['PAGs']['subcats']['Data']['show']=true;
  }
  if($location.search()['PFull']){
    $scope.menus['PAGs']['showSubCat'] = true;
    $scope.menus['PAGs']['subcats']['FullSim']['show']=true;
  }
  if($location.search()['PFast']){
    $scope.menus['PAGs']['showSubCat'] = true;
    $scope.menus['PAGs']['subcats']['FastSim']['show']=true;
  }
  if($location.search()['IData']){
    $scope.menus['IN']['showSubCat'] = true;
    $scope.menus['IN']['subcats']['Data']['show']=true;
  }
  if($location.search()['IFull']){
    $scope.menus['IN']['showSubCat'] = true;
    $scope.menus['IN']['subcats']['FullSim']['show']=true;
  }
  if($location.search()['IFast']){
    $scope.menus['IN']['showSubCat'] = true;
    $scope.menus['IN']['subcats']['FastSim']['show']=true;
  }
  if($location.search()['GGen']){
    $scope.menus['GEN']['showSubCat'] = true;
    $scope.menus['GEN']['subcats']['Gen']['show']=true;
  }
};


function ModalCtrl($scope, $http) {
  $scope.openDetailModal = function(release, cat, subCat, col, col_name, col_db_name){
    $scope.catSubCat = cat+"/"+subCat;
    $scope.validation_column = col_db_name;
    $scope.validation_column_name = col_name;
    $http({method:'POST', url:'FullDetails',data:{release: release, category:cat, subCategory:subCat, column:col}}).
      success(function(data,status){
        $scope.details = data;
          $scope.shouldBeOpen = true;
          $scope.selected_version = _.last($scope.details['VERSIONS']);
          $scope.latest_version = _.last($scope.details['VERSIONS']);
          if ( !$scope.latest_version ){
            $scope.latest_version = 0;
          }
          if ( !$scope.details[$scope.latest_version] ){ //if details are undefined -> create and empty dictionary
            $scope.details[$scope.latest_version] = {};
          } 
        }).error(function(data,status){
            alert("Error: " + status);
        });
  };
  $scope.open = function () {
    $scope.shouldBeOpen = true;
  };
  $scope.close = function () {
    $scope.shouldBeOpen = false;
  };
  $scope.checkUserName = function(cat, subCat){
    var local_subcat = $scope.catSubCat.split('/')[0];
     if (local_subcat == 'HLT'){
       $scope.hn_address = 'hn-cms-trigger-performance@cern.ch';
     }else if( (local_subcat=='Reconstruction') && ($scope.validation_column_name.toUpperCase() == 'MUON') ){
       $scope.hn_address = 'hn-cms-muon-object-validation@cern.ch';
     }else if($scope.validation_column_name.toUpperCase() == 'INFO'){
       $scope.hn_address = "";
     }else{
      $scope.hn_address = 'hn-cms-relval@cern.ch';
     };
    //Validators script

      $http({method:'POST', url:'checkValidatorsRights', data:{cat:cat, subCategory:subCat, statusKind:$scope.validation_column}})
      .success(function(data,status){
        if (data[0] == true){
          $http({method:'GET', url:'getLogedUserName'}).
            success(function(data,status){
              $scope.user_name = data[0];
              $scope.user_fullname = data[1];
            }).error(function(status){
              alert("Error: " + status);
            });
          $scope.editableModal = true;
          $scope.close();
        }else{
          alert("Error: You don't have permission to edit this field");
          $scope.editableModal = false;
          //alert("Error: You don't have permission to edit this field");
        }
      }).error(function(status){
        alert("Error: " + status);
      });
//    $scope.editableModal = true; //admin
//    $scope.close();  //admin
  };
  $scope.closeEditable = function(){
    $scope.editableModal = false;
  };
  $scope.selectVersion = function(version){
    $scope.selected_version = version;
  };
}


app.directive("editModal", function($http){
  return{
  restrict: 'E',
  replace: true,
  template:'<div modal="editableModal" close="closeEditable()" style="display: block;max-height:500px;">'+
      '  <div class="modal-header">'+
      '    <h2> Validation campaign: <text type="text">{{details[\'RELEASE_NAME\']}}</text></h2>'+
      '    <h4> <text> {{catSubCat}}</text></h4>'+
      '    <h3> Author: <text type="text">{{user_fullname}}</text></h3>'+
      '  </div>  <!--end of modal header-->'+
      '  <div class="modal-body">'+
      '    <h4>{{validation_column_name | uppercase}} Validation status: </h4>'+
      '    <select  ng-model="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\']">'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'NOT YET DONE\'" value="NOT YET DONE">NOT YET DONE</option>'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'OK\'" value="OK">OK</option>'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'FAILURE\'" value="FAILURE">FAILURE</option>'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'CHANGES EXPECTED\'" value="CHANGES EXPECTED">CHANGES EXPECTED</option>'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'IN PROGRESS\'" value="IN PROGRESS">IN PROGRESS</option>'+
      '      <option ng-selected="details[\'\'+latest_version+\'\'][\'VALIDATION_STATUS\'] == \'KNOWN ISSUE\'" value="KNOWN ISSUE">KNOWN ISSUE</option>'+
      '    </select>'+
      '    <p>Comments:</p>'+
      '      <div>'+
      '        <textarea  ng-model="details[\'\'+latest_version+\'\'][\'COMMENTS\']" maxlength="3500" style="width: 454px; height:129px;" >{{details[\'\'+latest_version+\'\'][\'COMMENTS\']}}</textarea>'+
      '      </div>'+
      '      {{details[\'\'+latest_version+\'\'][\'COMMENTS\'].length}}/3500'+
      '    <p>Links:</p>'+
      '      <div>'+
      '        <textarea  ng-model="details[\'\'+latest_version+\'\'][\'LINKS\']" maxlength="3500" style="width: 362px; height:60px;">{{details[\'\'+latest_version+\'\'][\'LINKS\']}}</textarea>'+
      '      </div>'+
      '      {{details[\'\'+latest_version+\'\'][\'LINKS\'].length}}/3500'+
      '  </div> <!--end of modal body-->'+
      '  <div class="modal-footer">'+
      '    <div ng-show="hn_address != \'\'">This message will be sent to: {{hn_address}}</div>'+
      '    <img ng-show="pendingUpdate" ng-src="https://twiki.cern.ch/twiki/pub/TWiki/TWikiDocGraphics/processing-bg.gif"/>'+
      '    <button class="btn" ng-click="updateValidation(details)" ng-disabled="pendingUpdate">Save Information</button>'+
      '    <button class="btn btn-primary" ng-click="closeEditable()">Close</button>'+
      '  </div>'+
      '</div>',
  link: function (scope, element, attr){
    scope.hn_address = ""
    scope.release_name = scope.$eval(attr.release);
    scope.column_name = scope.$eval(attr.catSubCat);
    //scope.new_status = scope.details['VALIDATION_STATUS'];
    scope.updateValidation = function(to_be_updated){
      // default values in-case for previously not added report columns it's null
      var data_to_send = {};

        data_to_send["comentAuthor"] = scope.user_fullname;
        data_to_send["stateValue"] = scope.details[''+scope.latest_version+'']['VALIDATION_STATUS'];
        data_to_send["relName"] = scope.details['RELEASE_NAME'];
        data_to_send["newComment"] = scope.details[''+scope.latest_version+'']['COMMENTS'];
        data_to_send["newLinks"] = scope.details[''+scope.latest_version+'']['LINKS'];
        data_to_send["catSubCat"] = scope.catSubCat[0]+scope.catSubCat.split('/')[1].substring(0,4);
        data_to_send["statusKind"] = scope.validation_column.toUpperCase();
        data_to_send["userName"] = scope.user_name;
        scope.pendingUpdate = true

      // we convert all undefined values to null
      // so they wont be deleted by stringify method
      $http({method:'POST', url:'updateReleaseInfo', data:
        JSON.stringify(data_to_send, function(k, v) { if (v === undefined) { return null; } return v; })}
      ).success(function(data,status){
          scope.pendingUpdate = false;
          alert(data);
          scope.closeEditable();
          scope.getReleaseData(scope.details['RELEASE_NAME']);
        }).error(function(status){
          scope.pendingUpdate = false;
          alert("Error: " + status);
          scope.closeEditable();
        });
    };
    }
  }
});

app.filter('newlines', function(){
  return function(text){
    if(text){
      var text_to = text.replace(/\n/g, '<br/>');
      return text_to.replace(/ /g,'&nbsp;');
    }
  }
});
app.filter('linkify', function(){
  return function(text){
    if(text){
    var replaceText, replacePattern1, replacePattern2;

    //URLs starting with http://, https://, or ftp://
    replacePattern1 = /(\b(https?|ftp):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/gim;
    replaceText = text.replace(replacePattern1, '<a href="$1" target="_blank">$1</a>');

    //URLs starting with "www." (without // before it, or it'd re-link the ones done above).
    replacePattern2 = /(^|[^\/])(www\.[\S]+(\b|$))/gim;
    replacedText = replaceText.replace(replacePattern2, '$1<a href="http://$2" target="_blank">$2</a>');
    return replacedText.replace(/\n/g,"<br>")  //return formatted links with new line to <br> as HTML <P> tag skips '\n'
    }
  }
});
