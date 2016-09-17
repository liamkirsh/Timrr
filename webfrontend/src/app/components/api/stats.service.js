(function (module) {
  'use strict';

  module.factory('TimrrAPI', function ($http, $q) {

    var vm = {
      getDailyStats: getDailyStats
    };

    init();

    return vm;

    function init () {
      vm.server = 'http://localhost:5000';
    }
    
    function getDailyStats(date) {
      return $http.get(vm.server + '/stats?date=' + date);
    }

  });

}(angular.module('inspinia')));
