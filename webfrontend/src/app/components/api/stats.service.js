(function (module) {
  'use strict';

  module.factory('TimrrAPI', function ($http, $q) {

    var vm = {
      getDailyStats: getDailyStats
    };

    init();

    return vm;

    function init () {
      vm.server = 'http://172.31.3.62:5000';
    }
    
    function getDailyStats(date) {
      return $http.get(vm.server + '/workperiods?delta=-1');
    }

  });

}(angular.module('inspinia')));
