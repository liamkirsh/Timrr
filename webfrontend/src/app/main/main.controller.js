'use strict';

angular.module('inspinia')
  .controller('MainController', function () {

    var vm = this;

    vm.userName = 'Swiggity Swooty';
    vm.helloText = 'Welcome in INSPINIA Gulp SeedProject';
    vm.descriptionText = 'It is an application skeleton for a typical AngularJS web app. You can use it to quickly bootstrap your angular webapp projects.';

    vm.blocks = [{
	    	from: '2016-09-17T00:25:43.000Z',
	    	to: '2016-09-17T00:49:00.000Z',
	    	type: 'productive',
	    	name: 'Optional'
    	},
    	{
    		from: '2016-09-17T00:55:00.000Z',
	    	to: '2016-09-17T00:59:00.000Z',
	    	type: 'undecided',
	    	name: 'Optional'
    	},
    	{
    		from: '2016-09-17T00:59:00.000Z',
	    	to: '2016-09-17T02:13:00.000Z',
	    	type: 'productive',
	    	name: 'Optional'
    	}
    ];

  });
