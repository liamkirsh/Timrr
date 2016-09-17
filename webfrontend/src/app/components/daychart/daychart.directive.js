'use strict';

angular.module('inspinia')
  .directive('daychart', function ($window) {
    return {
      link: link,
      restrict: 'E',
      scope: {
        blocks: '='
      },
      templateUrl: 'app/components/daychart/daychart.html',
      controller:
        function (
          $scope
        ) {

          var blockList = [];
          angular.forEach($scope.blocks, function(value, key) {
            var width = (new Date(value.to) - new Date(value.from)) / (24*60*60*1000) * 1170; //$scope.daychartWidth;
            console.log(new Date(value.from));
            console.log(Math.floor(new Date(value.from) / (24*60*60*1000)));
            var startOfDay = Math.floor(new Date(value.from) / (24*60*60*1000)) * (24*60*60*1000);
            console.log(startOfDay);
            var left = (new Date(value.from) - startOfDay) / (24*60*60*1000) * 1170;
            this.push({
              width: width,
              left: left,
              type: value.type,
              name: value.name
            });
          }, blockList);
          $scope.blockList = blockList;

          // change product view and get voucher codes
          $scope.editProduct = function (product) {
            if (product === 'all') {
              $scope.currentProduct = {
                'allProducts': true
              };
            } else {
              $scope.currentProduct = product;
              ProductService.getVoucherCodes(product.id).then(function (response) {
                $scope.currentVoucherCodes = response;
              });
            }
          };

        }
    };

    function link(scope, element, attrs) {
            scope.width = $window.innerWidth;

            function getWidth() {
              return element.context.firstChild.offsetWidth;
            }
            function onResize() {
                // uncomment for only fire when $window.innerWidth change   
                if (scope.width !== $window.innerWidth)
                {
                    scope.daychartWidth = getWidth();
                    scope.width = $window.innerWidth;
                    scope.$digest();
                }
            };

            function cleanUp() {
                angular.element($window).off('resize', onResize);
            }

            scope.daychartWidth = getWidth();
            angular.element($window).on('resize', onResize);
            scope.$on('$destroy', cleanUp);

    }
  }); 
